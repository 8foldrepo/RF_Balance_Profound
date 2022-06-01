import re
import subprocess
import time as t
from subprocess import Popen, PIPE

from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Hardware.Abstract.abstract_ua_interface import AbstractUAInterface
from definitions import ROOT_DIR


class UAInterface(AbstractUAInterface):
    connected_signal = pyqtSignal(bool)
    cal_data_signal = pyqtSignal(list, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
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
    def read_data(self):
        # cal_data_signal.emit(self.cal_data_signal)
        output = self.get_command_output()

        if output is None:
            self.log(level="Error", message="UA interface timed out due to invalid byte(s), could be a faulty cable?")
            self.cal_data_signal.emit([], -1)
            return [], -1

        if "status=-2" in output:
            self.log(level="Error", message="wtfib is not connected (check power and ethernet connection)")
            self.cal_data_signal.emit([], -2)
            return [], -2

        if not "Calibration data" in output:
            self.log(level="Error", message="Calibration data not found in output, read failed")
            self.cal_data_signal.emit([], -3)
            return [], -3

        # Try to extract the status number from the output, otherwise retry
        calibration_string_pre = output.splitlines()[3]
        calibration_string_pre_list = calibration_string_pre.split(" ")
        # Search for number in the string containing "status = "
        status_str = calibration_string_pre_list[2]
        try:
            status = int(re.search(r"\d+", status_str).group())
        except:
            status = -4

        if status == 1:
            self.cal_data_signal.emit([], -1)
            self.log(level = 'error', message="No ua found...")
            return [], -1

        calibration_string_pre_list2 = calibration_string_pre_list[5]
        calibration_data_quotes_removed = calibration_string_pre_list2.strip('"')
        calibration_data_list = calibration_data_quotes_removed.split(",")

        if len(calibration_data_list) < 27:
            self.log(level="Error", message=f"Calibration data contained less than 27 items : {calibration_data_list}")
            return [], -5

        self.ua_calibration_data = calibration_data_list
        self.cal_data_signal.emit(calibration_data_list, status)
        self.read_result = True
        return calibration_data_list, status

    def write_data(self, ua_calibration_data=None):
        print(ua_calibration_data)
        if ua_calibration_data is None:
            ua_calibration_data = self.ua_calibration_data

        first_string = f"{self.path_of_exe} {self.ip_address} " + " ".join(ua_calibration_data[0:7])
        low_eff_string = f'\"{" ".join(ua_calibration_data[7:17])}\"'
        high_eff_string = f'\"{" ".join(ua_calibration_data[17:27])}\"'

        process_call = first_string + " " + low_eff_string + " " + high_eff_string
        self.log(process_call)
        subprocess.call(process_call)

        output = self.get_command_output()

        if "status=-2" in output:
            self.log(level='error', message='wtfib is not connected (check power and ethernet connection)')
            self.write_result = False
            return -2

        if "status=-9" in output:
            self.log(level='error', message='calibration data incomplete, invalid, or improperly formatted')
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

    def get_command_output(self):
        startTime = t.time()
        # Try to get usable data until timeout occurs
        while t.time() - startTime < self.timeout_s:
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


if __name__ == "__main__":
    wtf = UAInterface(config=None)
    print(wtf.read_data())
    wtf.write_data(
        ['1', 'LC0013', '20210922', '3', '4.29', '13.74', '-95.5', '42.8', '47.1', '63.6', '60.5', '54.2', '58.2',
         '57.1',
         '76.8', '53.2', '75.3', '38.7', '38.3', '40.9', '40.5', '37.1', '40.4', '40.1', '40.0', '39.0', '36.9'])
