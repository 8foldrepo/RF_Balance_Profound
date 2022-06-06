from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

from Hardware.Abstract.abstract_ua_interface import AbstractUAInterface
from Utilities.useful_methods import log_msg


class SimulatedUAInterface(AbstractUAInterface):
    connected_signal = QtCore.pyqtSignal(bool)

    cal_data_signal = QtCore.pyqtSignal(list, str, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.write_result = False
        self.read_result = True
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

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def check_connected(self):
        return self.connected, ""

    def wrap_up(self):
        self.disconnect_hardware()

    @pyqtSlot()
    def read_data(self):
        self.read_result = True
        self.cal_data_signal.emit(self.ua_calibration_data, 'V1.0', 0)
        return self.ua_calibration_data, 'V1.0', 0

    def log(self, message, level="info"):
        log_msg(self, self.root_logger, message=message, level=level)

    def write_data(self, data):
        self.write_result = True
        return True

    def get_serial_number(self) -> str:
        return '"Simulated"'


if __name__ == "__main__":
    wtf = SimulatedUAInterface(config=None)
    print(wtf.read_data())
    wtf.write_data(
        ['1', 'LC0013', '20220606', '3', '4.29', '13.74', '-90.0', '86', '86', '86', '86', '86', '86', '86', '86', '86',
         '86', '86', '86', '86', '86', '86', '86', '86', '86', '86', '86'])
