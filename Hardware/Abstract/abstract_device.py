from abc import abstractmethod, ABCMeta
from typing import Tuple

from PyQt5.QtCore import pyqtSignal, QObject

from Utilities.useful_methods import log_msg


class AbstractDevice(QObject):
    """
    This base device class gives all devices access to signals and slots, the ability to log, and connect/disconnect
    hardware methods.
    """

    __metaclass__ = ABCMeta

    connected_signal = pyqtSignal(bool)
    connected: bool

    def __init__(self, config, device_key, parent=None):
        """Load config if one was not given and set up the logger"""
        super().__init__(parent=parent)
        from Utilities.load_config import (
            ROOT_LOGGER_NAME,
            LOGGER_FORMAT,
            load_configuration,
        )
        import logging
        import os
        from definitions import ROOT_DIR

        log_formatter = logging.Formatter(LOGGER_FORMAT)
        balance_logger = logging.getLogger("wtf_log")
        file_handler = logging.FileHandler(
            os.path.join(ROOT_DIR, "./logs/wtf.log"), mode="w"
        )
        file_handler.setFormatter(log_formatter)
        balance_logger.addHandler(file_handler)
        balance_logger.setLevel(logging.INFO)
        self.root_logger = logging.getLogger(ROOT_LOGGER_NAME)
        if config is not None:
            self.config = config
        else:
            self.config = load_configuration()
        self.device_key = device_key
        self.connected = False

    @abstractmethod
    def connect_hardware(self) -> Tuple[bool, str]:
        """
        Establish a connection and emit the connected signal (should emit and return True if successful)
        Also provides feedback in the form of text
        """
        ...

    @abstractmethod
    def disconnect_hardware(self):
        """Disconnect and emit the connected signal (should emit False if successful)"""
        ...

    @abstractmethod
    def get_serial_number(self) -> str:
        """Retrieves info for the systeminfo.ini file."""
        ...

    @abstractmethod
    def wrap_up(self):
        """Safely stop or turn off hardware and disconnect"""
        self.disconnect_hardware()

    def log(self, message, level="info"):
        """Log a message to the WTF.log file (the hardware log)"""
        log_msg(self, self.root_logger, message=message, level=level)


# Script/example code for testing
if __name__ == "__main__":
    pass
