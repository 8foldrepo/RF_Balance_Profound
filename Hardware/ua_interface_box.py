from PyQt5.QtCore import pyqtSignal, QObject
import subprocess
from Hardware.Abstract.abstract_device import AbstractDevice
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from Utilities.useful_methods import log_msg
from abc import abstractmethod
import os
from subprocess import Popen, PIPE
import time as t
from definitions import ROOT_DIR
from Utilities.useful_methods import log_msg
from Hardware.Abstract.abstract_device import AbstractDevice


class UAInterfaceBox(AbstractDevice):
    connected_signal = pyqtSignal(bool)
    dummy_command_signal = pyqtSignal(str)

    cal_data_signal = pyqtSignal(list, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.ip_address = '192.168.3.3'
        self.path_of_exe = ROOT_DIR + "\\Hardware\\interface_box_executable\\WTFiB_Calib.exe"

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

        self.log('Attempting to connect to WTFIB... ')

        p = Popen(["ping", self.ip_address, "-n","1"], stdout=PIPE)
        output = p.communicate()[0].decode()
        if 'timed out' in output:
            self.log('ping to WTFIB timed out')
            self.is_connected = False
            self.connected_signal.emit(self.is_connected)
            return

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
        # cal_data_signal.emit(self.cal_data_signal)

        global output

        startTime = t.time()
        timeout_s = 5
        while t.time() - startTime < timeout_s:
            try:
                p = Popen(["cmd", "/C", self.path_of_exe, self.ip_address], stdout=PIPE)
                output = p.communicate()[0].decode()
                break
            except UnicodeDecodeError as e:
                self.log(level='error', message=str(e))
                if str(e) == "'utf-8' codec can't decode byte 0xb8 in position 150: invalid start byte":
                    print("Getting output failed, retrying...")
        if "no UA" in output:
            # Trigger dialog box
            self.cal_data_signal.emit([], -1)
            self.log("No ua found...")
            return [], -1
        elif "Returned FW status=-2. FW version query failed and returned \"(null)\"" in output:
            self.cal_data_signal.emit([], -2)
            self.log("wtfib is not connected (check power and ethernet connection)")
            return [], -2
        else:
            calibration_string_pre = output.splitlines()[3]
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

            self.cal_data_signal.emit(calibration_data_list, status)
            return calibration_data_list, status

    def log(self, message, level='info'):
        log_msg(self, self.root_logger, message=message, level=level)

    def write_data(self):
        process_call = f"{self.path_of_exe} {self.ip_address} " + \
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

if __name__ == '__main__':
    wtf = UAInterfaceBox(config=None)
    print(wtf.read_data())

