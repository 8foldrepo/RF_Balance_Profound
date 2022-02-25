from Hardware.abstract_sensor import AbstractSensor
from abc import abstractmethod
import serial
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import random

from Utilities.useful_methods import is_number

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)
balance_logger = logging.getLogger('balance_log')
file_handler = logging.FileHandler("./logs/balance.log", mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class MT_balance(QObject):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()



        self.latest_weight = -1
        self.tare_weight = -1

        self.config = config
        self.connected = True

    """Zeroes the scale with the next stale weight reading"""
    def tare_balance(self):
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text".
        self.ser.write(b"T\r")
        while True:
            y = self.ser.readline().split(b" ")
            for item in y:
                if is_number(item):
                    self.tare_weight = float(item)
                    break
                else:
                    if item == b'I':
                        self.log_msg(level='error', message='Weight unstable or balance busy')
                        break
                    elif item == b'+':
                        self.log_msg(level='error', message='Balance overloaded')
                        break
                    elif item == b'-':
                        self.log_msg(level='error', message='Balance underloaded')
                        break

    def connect(self):
        try:
            self.ser = serial.Serial(
                port="COM3",  # May vary depending on computer
                baudrate=9600,
                timeout=1,
                parity=serial.PARITY_ODD,
                stopbits=serial.STOPBITS_TWO,
                bytesize=serial.SEVENBITS,
            )
            self.ser.write(b"ON\r")
            self.connected = True
        except serial.serialutil.SerialException:
            self.connected = False
            self.log_msg(level='info', message=
            "Radiation force balance not connected. Check that it is plugged in and look at Device manager to determine which COM port to use. It is currently hard coded"
                         )
        self.connected_signal.emit(self.connected)
    def disconnect_sensor(self):
        self.ser.close()
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text".
        self.ser.write(b"S\r")
        while True:
            y = self.ser.readline().split(b" ")
            for item in y:
                if is_number(item):
                    self.latest_weight = float(item)
                    break
                else:
                    if item == b'I':
                        self.log_msg(level='error', message='Weight unstable or balance busy')
                        break
                    elif item == b'+':
                        self.log_msg(level='error', message='Balance overloaded')
                        break
                    elif item == b'-':
                        self.log_msg(level='error', message='Balance underloaded')
                        break

        self.reading_signal.emit(self.latest_weight)

    def get_stable_reading(self):
        #Command: I2 Inquiry of balance data.
        #Response: I2 A Balance data as "text".
        self.ser.write(b"S\r")
        while True:
            y = self.ser.readline().split(b" ")
            for item in y:
                if is_number(item):
                    val = float(item)
                    break
                else:
                    if item == b'I':
                        self.log_msg(level = 'error', message='Weight unstable or balance busy')
                        break
                    elif item == b'+':
                        self.log_msg(level = 'error', message='Balance overloaded')
                        break
                    elif item == b'-':
                        self.log_msg(level = 'error', message='Balance underloaded')
                        break

        self.reading_signal.emit(val)

    def log_msg(self, message: str, level: str = None) -> None:
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
            balance_logger.debug(log_entry)
        elif level == 'error':
            root_logger.error(log_entry)
            balance_logger.error(log_entry)
        elif level == 'warning':
            root_logger.warning(log_entry)
            balance_logger.warning(log_entry)
        else:
            root_logger.info(log_entry)
            balance_logger.info(log_entry)