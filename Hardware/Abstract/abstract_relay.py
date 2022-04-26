from abc import abstractmethod, ABC, ABCMeta
from PyQt5.QtCore import pyqtSignal
from Hardware.Abstract.abstract_device import AbstractDevice

'''AbstractRelay adds relay read and write methods'''


class AbstractRelay(AbstractDevice):
    __metaclass__ = ABCMeta

    reading_signal = pyqtSignal(bool)
    timeout_s: float
    on_by_default: bool
    port: str

    '''Always call super().__init__ in subclasses'''

    @abstractmethod
    def __init__(self, config=None, device_key='Pump', parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

    '''Return the state of the relay (on/off)'''

    @abstractmethod
    def relay_read(self, on: bool) -> bool:
        ...

    '''Set the state of the relay (on/off)'''

    @abstractmethod
    def relay_write(self, on: bool):
        ...
