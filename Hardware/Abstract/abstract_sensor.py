from abc import abstractmethod, ABC
from PyQt5.QtCore import pyqtSignal
from Hardware.Abstract.abstract_device import AbstractDevice

'''AbstractSensor adds the ability to get a reading'''


class AbstractSensor(AbstractDevice):
    reading_signal = pyqtSignal(float)

    @abstractmethod
    def __init__(self, config, parent=None, device_key=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.connected = True

    '''Get the sensor reading as a float'''

    @abstractmethod
    def get_reading(self) -> float:
        ...
