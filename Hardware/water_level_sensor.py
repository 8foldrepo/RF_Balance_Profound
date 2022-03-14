from abc import abstractmethod
from PyQt5.QtCore import pyqtSignal
import random
from Hardware.Abstract.abstract_sensor import AbstractSensor

class WaterLevelSensor(AbstractSensor):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    @abstractmethod
    def __init__(self, config, parent=None, device_key = "Water_Level_Sensor"):
        super().__init__(parent=parent,config=config,  device_key = device_key)
        self.connected = True

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
         return random.choice(['below_level', 'above_level', 'level'])