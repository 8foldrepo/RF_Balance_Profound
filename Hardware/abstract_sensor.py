from PyQt5.QtCore import QObject, pyqtSignal
import random

class AbstractSensor(QObject):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.connected = True

    def connect(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    def disconnect_sensor(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
         noise = .1* random.random()
         signal = 23.2 + noise
         self.reading_signal.emit(round(signal,1))
