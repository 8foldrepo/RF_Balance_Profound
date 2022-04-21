import re
import subprocess
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from subprocess import Popen, PIPE
import time as t
from definitions import ROOT_DIR
from Hardware.Abstract.abstract_device import AbstractDevice


class UAInterfaceBox(AbstractDevice):
    connected_signal = pyqtSignal(bool)
    dummy_command_signal = pyqtSignal(str)
    cal_data_signal = pyqtSignal(list, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.ip_address = '192.168.3.3'
        self.UA_Read_Result = False
        self.UA_Write_Result = False
        self.path_of_exe = ROOT_DIR + "\\Hardware\\interface_box_executable\\WTFiB_Calib.exe"

        self.ua_calibration_data = None
        self.fields_setup()

    def fields_setup(self):
        self.timeout_s = self.config[self.device_key]['timeout_s']

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
        self.log('WTFIB connected successfully')
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

        output = self.get_command_output()

        if output is None:
            self.log(level="Error", message="UA interface timed out due to invalid byte(s), could be a faulty cable?")
            return [], -1

        if "status=-2" in output:
            self.log(level="Error", message="wtfib is not connected (check power and ethernet connection)")
            return [], -2

        if not "Calibration data" in output:
            self.log(level="Error", message="Calibration data not found in output, read failed")
            return [], -3

        #Try to extract the status number from the output, otherwise retry
        calibration_string_pre = output.splitlines()[3]
        calibration_string_pre_list = calibration_string_pre.split(' ')
        # Search for number in the string containing "status = "
        status_str = calibration_string_pre_list[2]
        try:
            status = int(re.search(r'\d+', status_str).group())
        except:
            status = -4

        if status == 1:
            self.cal_data_signal.emit([], -1)
            self.log("No ua found...")
            return [], -1

        calibration_string_pre_list2 = calibration_string_pre_list[5]
        calibration_data_quotes_removed = calibration_string_pre_list2.strip('"')
        calibration_data_list = calibration_data_quotes_removed.split(',')

        if len(calibration_data_list)<27:
            self.log(level="Error", message=f"Calibration data contained less than 27 items : {calibration_data_list}")
            return [], -5

        self.ua_calibration_data = calibration_data_list
        self.cal_data_signal.emit(calibration_data_list, status)
        return calibration_data_list, status

    def write_data(self, ua_calibration_data = None):
        if ua_calibration_data is None:
            ua_calibration_data = self.ua_calibration_data

        first_string = f"{self.path_of_exe} {self.ip_address} "+" ".join(ua_calibration_data[0:7])
        low_eff_string = f'\"{" ".join(ua_calibration_data[7:17])}\"'
        high_eff_string = f'\"{" ".join(ua_calibration_data[17:27])}\"'

        process_call = first_string + " " + low_eff_string + " " + high_eff_string
        self.log(process_call)
        subprocess.call(process_call)

        output = self.get_command_output()

        if "status=0" in output:
            self.log('UA write successful')
            self.UA_Write_Result = True
            return 0

        if "status=-2" in output:
            self.log(level='error', message='wtfib is not connected (check power and ethernet connection)')
            self.UA_Write_Result = False
            return -2

        if "status=2" in output:
            self.log(level='error', message='No UA connected, write failed')
            self.UA_Write_Result = False
            return 2

        self.log(level='error', message=f'Unrecognized write code: \n{output}')
        self.UA_Write_Result = False
        return -3

    def get_command_output(self):
        startTime = t.time()
        # Try to get usable data until timeot occurs
        while t.time() - startTime < self.timeout_s:
            # Get command prompt output, if it is illegible, retry
            try:
                p = Popen(["cmd", "/C", self.path_of_exe, self.ip_address], stdout=PIPE)
                output = p.communicate()[0].decode()
                return output
            except UnicodeDecodeError as e:
                self.log(level='error', message=str(e))
                if str(e) == "\'utf-8\' codec can't decode byte 0xb8 in position 150: invalid start byte":
                    print("Getting output failed, retrying...")
        return None

if __name__ == '__main__':
    wtf = UAInterfaceBox(config=None)
    print(wtf.write_data(['1', 'GG1138', '20201005', '3', '4.29', '13.58', '-89.6', '63.6', '65.4', '67.5', '66.8', '65.2',
                    '62.4', '70.0', '69.8', '71.2', '68.1', '38.7', '38.7', '42.5', '37.3', '44.6', '46.0', '45.5',
                    '45.0', '40.8', '39.7']))
    print(wtf.read_data())
