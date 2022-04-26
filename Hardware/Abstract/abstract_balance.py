from abc import abstractmethod, ABCMeta
from Hardware.Abstract.abstract_sensor import AbstractSensor
from PyQt5.QtCore import pyqtSignal


class AbstractBalance(AbstractSensor):
    __metaclass__ = ABCMeta

    timeout_s: int
    port: str

    def __init__(self, config, device_key="MT_Balance", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    @abstractmethod
    def fields_setup(self):
        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.port = self.config[self.device_key]['port']

    """Zeroes the scale with the next stale weight reading"""

    @abstractmethod
    def zero_balance_stable(self):
        ...

    """Zeroes the scale with the next stale weight reading"""

    @abstractmethod
    def zero_balance_instantly(self):
        ...

    @abstractmethod
    def get_stable_reading(self):
        ...
