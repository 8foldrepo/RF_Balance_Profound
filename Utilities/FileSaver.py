from Utilities.useful_methods import log_msg, check_directory, create_test_results_summary_file
from Utilities.variable_containers import FileMetadata, TestData
from definitions import ROOT_DIR
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
import logging
import shutil
import os

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
wtf_logger.addHandler(file_handler)
wtf_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)
log_formatter = logging.Formatter(LOGGER_FORMAT)


class FileSaver:
    test_data: TestData
    folder_name = None
    results_dir = None
    log_files_dir = None
    power_data_path = None
    waveform_data_path = None
    directories_created = False

    def __init__(self, config):
        if config is not None:
            self.config = config
        else:
            self.config = load_configuration()

    def create_folders(self, test_data):
        self.test_data = test_data
        self.create_results_folder()
        self.create_subfolders()
        self.copy_system_info()


    def create_results_folder(self):
        self.folder_name = self.test_data.serial_number + "-" + self.test_data.test_date_time
        results_path = os.path.join(self.config['Paths']['UA results root directory'], self.folder_name)
        # Retrieve the path of the results directory from the yaml file and create it if it does not exist
        self.results_dir = check_directory(results_path)

    def create_subfolders(self):
        if self.results_dir is None:
            self.log(level='error', message='Could not create subfolders before results folder, check function call')
            return

        log_files_path = os.path.join(self.results_dir, 'Log files')
        self.log_files_dir = check_directory(log_files_path)

        power_data_path = os.path.join(self.results_dir, 'Power data')
        self.power_data_path = check_directory(power_data_path)

        waveform_data_path = os.path.join(self.results_dir, 'Waveform data')
        self.waveform_data_path = check_directory(waveform_data_path)
        self.directories_created = True

    '''Copies the system info file into the results directory'''

    def copy_system_info(self):
        if self.log_files_dir is None:
            self.log(level='error', message='Could save config, log_files_dir does not exist')

        system_info_file = os.path.join(ROOT_DIR, 'systeminfo.ini')
        if not os.path.exists(system_info_file):
            self.log(level='Error', message='Could not store system info to results folder')
            self.log(level='Error', message=f'systeminfo.ini was not found in {ROOT_DIR}')
            return

        destination_path = os.path.join(self.log_files_dir, 'SystemHardware.log')
        shutil.copyfile(src=system_info_file, dst=destination_path)

    '''Save the test data (shared with the manager) to the results folder in the form of a  results summary'''

    def save_test_results_summary_and_log(self, test_data: TestData):
        if not test_data:  # if dictionary is empty return
            self.log(level='error', message='No results to save')
            return

        self.test_data = test_data

        path = os.path.join(self.results_dir, "Results Summary.txt")

        self.log(f"Saving results summary to: {path}")

        create_test_results_summary_file(self.test_data, path)
        self.save_log_file(self.test_data.script_log)

    # turn a 2d list into a .log file (a text file with a different extension
    '''saves the 2d list called log_table to a .log file. defaults to self.test_data if none is provided'''

    def save_log_file(self, log_table=None):
        if log_table is None:
            log_table = self.test_data.script_log

        try:
            path = os.path.join(self.log_files_dir, "ScriptResults.log")
        except TypeError:
            self.log("config has not been loaded and therefore the log path cannot be pulled from there, defaulting "
                     "log path")
            path = "../logs2/ScriptResults.log"

        self.log(f"Saving log file to: {path}")

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        f = open(path, 'w')
        for x in range(len(log_table)):
            f.write('\t'.join(log_table[x]))
            f.write('\n')

    def store_waveform(self, metadata:FileMetadata, times, voltages):  # assume single array every time

        path = check_directory(os.path.join(self.waveform_data_path, 'ElementScans',
                                            f"E{metadata.element_number:02}"))

        file = open(
            os.path.join(path, f"FindElement{metadata.element_number:02}_{metadata.axis}_"
                               f"{metadata.waveform_number}.txt"), 'w+')

        file.write(f"UASerialNumber={self.test_data.serial_number}\n")
        file.write("[File Format]\n")
        file.write(f"Version={self.config['Software_Version']}\n")
        file.write(f"# Arrays=1\n")
        file.write("[Position]\n")
        file.write(f"X={metadata.X}\n")
        file.write(f"Theta={metadata.Theta}\n")
        file.write(f"Calibration Frequency={metadata.frequency_MHz}MHz\n")
        file.write(f"Source Signal Amplitude={metadata.amplitude_mVpp}mVpp\n")
        file.write(f"Source Signal Type={metadata.source_signal_type}\n")
        file.write(f"# Cycles={metadata.num_cycles}\n")
        file.write("[Array 0]\n")
        file.write("Label=\"\"\n")
        file.write("X Data Type=\"Time (s)\"\n")
        file.write("Y Data Type=\"Voltage Waveform (V)\"\n")
        file.write("[Data]\n")
        file.write("Format=\"Cols arranged <X0>, <Y0>, <Uncertainty0> ... <Xn>, <Yn>, <Uncertaintyn>\"\n")
        file.write("Comment=\">>>>Data arrays start here<<<<\"\n")

        if len(times) != len(voltages):
            # self.log(level="error", message=f"length of times = {len(times)} ; length of voltages = {len(voltages)}
            # mismatch in store_find_element_waveform()")
            print(
                f"length of times = {len(times)} ; length of voltages = {len(voltages)} size mismatch in "
                f"store_find_element_waveform()")
            return
        else:
            for x in range(len(times)):
                formatted_time = "{:.6e}".format(times[x])
                formatted_voltage = "{:.6e}".format(voltages[x])
                file.write(f"{formatted_time}\t{formatted_voltage}\t0.000000E+0\n")

    # the three lists are 2D, first col in sub list is time second is voltage

    def store_measure_rfb_waveform(self, metadata, forward_power, reflected_power, acoustic_power):
        path = check_directory(os.path.join(self.power_data_path, 'EfficiencyTest',
                                            f"E{metadata.element_number:02}"))
        file_path = os.path.join(path, f"MeasureRFB_E{metadata.element_number:02}.txt")

        self.log(f"Saving efficiency test data to: {file_path}")
        file = open(file_path, 'w+')
        file.write(f"UASerialNumber={self.test_data.serial_number}\n")
        file.write("[File Format]\n")
        file.write(f"Version={self.config['Software_Version']}\n")
        file.write(f"# Arrays=3\n")
        file.write("[Position]\n")
        file.write(f"X={f'%.2f' % metadata.X}\n")
        file.write(f"Theta={f'%.2f' % metadata.Theta}\n")
        file.write(f"Calibration Frequency={f'%.2f' % metadata.frequency_MHz}MHz\n")
        file.write(f"Source Signal Amplitude={f'%.2f' % metadata.amplitude_mVpp}mVpp\n")
        file.write(f"Source Signal Type={metadata.source_signal_type}\n")
        file.write(f"# Cycles={metadata.num_cycles}\n")
        file.write("[Array 1]\n")
        file.write("Label=\"Forward Power (W)\"\n")
        file.write("X Data Type=\"Time (s)\"\n")
        file.write("Y Data Type=\"Wattage (W)\"\n")
        file.write("[Array 2]\n")
        file.write("Label=\"Reflected Power (W)\"\n")
        file.write("X Data Type=\"Time (s)\"\n")
        file.write("Y Data Type=\"Wattage (W)\"\n")
        file.write("[Array 3]\n")
        file.write("Label=\"Acoustic Power (W)\"\n")
        file.write("X Data Type=\"Time (s)\"\n")
        file.write("Y Data Type=\"Wattage (W)\"\n")
        file.write("[Data]\n")
        file.write(
            "Format=\"Cols arranged <FPX0>, <FPY0>, <RPX0>, <RPY0>, <APX0>, <APY0> ... <FPXn>, <FPYn>, <RPXn>, "
            "<RPYn>, <APXn>, <APYn>\"\n")
        file.write("Comment=\">>>>Data arrays start here<<<<\"\n")

        if len(forward_power) != len(reflected_power) != len(acoustic_power):
            # self.log(level="error", message=f"length of forward_power = {len(forward_power)}, reflected_power = {
            # len(reflected_power)}, and acoustic_power = {len(acoustic_power)} mismatch in
            # store_measure_rfb_waveform()")
            print(
                f"length of forward_power = {len(forward_power)}, reflected_power = {len(reflected_power)}, and "
                f"acoustic_power = {len(acoustic_power)} mismatch in store_measure_rfb_waveform()")
            return
        else:
            if len(forward_power[0]) != len(forward_power[1]):
                # self.log(level="error", message=f"in forward_power length of times = {forward_power[0]}, wattages =
                # {forward_power[1]}") mismatch in store_find_element_waveform()")
                print(
                    f"length of times = {len(forward_power[0])} ; length of wattages = {len(forward_power[1])} size "
                    f"mismatch in forward_power in store_find_element_waveform()")
            elif len(reflected_power[0]) != len(reflected_power[1]):
                # self.log(level="error", message=f"in reflected_power length of times = {reflected_power[0]},
                # wattages = {reflected_power[1]}") mismatch in store_find_element_waveform()")
                print(
                    f"length of times = {len(reflected_power[0])} ; length of wattages = {len(reflected_power[1])} size"
                    f" mismatch in reflected_power in store_find_element_waveform()")
            elif len(acoustic_power[0]) != len(acoustic_power[1]):
                # self.log(level="error", message=f"in acoustic_power length of times = {acoustic_power[0]}, wattages
                # = {acoustic_power[1]}") mismatch in store_find_element_waveform()")
                print(
                    f"length of times = {len(acoustic_power[0])} ; length of wattages = {len(acoustic_power[1])} size"
                    f" mismatch in acoustic_power in store_find_element_waveform()")
            else:
                for x in range(len(forward_power[0])):
                    forward_formatted_time = "{:.6e}".format(forward_power[0][x])
                    forward_formatted_wattage = "{:.6e}".format(forward_power[1][x])
                    reflected_formatted_time = "{:.6e}".format(reflected_power[0][x])
                    reflected_formatted_wattage = "{:.6e}".format(reflected_power[1][x])
                    acoustic_formatted_time = "{:.6e}".format(acoustic_power[0][x])
                    acoustic_formatted_wattage = "{:.6e}".format(acoustic_power[1][x])

                    file.write(
                        f"{forward_formatted_time}\t{forward_formatted_wattage}\t{reflected_formatted_time}\t"
                        f"{reflected_formatted_wattage}\t{acoustic_formatted_time}\t{acoustic_formatted_wattage}\n")

    def save_find_element_profile(self, metadata, positions, vsi_values):
        path = check_directory(os.path.join(self.waveform_data_path, 'ElementScans',
                                            f"E{metadata.element_number:02}"))

        file = open(os.path.join(path, f"FindElement{metadata.element_number:02}_{metadata.axis}__UMSProfile.txt"), 'w+')
        file.write(f"UASerialNumber={self.test_data.serial_number}\n")
        file.write("[File Format]\n")
        file.write(f"Version={self.config['Software_Version']}\n")
        file.write(f"# Arrays=1\n")
        file.write("[Position]\n")
        file.write(f"X={f'%.2f' % metadata.X}\n")
        file.write(f"Theta={f'%.2f' % metadata.Theta}\n")
        file.write(f"Calibration Frequency={f'%.2f' % metadata.frequency_MHz}MHz\n")
        file.write(f"Source Signal Amplitude={metadata.amplitude_mVpp}mVpp\n")
        file.write(f"Source Signal Type={metadata.source_signal_type}\n")
        file.write(f"# Cycles={metadata.num_cycles}\n")
        file.write("[Array 0]\n")
        file.write("Label=\"\"\n")
        if metadata.axis == "R" or metadata.axis == 'Theta':
            file.write("X Data Type=\"Position (deg)\"\n")
        else:
            file.write("X Data Type=\"Distance (mm)\"\n")
        file.write("Y Data Type=\"Voltage Squared Integral\"\n")
        file.write("[Data]\n")
        file.write("Format=\"Cols arranged <X0>, <Y0>, <Uncertainty0> ... <Xn>, <Yn>, <Uncertaintyn>\"\n")
        file.write("Comment=\">>>>Data arrays start here<<<<\"\n")

        if len(positions) != len(vsi_values):
            # self.log(level="error", message=f"length of distances = {len(distances)} ; length of vsi = {len(vsi)}
            # mismatch in store_find_element_waveform()")
            print(
                f"length of distances = {len(positions)} ; length of vsi = {len(vsi_values)} size mismatch in "
                f"store_find_element_waveform()")
            return
        else:
            for x in range(len(positions)):
                formatted_time = "{:.6e}".format(positions[x])
                formatted_voltage = "{:.6e}".format(vsi_values[x])
                file.write(f"{formatted_time}\t{formatted_voltage}\t0.000000E+0\n")

    # todo
    def save_frequency_sweep(self):
        pass

    def log(self, message, level='info'):
        log_msg(self, root_logger, message=message, level=level)

# def test_store_find_element_waveform(file_saver):
#     from numpy.random import uniform
#     metadata = dict()
#     metadata['element_number'] = 1
#     metadata['axis'] = "Th"
#     metadata['waveform_number'] = "Theta000"
#     metadata['serial_number'] = 'GH1214'
#     metadata['version'] = 1.0
#     metadata['X'] = 0.750
#     metadata['Theta'] = -171.198
#     metadata['calibration_frequency_(MHz)'] = '4'
#     metadata['source_signal_amplitude_(mVpp)'] = '50'
#     metadata['source_signal_type'] = 'Toneburst'
#     metadata['num_cycles'] = 0
# 
#     times = list()
#     voltages = list()
# 
#     for x in range(100):
#         times.append(uniform(4.14, 4.64))
#         voltages.append(uniform(-9, 7))
# 
#     times.sort()
# 
#     file_saver.store_waveform(metadata, times, voltages)
# 
# 
# def test_store_measure_rfb_waveform(file_saver):
#     from numpy.random import uniform
#     metadata = dict()
#     metadata['element_number'] = 1
#     metadata['axis'] = "Th"
#     metadata['waveform_number'] = "Theta000"
#     metadata['serial_number'] = 'GH1214'
#     metadata['version'] = 1.0
#     metadata['X'] = 0.750
#     metadata['Theta'] = -171.198
#     metadata['calibration_frequency_(MHz)'] = '4'
#     metadata['source_signal_amplitude_(mVpp)'] = '50'
#     metadata['source_signal_type'] = 'Toneburst'
#     metadata['num_cycles'] = 0
# 
#     forward_power = list()
#     reflected_power = list()
#     acoustic_power = list()
# 
#     times = list()
#     voltages = list()
# 
#     for x in range(20):
#         times.append(uniform(4.14, 4.64))
#         voltages.append(uniform(-9, 7))
# 
#     times.sort()
#     forward_power.append(times)
#     forward_power.append(voltages)
# 
#     times.clear()
#     voltages.clear()
# 
#     for x in range(20):
#         times.append(uniform(4.14, 4.64))
#         voltages.append(uniform(-9, 7))
# 
#     times.sort()
#     reflected_power.append(times)
#     reflected_power.append(voltages)
# 
#     times.clear()
#     voltages.clear()
# 
#     for x in range(20):
#         times.append(uniform(4.14, 4.64))
#         voltages.append(uniform(-9, 7))
# 
#     times.sort()
#     acoustic_power.append(times)
#     acoustic_power.append(voltages)
# 
#     file_saver.store_measure_rfb_waveform(metadata, forward_power, reflected_power, acoustic_power)
# 
# 
# def main():
#     from Utilities.data_structures import TestData
# 
#     test_data = TestData()
#     test_data.serial_number = 'GH1214'
#     test_data.script_log = []
#     test_data.script_log.append(["", "test", "log", ""])
# 
#     metadata = dict()
#     metadata['element_number'] = 1
#     metadata['axis'] = "Th"
#     metadata['waveform_number'] = "Theta000"
#     metadata['serial_number'] = 'GH1214'
#     metadata['version'] = 1.0
#     metadata['X'] = 0.750
#     metadata['Theta'] = -171.198
#     metadata['calibration_frequency_(MHz)'] = '4'
#     metadata['source_signal_amplitude_(mVpp)'] = '50'
#     metadata['source_signal_type'] = 'Toneburst'
#     metadata['num_cycles'] = 0
# 
#     file_saver = FileSaver(config=None, test_data=test_data)
#     file_saver.copy_system_info()
#     test_store_find_element_waveform(file_saver=file_saver)
#     distances = range(100)
#     vsi = range(100)
#     file_saver.save_find_element_profile(metadata=metadata, distances=distances, vsi=vsi)
#     file_saver.save_frequency_sweep()
#     fw_power = [range(100), range(1, 101)]
#     ref_power = [range(100, 200), range(101, 201)]
#     acou_power = [range(200, 300), range(301, 401)]
#     file_saver.store_measure_rfb_waveform(metadata=metadata, forward_power=fw_power, reflected_power=ref_power,
#                                              acoustic_power=acou_power)
#     file_saver.save_test_results_summary_and_log(test_data=test_data)
# 
# if __name__ == '__main__':
#     main()
