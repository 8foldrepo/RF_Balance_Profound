import time as t
from typing import Tuple, Union
import serial
from PyQt5 import QtCore
from Hardware.Abstract.abstract_relay import AbstractRelay
from Utilities.load_config import load_configuration


class RelayBoard(AbstractRelay):
    """A class for interfacing with the relay in the power module box which provides power to the RF power switcher"""

    reading_signal = QtCore.pyqtSignal(bool)

    def __init__(self, config=None, device_key="Daq_Power_Relay", parent=None):
        super().__init__(config=config, device_key=device_key, parent=None)
        self.ser = None
        self.fields_setup()
        self.on = False

    def fields_setup(self) -> None:
        """Initializes config, timeout_s, on_by_default, and port variables (latter 3 come from config)"""
        if self.config is None:
            self.config = load_configuration()

        self.timeout_s = self.config[self.device_key]["timeout_s"]
        self.on_by_default = self.config[self.device_key]["on_by_default"]
        self.port = self.config[self.device_key]["port"]

    def connect_hardware(self) -> Tuple[bool, str]:
        """
        Attempts to make serial communication, sends the on command,
        updates flags and returns connected boolean and feedback
        """
        feedback = ""
        try:
            self.ser = serial.Serial(
                port=self.port,  # May vary depending on computer
                baudrate=9600,
                timeout=self.timeout_s,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
            )
            self.ser.write(b"ON\r")
            self.connected = True
            self.log(f"{self.device_key} connected successfully")
            self.relay_write(self.on_by_default)
        except serial.serialutil.SerialException:
            self.connected = False
            feedback = f"{self.device_key} not connected. Check that it is plugged in and look at Device manager " \
                       f"to determine which COM port to use. Make sure it matches the config file"
            self.log(level='error', message=feedback)

        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def disconnect_hardware(self) -> None:
        """Sets connected flag to false and emits it if serial variable is not none"""
        if self.ser is None:
            self.log(level="error", message=f"{self.device_key} not connected")
            return

        self.connected = False
        self.connected_signal.emit(self.connected)

    def relay_read(self) -> Union[bool, None]:
        """Returns whether relay board is on or off"""
        if self.ser is None:
            self.log(level="error", message=f"{self.device_key} not connected")
            return

        self.ser.write(b"\xFF\x01\x03\n")  # Check state command

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            reply = self.ser.readline()
            if reply == b"\xff\x01\x01":  # On reply
                self.on = True
                self.log(f"{self.device_key} is ON")
                self.reading_signal.emit(True)
                return True
            elif reply == b"\xff\x01\x00":  # Off reply
                self.on = False
                self.log(f"{self.device_key} is OFF")
                self.reading_signal.emit(False)
                return False
        return False

    def relay_write(self, on: bool) -> None:
        """Writes on or off command depending on passed boolean value"""
        if self.ser is None:
            self.log(level="error", message=f"{self.device_key} not connected")
            return

        if on:
            self.ser.write(b"\xFF\x01\x01\n")  # On command
            self.relay_read()
        else:
            self.ser.write(b"\xFF\x01\x00\n")  # Off command
            self.relay_read()

    def wrap_up(self) -> None:
        """Calls the relay_write method with false parameter and calls disconnect_hardware method"""
        self.relay_write(False)
        self.disconnect_hardware()

    def get_serial_number(self) -> str:
        # stretch: implement
        return ""


if __name__ == "__main__":
    switch = RelayBoard()
    switch.connect_hardware()
    switch.relay_write(False)
    t.sleep(1)
    switch.relay_write(True)
    print(switch.relay_read())
