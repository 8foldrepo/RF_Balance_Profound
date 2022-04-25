import serial
from PyQt5.QtCore import pyqtSignal

from Utilities.load_config import load_configuration
from Hardware.Simulated.simulated_sensor import SimulatedSensor
import time as t
from PyQt5.QtCore import pyqtSignal
from abc import abstractmethod

class SimulatedRelay(SimulatedSensor):
    reading_signal = pyqtSignal(bool)

    def __init__(self, config = None, device_key = 'Pump', parent = None):
        super().__init__(config=config,device_key=device_key, parent = None)
        self.ser = None
        self.fields_setup()
        self.on = False

    @abstractmethod
    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()
        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.on_by_default = self.config[self.device_key]['on_by_default']
        self.port = self.config[self.device_key]['port']
        #retrieve config settings from config file

    @abstractmethod
    def connect_hardware(self):
        self.relay_write(self.on_by_default)
        self.connected_signal.emit(True)

    @abstractmethod
    def disconnect_hardware(self):
        self.connected_signal.emit(False)

    @abstractmethod
    def get_reading(self):
        return self.on

    @abstractmethod
    def relay_write(self, on: bool):
        self.on = on

if __name__ == '__main__':
    switch = SimulatedRelay()
    switch.connect()
    switch.relay_write(True)
    switch.relay_write(False)

