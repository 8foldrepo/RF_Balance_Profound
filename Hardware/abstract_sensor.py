from abc import abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal, QThread
import random

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)

from Utilities.useful_methods import log_msg
import os
from definitions import ROOT_DIR
balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR,"./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class AbstractSensor(QObject):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.connected = True

    @abstractmethod
    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    @abstractmethod
    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    @abstractmethod
    def get_reading(self):
         noise = .1* random.random()
         signal = 23.2 + noise
         self.reading_signal.emit(round(signal,1))