from typing import List
from PyQt5.QtCore import pyqtSignal, QObject

from data_structures.variable_containers import FrequencyRange


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
    skip_write_to_ua: bool
    schema: str

    def __init__(self):
        super().__init__()
        self.set_blank_values()

    def set_blank_values(self):
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
        self.write_result = None
        self.skip_write_to_ua = False
        self.schema = '1'
        self.angle_average = -90
        hf = "NaN"
        lf = "NaN"

        # Create results_summary table
        table = list([None] * 13)

        # Default values, will be updated during test
        table[0] = ["Element_01", "0", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[1] = ["Element_02", "5", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[2] = ["Element_03", "10", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[3] = ["Element_04", "15", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[4] = ["Element_05", "20", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[5] = ["Element_06", "25", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[6] = ["Element_07", "30", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[7] = ["Element_08", "35", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[8] = ["Element_09", "40", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[9] = ["Element_10", "45", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]
        table[10] = ["UA Common", "NaN", "-90", lf, "NaN", hf] + ["NaN"] * 9 + ["NO TEST", ""]

        elements_with_manual_lf = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        elements_with_manual_hf = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]

        # Todo: add ability to set manual frequencies per element
        table[11] = elements_with_manual_lf
        table[12] = elements_with_manual_hf

        self.results_summary = table

    def set_max_position(self, axis: str, element: int, max_position: float):
        """
            The list of strings should have length 4, and the number of empty strings at the beginning
            corresponds to the indentation level
        """
        # update element position
        if axis == "X":
            self.results_summary[element - 1][1] = "%.2f" % max_position
        else:
            self.results_summary[element - 1][2] = "%.2f" % max_position
        self.show_results_summary.emit(self.results_summary)

    def update_results_summary_with_efficiency_results(
            self,
            frequency_range: FrequencyRange,
            element: int,
            frequency_Hz: float,
            efficiency_percent: float,
            reflected_power_percent: float,
            forward_power_max: float,
            water_temperature_c: float,
            test_result: str,
            comment: str
    ):
        """Add efficiency test data to the results_summary table, and also emit them as a signal (to display them in the
            results tab"""
        if frequency_range == FrequencyRange.high_frequency:
            # High frequency
            self.results_summary[element - 1][5] = "%.2f" % (frequency_Hz / 1000000)
            # HF efficiency (%)
            self.results_summary[element - 1][11] = "%.0f" % efficiency_percent
            self.results_summary[element - 1][12] = "%.1f" % reflected_power_percent
            self.results_summary[element - 1][13] = "%.1f" % forward_power_max
            self.results_summary[element - 1][14] = "%.1f" % water_temperature_c
            if test_result.upper() == 'FAIL':
                comment = f"High frequency test failed: {comment}"
        else:  # Default to low frequency
            # Low Frequency
            self.results_summary[element - 1][3] = "%.2f" % (frequency_Hz / 1000000)
            # LF efficiency (%)
            self.results_summary[element - 1][7] = "%.0f" % efficiency_percent
            self.results_summary[element - 1][8] = "%.1f" % reflected_power_percent
            self.results_summary[element - 1][9] = "%.1f" % forward_power_max
            self.results_summary[element - 1][10] = "%.1f" % water_temperature_c
            if test_result.upper() == 'FAIL':
                comment = f"Low frequency test failed: {comment}"

        # If the element already failed do not overwrite the entry
        if self.results_summary[element - 1][15].upper() != 'FAIL':
            self.results_summary[element - 1][15] = test_result.upper()
            self.results_summary[element - 1][16] = comment

        self.show_results_summary.emit(self.results_summary)

    def update_results_summary_with_frequency_sweep(self, frequency_range: FrequencyRange, element: int,
                                                    frequency_Hz: float, vsi: float, units_str: str, ):
        """Add frequency sweep data to the results_summary table"""
        if 'RMS'.upper() in units_str.upper():
            self.results_summary[element - 1][0] = 'Vrms'
        else:
            self.results_summary[element - 1][0] = 'V^2s'

        if frequency_range == FrequencyRange.high_frequency:
            # High frequency
            self.results_summary[element - 1][5] = "%.2f" % (frequency_Hz / 1000000)
            self.results_summary[element - 1][6] = "%.2f" % (vsi)
            # HF efficiency (%)
        else:  # Default to low frequency
            # Low Frequency
            self.results_summary[element - 1][3] = "%.2f" % (frequency_Hz / 1000000)
            self.results_summary[element - 1][4] = "%.2f" % (vsi)
            # LF efficiency (%)
        self.show_results_summary.emit(self.results_summary)

    def calculate_angle_average(self):
        angle_sum = 0
        count = 0
        for i in range(10):
            angle_sum = angle_sum + float(self.results_summary[i][2])
            count = count + 1

        self.angle_average = angle_sum / count
        self.results_summary[10][2] = str(self.angle_average)

        # update UI representation
        self.show_results_summary.emit(self.results_summary)

    def log_script(self, entry: List[str]):
        self.script_log.append(entry)
        self.show_script_log.emit(self.script_log)

    def set_pass_result(self, element, test_result):
        # If the element already failed do not overwrite the entry
        if self.results_summary[element - 1][15].upper() != 'FAIL':
            self.results_summary[element - 1][15] = test_result.upper()

        # update UI representation
        self.show_results_summary.emit(self.results_summary)
