from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from typing import List, Tuple

from Hardware.Abstract.abstract_ua_interface import AbstractUAInterface
from Utilities.useful_methods import log_msg


class SimulatedUAInterface(AbstractUAInterface):
    connected_signal = QtCore.pyqtSignal(bool)

    cal_data_signal = QtCore.pyqtSignal(list, str, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.write_result: bool = False
        self.read_result: bool = True
        try:
            if self.config['Debugging']['simulate_ua_error']:
                self.read_result = False
        except KeyError:
            pass
        self.ua_calibration_data = ['1', 'GG1138', '20201005', '3', '4.29', '13.58', '-89.6', '63.6', '65.4', '67.5',
                                    '66.8', '65.2',
                                    '62.4', '70.0', '69.8', '71.2', '68.1', '38.7', '38.7', '42.5', '37.3', '44.6',
                                    '46.0', '45.5',
                                    '45.0', '40.8', '39.7']

    def connect_hardware(self) -> Tuple[bool, str]:
        """Sets the connected flag to true and emits a connected signal"""
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self) -> None:
        """Sets the connected flag to false and emits a disconnect signal"""
        self.connected = False
        self.connected_signal.emit(self.connected)

    def check_connected(self) -> Tuple[bool, str]:
        """Returns boolean of whether the UA interface is connected"""
        return self.connected, ""

    def wrap_up(self) -> None:
        """
        calls the disconnect hardware method for the simulated UA
        """
        self.disconnect_hardware()

    @pyqtSlot()
    def read_data(self) -> Tuple[List[str], str, int]:
        """emits and returns the calibration data list, version string, and status integer"""
        self.read_result = True
        self.cal_data_signal.emit(self.ua_calibration_data, 'V1.0', 0)
        return self.ua_calibration_data, 'V1.0', 0

    def log(self, message: str, level: str = "info"):
        """Log messages in varying levels of importance to the console"""
        log_msg(self, self.root_logger, message=message, level=level)

    def write_data(self, data: List[str]) -> bool:
        """Attempts to write the passed list of calibration data to the internal variable of the simulated UA"""
        try:
            self.ua_calibration_data = data
            self.write_result = True
        except Exception as e:
            self.log(level='error', message=f'could not write data to UA: {e}')
            self.write_result = False
        return self.write_result

    def get_serial_number(self) -> str:
        """Gets the serial number of the simulated UA interface"""
        return '"Simulated"'


if __name__ == "__main__":
    wtf = SimulatedUAInterface(config=None)
    print(wtf.read_data())
    wtf.write_data(
        ['1', 'LC0013', '20220606', '3', '4.29', '13.74', '-90.0', '86', '86', '86', '86', '86', '86', '86', '86', '86',
         '86', '86', '86', '86', '86', '86', '86', '86', '86', '86', '86'])
