import re
import time as t
from subprocess import Popen, PIPE
from typing import Tuple, List

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

from Hardware.Abstract.abstract_ua_interface import AbstractUAInterface
from definitions import ROOT_DIR


class UAInterface(AbstractUAInterface):
    connected_signal = QtCore.pyqtSignal(bool)
    cal_data_signal = QtCore.pyqtSignal(list, str, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.timeout_s = None
        self.ip_address = "192.168.3.3"
        self.read_result = False
        self.write_result = False
        self.path_of_exe = ROOT_DIR + "\\Hardware\\interface_box_executable\\WTFiB_Calib.exe"
        self.ua_calibration_data = None
        self.fields_setup()

    def fields_setup(self):
        self.timeout_s = self.config[self.device_key]["timeout_s"]

    def connect_hardware(self):
        self.connected = True

        self.log("Attempting to connect to WTFIB... ")

        # Ping the UA interface
        p = Popen(["ping", self.ip_address, "-n", "1"], stdout=PIPE)
        output = p.communicate()[0].decode()

        if "timed out" in output:
            feedback = "ping to WTFIB timed out"
            self.connected = False
        else:
            feedback = "WTFIB connected successfully"
            self.connected = True

        if not self.connected:
            self.log(feedback, level="error")
        else:
            self.log(feedback)
        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def check_connected(self):
        return self.connected

    def wrap_up(self):
        self.disconnect_hardware()

    @pyqtSlot()
    def read_data(self) -> Tuple[List[str], str, int]:
        # cal_data_signal.emit(self.cal_data_signal)
        output = self.get_read_command_output()
        if output is None:
            self.log(level="Error", message="UA interface timed out due to invalid byte(s), could be a faulty cable?")
            self.cal_data_signal.emit([], '', -1)
            return [], '', -1

        if "status=-2" in output:
            self.log(level="Error", message="wtfib is not connected (check power and ethernet connection)")
            self.cal_data_signal.emit([], '', -2)
            return [], '', -2

        if "Calibration data" not in output:
            self.log(level="Error", message="Calibration data not found in output, read failed")
            self.cal_data_signal.emit([], '', -3)
            return [], '', -3

        # Try to extract the status number from the output, otherwise retry
        firmware_string = output.splitlines()[0]
        fw_version = firmware_string.split(' ')[7]
        calibration_string_pre = output.splitlines()[3]
        calibration_string_pre_list = calibration_string_pre.split(" ")
        # Search for number in the string containing "status = "
        status_str = calibration_string_pre_list[2]
        try:
            device_status = int(re.search(r"\d+", status_str).group())
        except Exception:
            device_status = -4

        if device_status == 1:
            self.cal_data_signal.emit([], '', -1)
            self.log(level='error', message="No ua found...")

            return [], '', -1

        calibration_string_pre_list2 = calibration_string_pre_list[5]
        calibration_data_quotes_removed = calibration_string_pre_list2.strip('"')
        calibration_data_list = calibration_data_quotes_removed.split(",")

        if len(calibration_data_list) < 27:
            self.log(level="Error", message=f"Calibration data contained less than 27 items : {calibration_data_list}")
            return [], '', -5

        self.ua_calibration_data = calibration_data_list
        self.cal_data_signal.emit(calibration_data_list, fw_version, device_status)
        self.read_result = True
        return calibration_data_list, fw_version, device_status

    def write_data(self, ua_calibration_data=None):
        if ua_calibration_data is None:
            ua_calibration_data = self.ua_calibration_data

        output = self.get_write_command_output(ua_calibration_data)

        if "status=-2" in output:
            self.log(level='error', message='WTFIB is not connected (check power and ethernet connection)')
            self.write_result = False
            return -2

        if "status=-9" in output:
            self.log(level='error',
                     message=f'calibration data incomplete, invalid, or improperly formatted: {ua_calibration_data}')
            self.write_result = False
            return -9

        # if "status=2" in output:
        #     self.log(level="error", message="No UA connected, write failed")
        #     self.write_result = False
        #     return 2

        if "status=0" in output:
            self.log("UA write successful")
            self.write_result = True
            return 0

        self.log(level="error", message=f"Unrecognized write code: \n{output}")
        self.write_result = False
        return -3

    def get_read_command_output(self):
        start_time = t.time()
        # Try to get usable data until timeout occurs
        while t.time() - start_time < self.timeout_s:
            # Get command prompt output, if it is illegible, retry
            try:
                p = Popen(["cmd", "/C", self.path_of_exe, self.ip_address], shell=False, stdout=PIPE)
                output = p.communicate()[0].decode()
                return output
            except UnicodeDecodeError as e:
                self.log(level='error', message=str(e))
                if str(e) == "\'utf-8\' codec can't decode byte 0xb8 in position 150: invalid start byte":
                    self.log("Getting output failed, retrying...")
        return None

    def get_write_command_output(self, calibration_data):
        first_string = " ".join(calibration_data[0:7])
        low_eff_string = f'\"{" ".join(calibration_data[7:17])}\"'
        high_eff_string = f'\"{" ".join(calibration_data[17:27])}\"'

        command_str = self.path_of_exe + " " + self.ip_address + " " + first_string + " " + low_eff_string + " " + high_eff_string

        start_time = t.time()
        # Try to get usable data until timeout occurs

        while t.time() - start_time < self.timeout_s:
            # Get command prompt output, if it is illegible, retry
            try:
                p = Popen(command_str, shell=False, stdout=PIPE)
                output = p.communicate()[0].decode()
                print(output)
                return output
            except UnicodeDecodeError as e:
                self.log(level='error', message=str(e))
                if str(e) == "\'utf-8\' codec can't decode byte 0xb8 in position 150: invalid start byte":
                    self.log("Getting output failed, retrying...")
        return None


if __name__ == "__main__":
    wtf = UAInterface(config=None)
    data, firmware_str, status = wtf.read_data()

    print(data)

    wtf.write_data(['1', 'LC0013', '20220606', '3', '4.29', '13.74', '-90.0', '86.0', '86.0', '86.0', '86.0', '86.0',
                    '86.0', '86.0', '86.0', '86.0',
                    '86.0', '86.0', '86.0', '86.0', '86.0', '86.0', '86.0', '86.0', '86.0', '86.0', '86.0'])
