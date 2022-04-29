from abc import abstractmethod
from PyQt5.QtCore import pyqtSignal
from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractSensor(AbstractDevice):
    """AbstractSensor adds the ability to get a reading"""
    reading_signal = pyqtSignal(float)

    @abstractmethod
    def __init__(self, config, parent=None, device_key=None):
        super().__init__(parent=parent, config=config, device_key=device_key)

    @abstractmethod
    def get_reading(self) -> float:
        """Get the sensor reading as a float"""
        ...
