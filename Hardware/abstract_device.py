from abc import ABC, abstractmethod
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

class AbstractDevice(QObject):
    connected_signal = pyqtSignal(bool)
    dummy_command_signal = pyqtSignal(str)

    def __init__(self, config, device_key, parent = None):
        super().__init__(parent=parent)
        self.config = config
        self.device_key = device_key
        pass

    @abstractmethod
    def fields_setup(self):
        pass

    @abstractmethod
    def connect_hardware(self):
        self.connected_signal.emit(True)

    @abstractmethod
    def disconnect_hardware(self):
        self.connected_signal.emit(False)