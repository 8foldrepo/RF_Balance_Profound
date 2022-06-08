import logging
import os
import shutil
from datetime import datetime
from statistics import mean

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
from Utilities.rfb_data_logger import RFBDataLogger
from Utilities.useful_methods import log_msg, check_directory, create_test_results_summary_file
from data_structures.rfb_data import RFBData
from data_structures.test_data import TestData
from data_structures.variable_containers import FileMetadata, FrequencyRange
from definitions import ROOT_DIR

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger("wtf_log")
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode="w")
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
        """Creates the folder structure for a UA test (defaults to the results directory in the config)"""
        self.test_data = test_data
        self.create_results_folder()
        self.create_subfolders()
        self.copy_system_info()

    def create_results_folder(self):
        if self.test_data.serial_number is None or self.test_data.serial_number == "":
            self.folder_name = "No_Serial_Provided-" + self.test_data.test_date_time
        else:
            self.folder_name = self.test_data.serial_number + "-" + self.test_data.test_date_time
        results_path = os.path.join(self.config['Paths']['UA results root directory'], self.folder_name)
        # Retrieve the path of the "results" directory from the yaml file and create it if it does not exist
        self.results_dir = check_directory(results_path)

    def create_subfolders(self):
        if self.results_dir is None:
            self.log(level='error', message='Could not create subfolders before results folder, check function call')
            return

        log_files_path = os.path.join(self.results_dir, "Log files")
        self.log_files_dir = check_directory(log_files_path)

        power_data_path = os.path.join(self.results_dir, "Power data")
        self.power_data_path = check_directory(power_data_path)

        waveform_data_path = os.path.join(self.results_dir, "Waveform data")
        self.waveform_data_path = check_directory(waveform_data_path)
        self.directories_created = True

    def copy_system_info(self):
        """Copies the system info file into the results directory"""
        if self.log_files_dir is None:
            self.log(level='error', message='Could save config, log_files_dir does not exist')

        system_info_file = os.path.join(ROOT_DIR, "systeminfo.ini")
        if not os.path.exists(system_info_file):
            self.log(level='Error', message='Could not store system info to results folder')
            self.log(level='Error', message=f'systeminfo.ini was not found in {ROOT_DIR}')
            return

        destination_path = os.path.join(self.log_files_dir, "SystemHardware.log")
        shutil.copyfile(src=system_info_file, dst=destination_path)

    def save_test_results_summary_and_log(self, test_data: TestData) -> None:
        """Save the test data (shared with the manager) to the "results" folder in the form of a results summary"""
        if not test_data:  # if dictionary is empty return
            self.log(level="error", message="No results to save")
            return

        self.test_data = test_data

        path = os.path.join(self.results_dir, "Results Summary.txt")

        self.log(f"Saving results summary to: {path}")

        create_test_results_summary_file(self.test_data, path)
        self.save_log_file(self.test_data.script_log)

    # turn a 2d list into a .log file (a text file with a different extension

    def save_log_file(self, log_table: list = None):
        """saves the 2d list called log_table to a .log file. defaults to self.test_data if none is provided"""
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

        f = open(path, "w")
        for x in range(len(log_table)):
            f.write("\t".join(log_table[x]))
            f.write("\n")
        f.close()

    def store_waveform(self, metadata: FileMetadata, times, voltages,
                       storage_location, filename_stub):  # assume single array every time

        if storage_location != '':
            try:
                path = check_directory(
                    os.path.join(
                        storage_location, self.folder_name, 'ElementScans',
                        f"E{metadata.element_number:02}")
                )
            except PermissionError:
                path = check_directory(
                    os.path.join(
                        self.waveform_data_path, 'ElementScans',
                        f"E{metadata.element_number:02}")
                )
        else:
            path = check_directory(
                os.path.join(
                    self.waveform_data_path, 'ElementScans',
                    f"E{metadata.element_number:02}")
            )

        with open(os.path.join(path, f"{filename_stub}{metadata.element_number:02}_{metadata.axis}_"
                                     f"{metadata.waveform_number}.txt"), 'w+') as file:
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
            file.write('Label=""\n')
            file.write(f'X Data Type="{metadata.x_units_str}"\n')
            file.write(f'Y Data Type="{metadata.y_units_str}"\n')
            file.write("[Data]\n")
            file.write("Format=\"Cols arranged <X0>, <Y0>, <Uncertainty0> ... <Xn>, <Yn>, <Uncertaintyn>\"\n")
            file.write("Comment=\">>>>Data arrays start here<<<<\"\n")

            if len(times) != len(voltages):
                # self.log(level="error", message=f"length of times = {len(times)} ;
                # length of voltages = {len(voltages)}
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
    # todo: add a more specific filename and match the format of the example files
    def store_measure_rfb_waveform_csv(
            self,
            element_number,
            ua_serial_number,
            freq_mhz: float,
            diameter_mm: float,
            propagation_distance_mm: float,
            T_decC: float,
            UC_percent: float,
            power_ratio: float,
            g_mpersecsqrd: float,
            cal_fact,
            power_on_w: list,
            power_off_w: list,
            cumulative_results: list,
            threshold: float,
            offset_s: float,
            absorption: list,
            transducer_size: list,
            focusing: list,
            absorb_trans_times: list,
            transition_amps: list,
            raw_data: list,
            frequency_range: FrequencyRange,
            storage_location: str
    ):
        points = len(power_on_w)

        if storage_location != '':
            try:
                path = check_directory(
                    os.path.join(
                        storage_location, self.folder_name, "EfficiencyTest", f"E{element_number:02}"
                    )
                )
            except PermissionError:
                path = check_directory(
                    os.path.join(
                        self.power_data_path, "EfficiencyTest", f"E{element_number:02}"
                    )
                )
        else:
            path = check_directory(
                os.path.join(
                    self.power_data_path, "EfficiencyTest", f"E{element_number:02}"
                )
            )

        if frequency_range == FrequencyRange.high_frequency:
            file_path = os.path.join(path, f"E{element_number:02}_HFpower.csv")
        else:
            file_path = os.path.join(path, f"E{element_number:02}_LFpower.csv")

        self.log(f"Saving efficiency test data to: {file_path}")
        file = open(file_path, "w+")
        file.write("System Data\n")
        file.write(
            "Transducer,Freq (MHz),Diameter (mm),Geom Focal Length (mm),Propagation Distance (mm),Date,Time\n")

        date = datetime.now().strftime("%x")
        time = datetime.now().strftime("%I:%M %p")

        file.write(
            f'{ua_serial_number},{"%.6f" % freq_mhz},{"%.6f" % diameter_mm},Inf,{"%.6f" % propagation_distance_mm},'
            f'{date},{time}\n\n')

        file.write("Calibration Info\n")
        file.write("T (degC),UC (%),Power Ratio,g (m/s^2),Cal Fact\n")
        file.write(
            f'{"%.6f" % T_decC},{"%.6f" % UC_percent},{"%.6f" % power_ratio},{"%.6f" % g_mpersecsqrd} s^-2,'
            f'{"%.6f" % cal_fact} s^-3 m^2\n\n')

        file.write("Measurements\n")
        file.write("Points\n")
        file.write(f"{points}\n")
        file.write("Power On (W),Power Off (W)\n")

        if len(power_off_w) != len(power_on_w):
            self.log(
                "error: length of power_off_w and power_on_w unequal in method store_measure_rfb_waveform_csv, "
                "skipping over writing these")
        else:
            for x in range(points):
                file.write(f'{"%.6f" % power_on_w[x]},{"%.6f" % power_off_w[x]}\n')

        file.write("Cumulative Results\n")
        file.write(",Power On (W),Power Off (W),Combined\n")
        # cumulative_results[0] = Power (W), [1] = Random UC (%), [2] = Total UC (%)
        # sublist [0] = Power On (W), [1] = Power Off (W), [2] = Combined
        try:
            file.write(
                f'Power (W),{"%.6f" % cumulative_results[0][0]},{"%.6f" % cumulative_results[0][1]},'
                f'{"%.6f" % cumulative_results[0][2]}\n')

            file.write(
                f'Random UC (%),{"%.6f" % cumulative_results[1][0]},{"%.6f" % cumulative_results[1][1]},'
                f'{"%.6f" % cumulative_results[1][2]}\n')
            file.write(
                f'Total UC (%),{"%.6f" % cumulative_results[2][0]},{"%.6f" % cumulative_results[2][1]},'
                f'{"%.6f" % cumulative_results[2][2]}\n\n')
        except IndexError:
            self.log("Cumulative results could not be accessed, skipping log step", "error")

        file.write("Data Analysis\n")
        file.write("Threshold,Offset (s)\n")
        file.write(f'{"%.6f" % threshold},{"%.6f" % offset_s}\n\n')

        file.write("Absorption,Transducer Size,Focussing\n")
        file.write(
            f"{absorption[0]}, {transducer_size[0]}, {focusing[0]}\n"
        )  # should be str of either 'on' or 'off'
        file.write(
            f'{"%.6f" % absorption[1]}, {"%.6f" % transducer_size[1]}, {"%.6f" % focusing[1]}\n'
        )  # should be floats
        file.write("Transition Times (s)\n")
        file.write("StartOn,EndOn,StartOff,EndOff\n")

        # matches number of points to start on, end on, start off, and end off in absorb_trans_focus_times 2D list
        # absorb_trans_focus_times[0] = start on, [1] = end on, [2] = start off, [3] = end off
        if points == len(absorb_trans_times[0]) == len(absorb_trans_times[1]) == len(absorb_trans_times[2]) == len(
                absorb_trans_times[3]):
            for x in range(points):
                file.write(
                    f'{"%.6f" % absorb_trans_times[0][x]},{"%.6f" % absorb_trans_times[1][x]},'
                    f'{"%.6f" % absorb_trans_times[2][x]},{"%.6f" % absorb_trans_times[3][x]}\n')
        else:
            self.log('error: length mismatch between points parameter and absorb_trans_focus_times start/end '
                     'lists in store_measure_rfb_waveform_csv in FileSaver.py, skipping over this section')

        file.write("\nTransition Amp\n")
        file.write("StartOn,EndOn,StartOff,EndOff\n")

        if points == len(transition_amps[0]) == len(transition_amps[1]) == len(transition_amps[2]) == len(
                transition_amps[3]):
            for x in range(points):
                file.write(f'{"%.6f" % transition_amps[0][x]},{"%.6f" % transition_amps[1][x]},'
                           f'{"%.6f" % transition_amps[2][x]},{"%.6f" % transition_amps[3][x]}\n')
        else:
            self.log(
                f"error: length mismatch between points ({points}) parameter and transition_amp_times start/end lists "
                f"({len(transition_amps[0])}, {len(transition_amps[1])}, "
                f"{len(transition_amps[2])}, {len(transition_amps[3])}) "
                f"in store_measure_rfb_waveform_csv in FileSaver.py, skipping over this section")

        file.write("\nRaw Data\n")
        file.write("Time (s),Mass (mg),Acoustic Power (W), Pf(W), Pr(W)\n")
        for x in range(min(len(raw_data[0]), len(raw_data[1]), len(raw_data[2]), len(raw_data[3]), len(raw_data[4]))):
            time_s = "%.6f" % raw_data[0][x]
            mass_mg = "% .6f" % raw_data[1][x]
            ac_pow_w = "%.6f" % raw_data[2][x]
            fw_pow_w = "%.6f" % raw_data[3][x]
            rf_pow_w = "%.6f" % raw_data[4][x]
            file.write(f"{time_s},{mass_mg},{ac_pow_w},{fw_pow_w},{rf_pow_w}\n")
        file.close()

    def save_find_element_profile(self, metadata, positions, vsi_values,
                                  storage_location, filename_stub="FindElement") -> bool:
        if storage_location != '' and storage_location is not None:
            try:
                path = check_directory(os.path.join(storage_location, self.folder_name, "ElementScans",
                                                    f"E{metadata.element_number:02}"))
            except PermissionError:
                path = check_directory(os.path.join(self.waveform_data_path, "ElementScans",
                                                    f"E{metadata.element_number:02}"))
        else:
            path = check_directory(
                os.path.join(self.waveform_data_path, "ElementScans", f"E{metadata.element_number:02}")
            )

        full_path = os.path.join(path, f"{filename_stub}{metadata.element_number:02}_{metadata.axis}__UMSProfile.txt")

        with open(full_path, "w+") as file:
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
            file.write('Label=""\n')
            file.write(f'X Data Type="{metadata.x_units_str}"\n')
            file.write(f'Y Data Type="{metadata.y_units_str}"\n')
            file.write("[Data]\n")
            file.write(
                'Format="Cols arranged <X0>, <Y0>, <Uncertainty0> ... <Xn>, <Yn>, <Uncertaintyn>"\n'
            )
            file.write('Comment=">>>>Data arrays start here<<<<"\n')

            if len(positions) != len(vsi_values):
                # self.log(level="error", message=f"length of distances = {len(distances)} ; length of vsi = {len(vsi)}
                # mismatch in store_find_element_waveform()")
                print(
                    f"length of distances = {len(positions)} ; length of vsi = {len(vsi_values)} size mismatch in "
                    f"store_find_element_waveform()"
                )
                file.close()
                return False
            else:
                for x in range(len(positions)):
                    formatted_time = "{:.6e}".format(positions[x])
                    formatted_voltage = "{:.6e}".format(vsi_values[x])
                    file.write(f"{formatted_time}\t{formatted_voltage}\t0.000000E+0\n")

    def save_frequency_sweep(self, metadata, frequencies, vsi_values, storage_location, filename_stub="FindElement"):
        if storage_location != '' and storage_location is not None:
            try:
                path = check_directory(os.path.join(storage_location, self.folder_name, "ElementScans",
                                                    f"E{metadata.element_number:02}"))
            except PermissionError:
                path = check_directory(os.path.join(self.waveform_data_path, "ElementScans",
                                                    f"E{metadata.element_number:02}"))
        else:
            path = check_directory(
                os.path.join(self.waveform_data_path, "ElementScans", f"E{metadata.element_number:02}")
            )

        full_path = os.path.join(path, f"{filename_stub}{metadata.element_number:02}_FrequencyProfile.txt", )

        with open(full_path, 'w+') as file:
            file.write(f"UASerialNumber={self.test_data.serial_number}\n")
            file.write("[File Format]\n")
            file.write(f"Version={self.config['Software_Version']}\n")
            file.write(f"# Arrays=1\n")
            file.write("[Position]\n")
            file.write(f"X={f'%.2f' % metadata.X}\n")
            file.write(f"Theta={f'%.2f' % metadata.Theta}\n")
            file.write(f"Nominal Low Frequency={f'%.2f' % metadata.nominal_low_frequency_MHz}MHz\n")
            file.write(f"Nominal High Frequency={f'%.2f' % metadata.nominal_high_frequency_MHz}MHz\n")
            file.write(f"Source Signal Amplitude={metadata.amplitude_mVpp}mVpp\n")
            file.write(f"Source Signal Type={metadata.source_signal_type}\n")
            file.write(f"# Cycles={metadata.num_cycles}\n")
            file.write("[Array 0]\n")
            file.write('Label=""\n')
            file.write(f'X Data Type="{metadata.x_units_str}"\n')
            file.write(f'Y Data Type="{metadata.y_units_str}"\n')
            file.write("[Data]\n")
            file.write('Format="Cols arranged <X0>, <Y0>, <Uncertainty0> ... <Xn>, <Yn>, <Uncertaintyn>"\n')
            file.write('Comment=">>>>Data arrays start here<<<<"\n')

            if len(frequencies) != len(vsi_values):
                # self.log(level="error", message=f"length of distances = {len(distances)} ; length of vsi = {len(vsi)}
                # mismatch in store_find_element_waveform()")
                print(
                    f"length of distances = {len(frequencies)} ; length of vsi = {len(vsi_values)} size mismatch in "
                    f"store_find_element_waveform()"
                )
            else:
                for x in range(len(frequencies)):
                    formatted_time = "{:.6e}".format(frequencies[x])
                    formatted_voltage = "{:.6e}".format(vsi_values[x])
                    file.write(f"{formatted_time}\t{formatted_voltage}\t0.000000E+0\n")

    def log(self, message, level="info"):
        log_msg(self, root_logger, message=message, level=level)

    def extract_file_data(self, rfb_logger: RFBDataLogger, rfb_data: RFBData, system_info, element: int,
                          frequency_mhz: float, threshold, offset, frequency_range, storage_location: str):
        balance_readings_mg = [value * 1000 for value in rfb_logger.balance_readings_g]
        # Time (s),Mass (mg),Acoustic Power (W), Pf(W), Pr(W)
        raw_data = [
            rfb_logger.times_s,
            balance_readings_mg,
            rfb_logger.acoustic_powers_w,
            rfb_logger.f_meter_readings_w,
            rfb_logger.r_meter_readings_w,
        ]

        absorption = ["Off", 1.000690]
        transducer_size = ["Off", 1.013496]
        focusing = ["Off", 1.000000]

        buffer = self.config["Analysis"]["samples_to_remove_at_end"]

        # transition_times_s/transition_amp_w[0] = start on, [1] = end on, [2] = start off, [3] = end off
        num_cycles = len(rfb_data.on_time_intervals_s)
        transition_times_s = [[float('nan')] * num_cycles, [float('nan')] * num_cycles, [float('nan')] * num_cycles,
                              [float('nan')] * num_cycles]
        for i in range(num_cycles):
            if i != 0:
                # Beginning of on transition
                try:
                    transition_times_s[0][i] = rfb_data.times_s[rfb_data.off_indices[i - 1][1]]
                except IndexError:
                    print("encountered index error exception 478")
                    transition_times_s[0][i] = float("NaN")  # todo: find out why IndexError is occurring here
            else:
                # Beginning of on transition
                transition_times_s[0][i] = rfb_data.times_s[rfb_data.awg_on_ray.index(True) - buffer]
            # Beginning of off transition
            transition_times_s[2][i] = rfb_data.times_s[rfb_data.on_indices[i][1]]

            transition_times_s[1][i] = rfb_data.on_time_intervals_s[i][0]  # End of on transition
            try:
                transition_times_s[3][i] = rfb_data.off_time_intervals_s[i][0]  # End of off transition
            except IndexError:
                transition_times_s[3][i] = float("NaN")
            # todo: for some reason, rfb_data.off_time_intervals_s[2][0] does not exist

        transition_amp_w = [[float('nan')] * num_cycles, [float('nan')] * num_cycles, [float('nan')] * num_cycles,
                            [float('nan')] * num_cycles]
        for i in range(num_cycles):
            if i != 0:
                # Beginning of on transition
                if 0 < i < len(rfb_data.off_indices) + 1 and i < len(transition_amp_w[0]):
                    transition_amp_w[0][i] = rfb_data.acoustic_powers_w[rfb_data.off_indices[i - 1][1]]
                else:
                    transition_amp_w[0][i] = float("NaN")
            else:
                # Beginning of on transition
                transition_amp_w[0][i] = rfb_data.acoustic_powers_w[rfb_data.awg_on_ray.index(True) - buffer]
            # Beginning of off transition
            transition_amp_w[2][i] = rfb_data.acoustic_powers_w[rfb_data.on_indices[i][1]]

            transition_amp_w[1][i] = rfb_data.acoustic_powers_w[rfb_data.on_indices[i][0]]  # End of on transition
            try:
                transition_amp_w[3][i] = rfb_data.acoustic_powers_w[rfb_data.off_indices[i][0]]  # End of off transition
            except IndexError:
                transition_amp_w[3][i] = float("NaN")
            # todo: for some reason, line in try block above hits index error exception

        power_on_w = transition_amp_w[1]
        power_off_w = transition_amp_w[2]

        if len(power_on_w) > 0 and len(power_off_w) > 0:
            cumulative_results = (
                [[mean(power_on_w), mean(power_off_w),
                  rfb_data.acoustic_power_on_mean],
                 [rfb_data.p_on_rand_unc, rfb_data.p_on_rand_unc, rfb_data.p_on_rand_unc],
                 [rfb_data.p_on_total_unc, rfb_data.p_on_total_unc, rfb_data.p_on_total_unc]]
            )
        else:
            self.log(level='error', message='Missing power data, setting cumulative_results list to empty list')
            cumulative_results = []  # needed or else referenced before assignment error is raised

        # todo: check that p_on_rand_unc is the one we want
        self.store_measure_rfb_waveform_csv(
            element_number=element,
            ua_serial_number=self.test_data.serial_number,
            freq_mhz=frequency_mhz,
            diameter_mm=float(
                system_info["Hydrophone system"]["Hydrophone Diameter"].split(" ")[0].replace('"', "")
            ),
            propagation_distance_mm=15.000000,
            T_decC=rfb_data.water_temperature_c,
            UC_percent=float(rfb_data.p_on_rand_unc),
            power_ratio=1.000000,
            g_mpersecsqrd=9.810000,
            cal_fact=14600.571062,
            power_on_w=power_on_w,
            power_off_w=power_off_w,
            cumulative_results=cumulative_results,
            threshold=threshold,
            offset_s=offset,
            absorption=absorption,
            transducer_size=transducer_size,
            focusing=focusing,
            absorb_trans_times=transition_times_s,
            transition_amps=transition_amp_w,
            raw_data=raw_data,
            frequency_range=frequency_range,
            storage_location=storage_location
        )
