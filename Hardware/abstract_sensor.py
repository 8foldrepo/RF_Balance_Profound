from abc import abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal, QThread
import random

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)
sensor_logger = logging.getLogger('sensor_log')
file_handler = logging.FileHandler("./logs/sensor.log", mode='w')
file_handler.setFormatter(log_formatter)
sensor_logger.addHandler(file_handler)
sensor_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class AbstractSensor(QObject):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.connected = True

    @abstractmethod
    def connect(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    @abstractmethod
    def disconnect_sensor(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    @abstractmethod
    def get_reading(self):
         noise = .1* random.random()
         signal = 23.2 + noise
         self.reading_signal.emit(round(signal,1))

    def log_msg(self, level: str, message: str) -> None:
        """
        Convenience function to log messages in a compact way with useful info.

            Parameters:
                level (str): A string indicating the logger level, can be either
                'info', 'debug' or 'error'
                message (str): A string that contains the message to be logged

            Returns:
                None
        """
        thread_name = QThread.currentThread().objectName()
        log_entry = f"[{type(self).__name__}] [{thread_name}] : {message}"
        if level == 'debug':
            root_logger.debug(log_entry)
            sensor_logger.debug(log_entry)
        elif level == 'error':
            root_logger.error(log_entry)
            sensor_logger.error(log_entry)
        elif level == 'warning':
            root_logger.warning(log_entry)
            sensor_logger.warning(log_entry)
        else:
            root_logger.info(log_entry)
            sensor_logger.info(log_entry)