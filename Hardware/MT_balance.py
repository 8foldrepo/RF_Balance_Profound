from Hardware.abstract_sensor import AbstractSensor
from abc import abstractmethod
import serial
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import  time as t

from Utilities.useful_methods import is_number

from Utilities.load_config import load_configuration

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

class MT_balance(QObject):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config, device_key = "MT_Balance"):
        super().__init__()
        self.config = config
        self.device_key = device_key

        self.ser = None

        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.port = self.config[self.device_key]['port']

    """Zeroes the scale with the next stale weight reading"""
    def zero_balance(self):
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text".
        if self.ser is None or self.connected == False:
            log_msg(self, root_logger,"Device is not connected")
            return
        log_msg(self, root_logger,"Zeroing Balance, Please wait")
        self.ser.write(b"\nZ\n")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if item == b'Z A':
                    log_msg(self, root_logger,level='info', message='Balance Zeroed')
                    return
                else:
                    if item == b'I':
                        log_msg(self, root_logger,level='error', message='Weight unstable or balance busy')
                        return
                    elif item == b'+':
                        log_msg(self, root_logger,level='error', message='Balance overloaded')
                        return
                    elif item == b'-':
                        log_msg(self, root_logger,level='error', message='Balance underloaded')
                        return
        log_msg(self, root_logger,level='error', message=f'{self.device_key} timed out')

    #TODO: make code recognize the com port without hard coding it
    def connect(self):
        try:
            self.ser = serial.Serial(
                port=self.port,  # May vary depending on computer
                baudrate=1200,
                timeout=self.timeout_s,
                parity=serial.PARITY_ODD,
                stopbits=serial.STOPBITS_TWO,
                bytesize=serial.SEVENBITS,
            )
            self.ser.write(b"ON\r")
            self.connected = True
        except serial.serialutil.SerialException:
            self.connected = False
            log_msg(self, root_logger,level='info', message=
            "Radiation force balance not connected. Check that it is plugged in and look at Device manager to determine which COM port to use. It is currently hard coded"
                         )
        self.connected_signal.emit(self.connected)

    def disconnect_sensor(self):
        if self.ser is None:
            log_msg(self, root_logger,level='error', message=f'{self.device_key} not connected')
            return

        self.ser.close()
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        if self.ser is None:
            log_msg(self, root_logger,level='error', message=f'{self.device_key} not connected')
            return

        self.ser.write(b"SI\n")
        log_msg(self, root_logger,"Getting weight, please wait")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if b'S D' in item:
                    chunks = item.split(b" ")
                    for chunk in chunks:
                        if is_number(chunk):
                            val = float(chunk)
                            log_msg(self, root_logger,f'Weight acquired: {val} g')
                            self.latest_weight = val
                            self.reading_signal.emit(val)
                            return
                else:
                    if item == b'I':
                        log_msg(self, root_logger,level = 'error', message='Weight unstable or balance busy')
                        return
                    elif item == b'+':
                        log_msg(self, root_logger,level = 'error', message='Balance overloaded')
                        return
                    elif item == b'-':
                        log_msg(self, root_logger,level = 'error', message='Balance underloaded')
                        return
        log_msg(self, root_logger,level='error', message=f'{self.device_key} timed out')

    def reset(self):
        if self.ser is None:
            log_msg(self, root_logger,level='error', message=f'{self.device_key} not connected')
            return

        self.ser.write(b"\n@\n")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if not item == b'':
                    log_msg(self, root_logger,"Reset")
                    return
        log_msg(self, root_logger,level='error', message=f'{self.device_key} timed out')

    def get_stable_reading(self):
        if self.ser is None:
            log_msg(self, root_logger,level='error', message=f'{self.device_key} not connected')
            return
        #Command: I2 Inquiry of balance data.
        #Response: I2 A Balance data as "text".
        self.ser.write(b"\nS\n")
        log_msg(self, root_logger,"Getting stable weight, please wait")

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            y = self.ser.readline().split(b"\r\n")
            for item in y:
                if b'S S' in item:
                    chunks = item.split(b" ")
                    for chunk in chunks:
                        if is_number(chunk):
                            val = float(chunk)
                            log_msg(self, root_logger,f'Stable weight acquired: {val} g')
                            self.latest_weight = val
                            self.reading_signal.emit(val)
                            return
                else:
                    if item == b'I':
                        log_msg(self, root_logger,level = 'error', message='Weight unstable or balance busy')
                        return
                    elif item == b'+':
                        log_msg(self, root_logger,level = 'error', message='Balance overloaded')
                        return
                    elif item == b'-':
                        log_msg(self, root_logger,level = 'error', message='Balance underloaded')
                        return
        log_msg(self, root_logger,level='error', message=f'{self.device_key} timed out')

    def log_msg(self, message: str, level: str = None) -> None:
        print(message)
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

if __name__ == '__main__':
    balance = MT_balance(config=load_configuration())
    balance.connect()
    balance.reset()
    balance.zero_balance()
    input('press enter when weight is on scale')
    balance.get_reading()
    balance.get_stable_reading()