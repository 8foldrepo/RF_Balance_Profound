import serial
from PyQt5.QtCore import pyqtSignal

from Utilities.load_config import load_configuration
from Hardware.Simulated.simulated_relay import SimulatedRelay
import time as t
from PyQt5.QtCore import pyqtSignal


class Relay_Board(SimulatedRelay):
    reading_signal = pyqtSignal(bool)

    def __init__(self, config = None, device_key = 'Pump', parent = None):
        super().__init__(config=config,device_key=device_key, parent = None)
        self.ser = None
        self.fields_setup()
        self.on = False

    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.on_by_default = self.config[self.device_key]['on_by_default']
        self.port = self.config[self.device_key]['port']

    def connect_hardware(self):
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
        except serial.serialutil.SerialException:
            self.connected = False
            self.log( level='error', message=
            f"{self.device_key} not connected. Check that it is plugged in and look at Device manager "
            "to determine which COM port to use. It is currently hard coded")
        self.connected_signal.emit(self.connected)
        self.relay_write(self.on_by_default)

    def disconnect_hardware(self):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return

        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return

        self.ser.write(b"\xFF\x01\x03\n") #Check state command

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            reply = self.ser.readline()
            if reply == b'\xff\x01\x01': #On reply
                self.on = True
                self.log(f"{self.device_key} is ON")
                self.reading_signal.emit(True)
                return True
            elif reply == b'\xff\x01\x00': #Off reply
                self.on = False
                self.log(f"{self.device_key} is OFF")
                self.reading_signal.emit(False)
                return False
        return False

    def relay_write(self, on: bool):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return

        if on:
            self.ser.write(b"\xFF\x01\x01\n") #On command
            self.get_reading()
        else:
            self.ser.write(b"\xFF\x01\x00\n") #Off command
            self.get_reading()

        #self.on = on


if __name__ == '__main__':
    switch = Relay_Board()
    switch.connect_hardware()
    switch.relay_write(True)

