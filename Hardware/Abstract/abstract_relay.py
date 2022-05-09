from abc import abstractmethod, ABCMeta

from PyQt5.QtCore import pyqtSignal

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractRelay(AbstractDevice):
    """AbstractRelay adds relay read and write methods"""

    __metaclass__ = ABCMeta

    reading_signal = pyqtSignal(bool)
    timeout_s: float
    on_by_default: bool
    port: str

    @abstractmethod
    def __init__(self, config=None, device_key="Pump", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

    @abstractmethod
    def relay_read(self) -> bool:
        """Return the state of the relay (on/off)"""

        ...

    @abstractmethod
    def relay_write(self, on: bool):
        """Set the state of the relay (on/off)"""

        ...
