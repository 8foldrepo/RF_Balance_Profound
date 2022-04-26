from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Hardware.Abstract.abstract_ua_interface import AbstractUAInterface
from Utilities.useful_methods import log_msg


class SimulatedUAInterface(AbstractUAInterface):
    connected_signal = pyqtSignal(bool)

    cal_data_signal = pyqtSignal(list, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.UA_Write_Result = False
        self.UA_Read_Result = False
        self.ua_calibration_data = {
            'cal_data_array': {
                'schema': '',
                'serial_no': '',
                'production_date': '',
                'hardware_code': '',
                'common_lo_freq': '',
                'common_hi_freq': '',
                'beam_align': '',
                'command': '',
                'status': '',
                'fwversion': '',
                'efficiency_low_list': '',
                'efficiency_high_list': ''
            },
            'low_freq': {
                'schema': '',
                'serial_no': '',
                'production_date': '',
                'hardware_code': '',
                'common_lo_freq': '',
                'common_hi_freq': '',
                'beam_align': '',
                'command': '',
                'status': '',
                'fwversion': ''
            },
            'high_freq': {
                'schema': '',
                'serial_no': '',
                'production_date': '',
                'hardware_code': '',
                'common_lo_freq': '',
                'common_hi_freq': '',
                'beam_align': '',
                'command': '',
                'status': '',
                'fwversion': ''
            }
        }

    def fields_setup(self):
        pass

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ''

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def check_connected(self):
        return self.connected, ''

    def wrap_up(self):
        self.disconnect_hardware()

    @pyqtSlot()
    def read_data(self):
        self.UA_Read_Result = True
        self.cal_data_signal.emit(['1', 'GG1138', '20201005', '3', '4.29', '13.58', '-89.6', '63.6', '65.4', '67.5',
                                   '66.8', '65.2',
                                   '62.4', '70.0', '69.8', '71.2', '68.1', '38.7', '38.7', '42.5', '37.3', '44.6',
                                   '46.0', '45.5',
                                   '45.0', '40.8', '39.7'], 0)
        return ['1', 'GG1138', '20201005', '3', '4.29', '13.58', '-89.6', '63.6', '65.4', '67.5', '66.8', '65.2',
                '62.4', '70.0', '69.8', '71.2', '68.1', '38.7', '38.7', '42.5', '37.3', '44.6', '46.0', '45.5',
                '45.0', '40.8', '39.7'],0

    def log(self, message, level='info'):
        log_msg(self, self.root_logger, message=message, level=level)

    def write_data(self):
        self.UA_Write_Result = True
        return True


if __name__ == "__main__":
    wtf = SimulatedUAInterface(config=None)
    print(wtf.read_data())
