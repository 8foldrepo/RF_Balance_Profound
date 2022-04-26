from PyQt5.QtCore import pyqtSignal
from abc import abstractmethod
from Hardware.Abstract.abstract_device import AbstractDevice
from Utilities.useful_methods import log_msg


class SimulatedDevice(AbstractDevice):
    connected_signal = pyqtSignal(bool)

    def __init__(self, config, device_key, parent=None):
        super().__init__(parent=parent, device_key=device_key, config=config)

    @abstractmethod
    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ''

    @abstractmethod
    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def wrap_up(self):
        self.disconnect_hardware()

    def log(self, message, level='info'):
        log_msg(self, self.root_logger, message=message, level=level)
