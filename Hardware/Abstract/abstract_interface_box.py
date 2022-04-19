from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Utilities.useful_methods import log_msg
from Hardware.Abstract.abstract_device import AbstractDevice


class UAInterfaceBox(AbstractDevice):
    connected_signal = pyqtSignal(bool)
    dummy_command_signal = pyqtSignal(str)

    cal_data_signal = pyqtSignal(list, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.UA_Write_Result = False
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
        self.is_connected = True
        self.connected_signal.emit(self.is_connected)

    def disconnect_hardware(self):
        self.is_connected = False
        self.connected_signal.emit(self.is_connected)

    def connected(self):
        return self.is_connected

    def wrap_up(self):
        self.disconnect_hardware()

    @pyqtSlot()
    def read_data(self):
        pass

    def log(self, message, level='info'):
        log_msg(self, self.root_logger, message=message, level=level)

    def write_data(self):
       pass

if __name__ == "__main__":
    wtf = UAInterfaceBox(config=None)
    print(wtf.read_data())
