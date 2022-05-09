from typing import List
from PyQt5.QtCore import pyqtSignal, QObject
from definitions import FrequencyRange


class FileMetadata:
    element_number: int
    X: float
    Theta: float
    frequency_MHz: float
    amplitude_mVpp: float
    source_signal_type: str
    num_cycles: int
    axis: str
    waveform_number: int


class SystemInfo:
    rf_balance_sn: str
    oscilloscope_sn: str
    wtf_sn: str
    awg_sn: str
    forward_power_sn: str
    reflected_power_sn: str
    thermocouple_sn: str


class RFBData:
    element: int
    frequency_range: FrequencyRange
    water_temperature_c: float

    # Test criteria
    Pf_max: float
    Pa_max: float
    ref_limit: float

    times_s: List[float]
    # The indices of these lists math the times array 1 for 1 and each entry is a capture that occurred at that time
    f_meter_readings_w: List[float]
    r_meter_readings_w: List[float]
    acoustic_powers_w: List[float]
    balance_readings_g: List[float]
    #   Record of whether the AWG was off or on for each sample
    awg_on_ray: List[bool]

    # Instantaneous readings to be shown in the UI
    grams: float
    forward_power_w: float
    reflected_power_w: float

    # Analysis metrics of the graph as a whole
    p_on_rand_unc: float
    p_off_rand_unc: float
    p_on_total_unc: float
    p_off_total_unc: float
    p_com_rand_unc: float
    p_com_total_unc: float
    acoustic_power_off_mean: float
    acoustic_power_on_mean: float
    acoustic_power_mean: float
    forward_power_on_mean: float
    reflected_power_on_mean: float
    efficiency_percent: float
    reflected_power_percent: float
    forward_power_max: float

    def __init__(self, element:int, frequency_range:FrequencyRange, water_temperature_c:float, Pf_max:float,
                 Pa_max:float, ref_limit:float):
        self.element = element
        self.frequency_range = frequency_range
        self.water_temperature_c = water_temperature_c
        self.Pf_max = Pf_max
        self.Pa_max = Pa_max
        self.ref_limit = ref_limit

    def end_of_test_data_analysis(self):
        from Utilities.useful_methods import get_awg_on_values
        # List containing all readings while AWG was on
        acoustic_power_on_data = get_awg_on_values(self.acoustic_powers_w, self.awg_on_ray)
        # Mean acoustic power while on
        acoustic_power_on_mean = sum(acoustic_power_on_data) / len(acoustic_power_on_data)

        # List containing all readings while AWG was on
        forward_power_on_data = get_awg_on_values(self.f_meter_readings_w, self.awg_on_ray)
        # Mean acoustic power while on
        self.forward_power_on_mean = sum(forward_power_on_data) / len(forward_power_on_data)

        if self.forward_power_on_mean != 0:
            self.efficiency_percent = acoustic_power_on_mean / self.forward_power_on_mean * 100
        else:
            self.efficiency_percent = 0

        # List containing all readings while AWG was on
        reflected_power_on_data = get_awg_on_values(self.r_meter_readings_w, self.awg_on_ray)
        # Mean acoustic power while on
        self.reflected_power_on_mean = sum(reflected_power_on_data) / len(reflected_power_on_data)

        if self.forward_power_on_mean != 0:
            self.reflected_power_percent = self.reflected_power_on_mean / self.forward_power_on_mean * 100
        else:
            self.reflected_power_percent = 1

        self.forward_power_max = max(forward_power_on_data)

    # Do not call this method while a rfb_data_logger is capturing readings
    def trim_data(self):
        from Utilities.useful_methods import trim
        self.times_s, self.acoustic_powers_w, self.awg_on_ray, self.f_meter_readings_w, self.r_meter_readings_w, \
            self.balance_readings_g = trim([self.times_s, self.acoustic_powers_w, self.awg_on_ray,
                                            self.f_meter_readings_w, self.r_meter_readings_w, self.balance_readings_g])

    #Todo:
    def get_pass_result(self) -> str:
        return "Pass"

    def get_result_log_entry(self):
        return ['', "Pass/Fail test",
                                   f"Element_{self.element};Pf (W)={self.forward_power_on_mean};Pr (W)="
                                   f"{self.reflected_power_on_mean};Pa (W)={self.acoustic_power_on_mean};Efficiency (%)"
                                   f"={self.efficiency_percent};RF_Reflection (%)={self.reflected_power_percent};"
                                   f"Pf Max (W)={self.forward_power_max};WaterTemp (C)={self.water_temperature_c};"
                                   f"Test result={self.get_pass_result()};Pf Max limit (W)={self.Pf_max}",
                                   '']


class TestData(QObject):
    show_results_summary = pyqtSignal(list)
    show_script_log = pyqtSignal(list)

    script_log: List[List[str]]
    results_summary: List[List[str]]

    test_date_time: str
    software_version: str
    test_comment: str
    serial_number: str
    operator_name: str
    script_name: str
    script_log: str
    low_frequency_MHz: float
    high_frequency_MHz: float
    hardware_code: str
    write_result: bool

    def __init__(self):
        super().__init__()
        self.set_blank_values()

    def set_blank_values(self):
        super().__init__()
        from datetime import datetime

        # add formatted date
        now = datetime.now()
        formatted_date = now.strftime("%Y.%m.%d-%H.%M")
        self.test_date_time = formatted_date
        self.software_version = ""
        self.test_comment = ""
        self.serial_number = ""
        self.operator_name = ""
        self.script_name = ""
        self.script_log = list()
        self.low_frequency_MHz = float("nan")
        self.high_frequency_MHz = float("nan")
        self.hardware_code = ""
        self.results_summary = list()
        self.write_result = False
        hf = "NaN"
        lf = "NaN"

        # Create results_summary table
        table = list([None] * 13)

        # Default values, will be updated during test
        table[0] = ["Element_01", "0", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[1] = ["Element_02", "5", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[2] = ["Element_03", "10", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[3] = ["Element_04", "15", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[4] = ["Element_05", "20", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[5] = ["Element_06", "25", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[6] = ["Element_07", "30", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[7] = ["Element_08", "35", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[8] = ["Element_09", "40", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[9] = ["Element_10", "45", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]
        table[10] = ["UA Common", "NaN", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["DNF", ""]

        elements_with_manual_lf = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        elements_with_manual_hf = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]

        # Todo: add ability to set manual frequencies per element
        table[11] = elements_with_manual_lf
        table[12] = elements_with_manual_hf

        self.results_summary = table

    """
    The list of strings should have length 4, and the number of empty strings at the beginning 
    corresponds to the indentation level
    """

    def set_max_position(self, axis: str, element: int, max_position: float):
        # update element position
        if axis == "X":
            self.results_summary[element - 1][1] = "%.2f" % max_position
        else:
            self.results_summary[element - 1][2] = "%.2f" % max_position
        self.show_results_summary.emit(self.results_summary)

    """Add efficiency test data to the results_summary table, and also emit them as a signal (to display them in the 
    results tab"""

    def update_results_summary_with_efficiency_results(
            self,
            high_frequency: bool,
            element: int,
            frequency_Hz: float,
            efficiency_percent: float,
            reflected_power_percent: float,
            forward_power_max: float,
            water_temperature_c: float,
    ):
        if high_frequency:
            # High frequency
            self.results_summary[element - 1][5] = "%.2f" % (frequency_Hz / 1000000)
            # HF efficiency (%)
            self.results_summary[element - 1][11] = "%.0f" % efficiency_percent
            self.results_summary[element - 1][12] = "%.1f" % reflected_power_percent
            self.results_summary[element - 1][13] = "%.1f" % forward_power_max
            self.results_summary[element - 1][14] = "%.1f" % water_temperature_c
        else:  # Default to low frequency
            # Low Frequency
            self.results_summary[element - 1][3] = "%.2f" % (frequency_Hz / 1000000)
            # LF efficiency (%)
            self.results_summary[element - 1][7] = "%.0f" % efficiency_percent
            self.results_summary[element - 1][8] = "%.1f" % reflected_power_percent
            self.results_summary[element - 1][9] = "%.1f" % forward_power_max
            self.results_summary[element - 1][10] = "%.1f" % water_temperature_c
        self.show_results_summary.emit(self.results_summary)

    def calc_angle_average(self):
        angle_sum = 0
        count = 0
        for i in range(10):
            angle_sum = angle_sum + float(self.results_summary[i][2])
            count = count + 1

        angle_average = angle_sum / count
        self.results_summary[10][2] = str(angle_average)
        self.show_results_summary.emit(self.results_summary)

    def log_script(self, entry: List[str]):
        self.script_log.append(entry)
        self.show_script_log.emit(self.script_log)
