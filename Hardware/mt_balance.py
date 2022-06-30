"""
Hardware programming interface class for the Mettler Toledo Balance.
Programming/Reference Manual ~page 87
https://www.wolflabs.co.uk/document/Mettler-Toledo_Balances-Analytical_MS-S-MS-L%20Models_manual.pdf
"""

import time as t
from typing import Union, Tuple

import serial
from PyQt5 import QtCore

from Hardware.Abstract.abstract_balance import AbstractBalance
from Utilities.load_config import load_configuration
from Utilities.useful_methods import is_number


class MT_balance(AbstractBalance):
    """
    Inherits AbstractBalance from /Hardware/Abstract; reading signal connected to logger and connected signal is
    hooked up to main window balance indicator
    """
    reading_signal = QtCore.pyqtSignal(float)
    connected_signal = QtCore.pyqtSignal(bool)

    def __init__(self, config, device_key="MT_Balance", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        self.continuously_reading = False
        self.ser = None
        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    def fields_setup(self) -> None:
        """
        Load the config file if one is not provided and populates class variables therefrom
        Initializes config, timeout_s, and port variables
        """

        if self.config is None:
            self.config = load_configuration()

        self.timeout_s = self.config[self.device_key]["timeout_s"]
        self.port = self.config[self.device_key]["port"]

    def zero_balance_stable(self) -> None:
        """Zeroes the scale with the next stale weight reading"""
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if self.ser is None or self.connected is False:
            self.log(message="Device is not connected, cannot run zero_balance_stable()", level='warning')
            return
        self.log(message="Zeroing Balance, Please wait", level='info')
        self.ser.write(b"\nZ\n")

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if item == b"Z A":
                    self.log(level="info", message="Balance Zeroed")
                    return
                else:
                    if item == b'I':
                        self.log(level='error', message='Weight unstable or balance busy')
                        return
                    elif item == b"+":
                        self.log(level="error", message="Balance overloaded")
                        return
                    elif item == b"-":
                        self.log(level="error", message="Balance underloaded")
                        return
        self.log(level="error", message=f"{self.device_key} timed out")

    def wrap_up(self) -> None:
        """Runs the disconnect_hardware() method; class shutdown sequence"""
        self.disconnect_hardware()

    def zero_balance_instantly(self) -> None:
        """Zeroes (tares) the scale immediately"""

        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if self.ser is None or self.connected is False:
            self.log(message="Device is not connected, cannot run zero instantly method", level='warning')
            return
        self.log(message="Zeroing Balance", level='info')
        self.ser.write(b"\nTI\n")
        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                # For some reason when Debugging these can also appear as b'ES'. that is normal.
                if b"TI D" in item or b"TI S" in item:
                    self.log(level="info", message="Balance Zeroed")
                    t.sleep(.05)
                    return
                else:
                    if item == b'TI I':
                        self.log(level='error', message='Weight unstable or balance busy')
                        return
                    elif item == b"TI +":
                        self.log(level="error", message="Balance overloaded")
                        return
                    elif item == b"TI -":
                        self.log(level="error", message="Balance underloaded")
                        return
        self.log(level="error", message=f"{self.device_key} timed out")

    def connect_hardware(self) -> Tuple[bool, str]:
        """
        Attempts to establish a serial communication line using
        Python's serial library, also has error exception handling.

        :returns:
            boolean representing whether balance is connected, and string representing feedback is issues encountered
        """
        feedback = ""
        try:
            self.ser = serial.Serial(
                port=self.port,  # May vary depending on computer
                baudrate=1200,
                timeout=self.timeout_s,
                parity=serial.PARITY_ODD,
                stopbits=serial.STOPBITS_TWO,
                bytesize=serial.SEVENBITS,
            )
            # self.ser.write(b"ON\r")
            self.ser.write(b'@')
            self.connected = True
        except serial.serialutil.SerialException as e:
            self.connected = False
            if "Access is denied" in str(e):
                feedback = f"{self.device_key} is in use by another program, close it and restart (also check the " \
                           f"com ports in the config file): \n{e}"
            else:
                feedback = f"{self.device_key} not connected. Check that it is plugged in and look at Device manager " \
                           f"to determine which COM port to use and enter it into local.yaml: \n{e}"
        if not self.connected:
            self.log(level="error", message=feedback)
        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def disconnect_hardware(self) -> None:
        """Closes the serial connection, sets the connected flag to false and emits disconnection signal"""
        if self.ser is None:
            self.log(level="error", message=f"{self.device_key} not connected")
            return

        self.ser.close()
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self) -> Union[None, float]:
        """Sets the balance to continuous read mode and sends the immediately detected weight via signal and return"""
        if self.ser is None or not self.connected:
            self.log(level="error", message=f"{self.device_key} not connected")
            return

        if not self.continuously_reading:
            self.log("balance was not in continuous read mode, switching to it now")
            self.start_continuous_reading()
            self.continuously_reading = True

        self.ser.flushInput()

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if b"S D" in item or b"S S" in item:
                    chunks = item.split(b" ")
                    for chunk in chunks:
                        if is_number(chunk):
                            val = float(chunk)
                            self.latest_weight = val
                            self.reading_signal.emit(val)
                            if val > 1:
                                pass  # todo: remove
                            return val
                else:
                    if item == b'I':
                        self.log(level='error', message='Weight unstable or balance busy')
                        return
                    elif item == b"+":
                        self.log(level="error", message="Balance overloaded")
                        return
                    elif item == b"-":
                        self.log(level="error", message="Balance underloaded")
                        return
        self.log(level="error", message=f"{self.device_key} timed out")

    def reset(self) -> None:
        """Sends the MT pre-defined reset command to the balance, has error exception handling"""
        if self.ser is None:
            self.log(level="error", message=f"{self.device_key} not connected")
            return

        self.ser.write(b"\n@\n")

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if item != b"":
                    self.log(message="Reset", level='info')
                    return
        self.log(level="error", message=f"{self.device_key} timed out")

    def get_stable_reading(self) -> Union[float, None]:
        """
        Sends the MT pre-defined stable reading command and returns
        the weight once ready via signal and return statements

        :returns: latest stable weight as a float, or none if capture was unsuccessful
        """
        if self.ser is None:
            self.log(level="error", message=f"{self.device_key} not connected")
            return
        self.ser.write(b"\nS\n")
        self.continuously_reading = False
        self.log("Getting stable reading, please wait")

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if b"S S" in item:
                    chunks = item.split(b" ")
                    for chunk in chunks:
                        if is_number(chunk):
                            val = float(chunk)
                            self.log(f"Stable weight acquired: {val} g")
                            self.latest_weight = val
                            self.reading_signal.emit(val)
                            return self.latest_weight
                else:
                    if item == b'I':
                        self.log(level='error', message='Weight unstable or balance busy')
                        return
                    elif item == b"+":
                        self.log(level="error", message="Balance overloaded")
                        return
                    elif item == b"-":
                        self.log(level="error", message="Balance underloaded")
                        return
        self.log(level="error", message=f"{self.device_key} timed out")

    def get_serial_number(self) -> Union[str, None]:
        """
        Sends the MT pre-defined get serial number command, decodes
        the response to utf-8 and returns value, has error handling

        :returns: serial number as a string, or none if retrieval was unsuccessful
        """
        if not self.connected:
            return None

        self.stop_continuous_reading()

        self.ser.write(b"\nI4\n")

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:

                if b"I4" in item:
                    chunks = item.split(b" ")
                    for chunk in chunks:
                        if len(chunk) > 6:
                            return chunk.decode("utf-8")

                else:
                    if item == b'I':
                        self.log(level='error', message='Weight unstable or balance busy')
                        return None
                    elif item == b"+":
                        self.log(level="error", message="Balance overloaded")
                        return None
                    elif item == b"-":
                        self.log(level="error", message="Balance underloaded")
                        return None
        self.log(level="error", message=f"{self.device_key} timed out")

    def start_continuous_reading(self) -> None:
        """Sends the continuous reading command to the balance, and sets the continuous reading flag to false"""
        self.ser.write(b"\nSIR\n")
        self.continuously_reading = True

    def stop_continuous_reading(self) -> None:
        """Sends the stop continuous reading command to the balance, and sets the continuous reading flag to false"""
        self.ser.write(b"\n@\n")
        self.continuously_reading = False


if __name__ == "__main__":
    import unittest

    unittest.main()
