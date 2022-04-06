import random
from abc import  abstractmethod
from Hardware.Abstract.abstract_sensor import AbstractSensor
import serial
from PyQt5.QtCore import pyqtSignal
import  time as t

from Utilities.useful_methods import is_number
from Utilities.load_config import load_configuration

class AbstractBalance(AbstractSensor):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config, device_key = "MT_Balance", parent = None):
        super().__init__(config=config, device_key=device_key, parent=parent)

        self.ser = None
        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    @abstractmethod
    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.port = self.config[self.device_key]['port']

    """Zeroes the scale with the next stale weight reading"""
    @abstractmethod
    def zero_balance_stable(self):
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if self.ser is None or self.connected == False:
            self.log("Device is not connected")
            return
        self.log("Zeroing Balance, Please wait")
        self.ser.write(b"\nZ\n")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            item  = random.choice([b"ZA", b"I"])

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

    """Zeroes the scale with the next stale weight reading"""

    @abstractmethod
    def zero_balance_instantly(self):
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if self.ser is None or self.connected == False:
            self.log("Device is not connected")
            return
        self.log("Zeroing Balance, Please wait")
        self.ser.write(b"\nZ\n")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            item = random.choice([b"Z S", b"Z D", b"Z I"])

            if item == b'Z S' or b'Z D':
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

    @abstractmethod
    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    @abstractmethod
    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    @abstractmethod
    def get_reading(self):
        self.log("Getting weight, please wait")

        item = random.choice([b'S D', b'I'])
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
        self.log("Reset")

    @abstractmethod
    def get_stable_reading(self):
        self.log("Getting stable weight, please wait")
        item = random.choice([b"S S", b"I"])

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

if __name__ == '__main__':
    balance = AbstractBalance(config=load_configuration())
    balance.connect_hardware()
    balance.reset()
    balance.zero_balance()
    input('press enter when weight is on scale')
    balance.get_reading()
    balance.get_stable_reading()