from abc import abstractmethod
from PyQt5.QtCore import pyqtSignal
import random
from Hardware.Abstract.abstract_device import AbstractDevice

class AbstractSensor(AbstractDevice):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    @abstractmethod
    def __init__(self, config, parent=None, device_key = None):
        super().__init__(parent=parent,config=config,  device_key = device_key)
        self.connected = True

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
         noise = .1* random.random()
         signal = 23.2 + noise
         reading = round(signal,1)

         self.reading_signal.emit(reading)
         return reading