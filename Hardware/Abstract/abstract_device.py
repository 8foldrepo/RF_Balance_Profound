from PyQt5.QtCore import pyqtSignal, QObject
from abc import abstractmethod
from Utilities.useful_methods import log_msg


class AbstractDevice(QObject):
    connected_signal = pyqtSignal(bool)
    dummy_command_signal = pyqtSignal(str)

    def __init__(self, config, device_key, parent = None):
        super().__init__(parent=parent)
        from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
        import logging
        log_formatter = logging.Formatter(LOGGER_FORMAT)
        import os
        from definitions import ROOT_DIR
        balance_logger = logging.getLogger('wtf_log')
        file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
        file_handler.setFormatter(log_formatter)
        balance_logger.addHandler(file_handler)
        balance_logger.setLevel(logging.INFO)
        self.root_logger = logging.getLogger(ROOT_LOGGER_NAME)
        if config is not None:
            self.config = config
        else:
            self.config = load_configuration()
        self.device_key = device_key
        self.is_connected = False
        pass

    @abstractmethod
    def fields_setup(self):
        pass

    @abstractmethod
    def connect_hardware(self):
        self.is_connected = True
        self.connected_signal.emit(self.is_connected)

    @abstractmethod
    def disconnect_hardware(self):
        self.is_connected = False
        self.connected_signal.emit(self.is_connected)

    @abstractmethod
    def connected(self):
        return self.is_connected

    @abstractmethod
    def wrap_up(self):
        self.disconnect_hardware()

    def log(self, message, level = 'info'):
        log_msg(self,self.root_logger, message= message,level=level)