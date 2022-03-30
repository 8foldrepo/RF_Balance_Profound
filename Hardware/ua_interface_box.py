import subprocess
from Hardware.Abstract.abstract_device import AbstractDevice
from PyQt5.QtCore import pyqtSignal, QObject
from Utilities.useful_methods import log_msg
from abc import abstractmethod


class UAInterfaceBox(AbstractDevice):
    connected_signal = pyqtSignal(bool)

    cal_data_signal = pyqtSignal(object)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)

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

    def read_data(self) -> list:
        # cal_data_signal.emit(self.cal_data_signal)
        command_output = subprocess.check_output('/interface_box_executable/WTFiB_Calib', '192.168.3.1').decode()
        calibration_string_pre = command_output.splitlines()[3]
        calibration_string_pre_list = calibration_string_pre.split(' ')
        status = int(calibration_string_pre_list[3].split('=')[1])
        calibration_string_pre_list2 = calibration_string_pre_list[5]
        calibration_data_quotes_removed = calibration_string_pre_list2.strip('"')
        calibration_data_list = calibration_data_quotes_removed.split(',')

        self.ua_calibration_data['cal_data_array']['schema'] = calibration_data_list[0]
        self.ua_calibration_data['cal_data_array']['serial_no'] = calibration_data_list[1]
        self.ua_calibration_data['cal_data_array']['production_date'] = calibration_data_list[2]
        self.ua_calibration_data['cal_data_array']['hardware_code'] = calibration_data_list[3]
        self.ua_calibration_data['cal_data_array']['common_lo_freq'] = calibration_data_list[4]
        self.ua_calibration_data['cal_data_array']['common_hi_freq'] = calibration_data_list[5]
        self.ua_calibration_data['cal_data_array']['beam_align'] = calibration_data_list[6]
        self.ua_calibration_data['cal_data_array']['efficiency_low_list'] = calibration_data_list[7:16]
        self.ua_calibration_data['cal_data_array']['efficiency_high_list'] = calibration_data_list[17:26]

        return calibration_data_list, status

    def write_data(self):
        process_call = "/interface_box_executable/WTFib_Calib 192.168.3.1 " + \
                       self.ua_calibration_data['cal_data_array']['schema'] + "," + \
                       self.ua_calibration_data['cal_data_array']['serial_no'] + "," + \
                       self.ua_calibration_data['cal_data_array']['production_date'] + "," + \
                       self.ua_calibration_data['cal_data_array']['hardware_code'] + "," + \
                       self.ua_calibration_data['cal_data_array']['common_lo_freq'] + "," + \
                       self.ua_calibration_data['cal_data_array']['common_hi_freq'] + "," + \
                       self.ua_calibration_data['cal_data_array']['beam_align'] + "," + \
                       ','.join(map(str, self.ua_calibration_data['cal_data_array']['efficiency_low_list'])) + "," + \
                       ','.join(map(str, self.ua_calibration_data['cal_data_array']['efficiency_high_list']))
        subprocess.call(process_call)
