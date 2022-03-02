from abc import abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal, QThread
import random

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)

import serial

from Utilities.useful_methods import log_msg
import os
from definitions import ROOT_DIR
balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR,"./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

from Utilities.load_config import load_configuration
from Hardware.abstract_sensor import AbstractSensor
import time as t

class Relay_Board(AbstractSensor):
    def __init__(self, config = None, device_key = 'Pump'):
        self.config = config
        self.device_key = device_key
        self.ser = None
        self.fields_setup()

        super().__init__(config = config)
        self.on = False

    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.on_by_default = self.config[self.device_key]['on_by_default']
        self.port = self.config[self.device_key]['port']

    def connect(self):
        try:
            self.ser = serial.Serial(
                port=self.port,  # May vary depending on computer
                baudrate=9600,
                timeout=self.timeout_s,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
            )
            self.ser.write(b"ON\r")
            self.connected = True
        except serial.serialutil.SerialException:
            self.connected = False
            log_msg(self, root_logger, level='info', message=
            "Radiation force balance not connected. Check that it is plugged in and look at Device manager "
            "to determine which COM port to use. It is currently hard coded")
        self.connected_signal.emit(self.connected)


        self.relay_write(self.on_by_default)

    def disconnect_sensor(self):
        if self.ser is None:
            log_msg(self, root_logger,level='error', message=f'{self.device_key} not connected')
            return

        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        if self.ser is None:
            log_msg(self, root_logger,level='error', message=f'{self.device_key} not connected')
            return

        self.ser.write(b"\xFF\x01\x03\n") #Check state command

        starttime = t.time()
        while t.time() - starttime < self.timeout_s:
            reply = self.ser.readline()
            if reply == b'\xff\x01\x01': #On reply
                self.on = True
                log_msg(self, root_logger,f"{self.device_key} is ON")
                self.reading_signal.emit(1)
                return True
            elif reply == b'\xff\x01\x00': #Off reply
                self.on = False
                log_msg(self, root_logger,f"{self.device_key} is OFF")
                self.reading_signal.emit(0)
                return False


    def relay_write(self, on: bool):
        if self.ser is None:
            log_msg(self, root_logger,level='error', message=f'{self.device_key} not connected')
            return

        if on:
            self.ser.write(b"\xFF\x01\x01\n") #On command
            self.get_reading()
        else:
            self.ser.write(b"\xFF\x01\x00\n") #Off command
            self.get_reading()

        #self.on = on

if __name__ == '__main__':
    switch = Relay_Board()
    switch.connect()
    switch.relay_write(True)
    switch.relay_write(False)

