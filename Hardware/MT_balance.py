from Hardware.Abstract.abstract_sensor import AbstractSensor
import serial
from PyQt5.QtCore import pyqtSignal
import  time as t

from Utilities.useful_methods import is_number
from Utilities.load_config import load_configuration

class MT_balance(AbstractSensor):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config, device_key = "MT_Balance", parent = None):
        super().__init__(config=config, device_key=device_key, parent=parent)

        self.ser = None
        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.port = self.config[self.device_key]['port']

    """Zeroes the scale with the next stale weight reading"""
    def zero_balance(self):
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text".
        if self.ser is None or self.connected == False:
            self.log("Device is not connected")
            return
        self.log("Zeroing Balance, Please wait")
        self.ser.write(b"\nZ\n")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if item == b'Z A':
                    self.log(level='info', message='Balance Zeroed')
                    return
                else:
                    if item == b'I':
                        self.log(level='error', message='Weight unstable or balance busy')
                        return
                    elif item == b'+':
                        self.log(level='error', message='Balance overloaded')
                        return
                    elif item == b'-':
                        self.log(level='error', message='Balance underloaded')
                        return
        self.log(level='error', message=f'{self.device_key} timed out')

    #TODO: make code recognize the com port without hard coding it
    def connect_hardware(self):
        try:
            self.ser = serial.Serial(
                port=self.port,  # May vary depending on computer
                baudrate=1200,
                timeout=self.timeout_s,
                parity=serial.PARITY_ODD,
                stopbits=serial.STOPBITS_TWO,
                bytesize=serial.SEVENBITS,
            )
            self.ser.write(b"ON\r")
            self.connected = True
        except serial.serialutil.SerialException:
            self.connected = False
            self.log(level='error', message=
            f"{self.device_key} not connected. Check that it is plugged in and look at Device manager to "
            f"determine which COM port to use. It is currently hard coded")
        self.connected_signal.emit(self.connected)

    def disconnect_hardware(self):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return

        self.ser.close()
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return

        self.ser.write(b"SI\n")
        self.log("Getting weight, please wait")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if b'S D' in item:
                    chunks = item.split(b" ")
                    for chunk in chunks:
                        if is_number(chunk):
                            val = float(chunk)
                            self.log(f'Weight acquired: {val} g')
                            self.latest_weight = val
                            self.reading_signal.emit(val)
                            return
                else:
                    if item == b'I':
                        self.log(level = 'error', message='Weight unstable or balance busy')
                        return
                    elif item == b'+':
                        self.log(level = 'error', message='Balance overloaded')
                        return
                    elif item == b'-':
                        self.log(level = 'error', message='Balance underloaded')
                        return
        self.log(level='error', message=f'{self.device_key} timed out')

    def reset(self):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return

        self.ser.write(b"\n@\n")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if not item == b'':
                    self.log("Reset")
                    return
        self.log(level='error', message=f'{self.device_key} timed out')

    def get_stable_reading(self):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return
        #Command: I2 Inquiry of balance data.
        #Response: I2 A Balance data as "text".
        self.ser.write(b"\nS\n")
        self.log("Getting stable weight, please wait")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if b'S S' in item:
                    chunks = item.split(b" ")
                    for chunk in chunks:
                        if is_number(chunk):
                            val = float(chunk)
                            self.log(f'Stable weight acquired: {val} g')
                            self.latest_weight = val
                            self.reading_signal.emit(val)
                            return
                else:
                    if item == b'I':
                        self.log(level = 'error', message='Weight unstable or balance busy')
                        return
                    elif item == b'+':
                        self.log(level = 'error', message='Balance overloaded')
                        return
                    elif item == b'-':
                        self.log(level = 'error', message='Balance underloaded')
                        return
        self.log(level='error', message=f'{self.device_key} timed out')

if __name__ == '__main__':
    balance = MT_balance(config=load_configuration())
    balance.connect()
    balance.reset()
    balance.zero_balance()
    input('press enter when weight is on scale')
    balance.get_reading()
    balance.get_stable_reading()