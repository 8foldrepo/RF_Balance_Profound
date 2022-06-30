from pprint import pformat
from typing import List, Union
from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from Utilities.load_config import load_configuration
from Utilities.useful_methods import mean_of_non_none_values
from data_structures.variable_containers import FrequencyRange


class TestData(QObject):
    """
    A class dedicated to organizing the results of an element efficiency test for
    presentation, analysis, modularization, and to increase the project's compactness
    """
    # connected to results_tab.populate_results_table() in main window class
    show_results_summary = QtCore.pyqtSignal(list)
    show_script_log = QtCore.pyqtSignal(list)  # connected to results_tab.populate_log_table() in main window class

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
    angle_average: float

    def __init__(self, config=None):
        super().__init__()

        self.config = config
        if config is None:
            self.config = load_configuration()

        self.set_blank_values()

    def set_blank_values(self) -> None:
        """
        Initializes the "results" table list as well as variables
        to be used in the final formulation of the results data
        """
        from datetime import datetime

        # add formatted date and initialize variables
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

    def update_ua_common_frequencies(self, low_frequency_MHz: float, high_frequency_MHz: float) -> None:
        """
        Updates the fields for UA common low frequency and high frequency in the class variables as well as the
        results summary, and also emit the results summary to the UI
        """
        self.low_frequency_MHz = low_frequency_MHz
        self.high_frequency_MHz = high_frequency_MHz
        self.results_summary[10][3] = "%.2f" % self.low_frequency_MHz
        self.results_summary[10][5] = "%.2f" % self.high_frequency_MHz
        self.show_results_summary.emit(self.results_summary)

    def set_max_position(self, axis: str, element: int, max_position: float) -> None:
        """
        The list of strings should have length 4, and the number of empty
        strings at the beginning corresponds to the indentation level
        """

        # update element position
        if axis == "X":
            self.results_summary[element - 1][1] = "%.2f" % max_position
        else:
            self.results_summary[element - 1][2] = "%.2f" % max_position
            # (self.config['WTF_PositionParameters']['ThetaHomeCoord']
            # -  self.config['WTF_PositionParameters'][
            #      'ThetaHydrophoneCoord']))
        self.show_results_summary.emit(self.results_summary)

    def update_results_summary_with_efficiency_results(self, frequency_range: FrequencyRange, element: int,
                                                       frequency_hz: float, efficiency_percent: float,
                                                       reflected_power_percent: float, forward_power_max: float,
                                                       water_temperature_c: float, test_result: str, comment: str):
        """
        Add efficiency test data to the results_summary table, and also emit them as a signal (to display them in the
        results tab
        """
        if frequency_range == FrequencyRange.high_frequency:
            # High frequency
            self.results_summary[element - 1][5] = "%.2f" % (frequency_hz / 1000000)
            # HF efficiency (%)
            self.results_summary[element - 1][11] = "%.1f" % efficiency_percent
            self.results_summary[element - 1][12] = "%.1f" % reflected_power_percent
            self.results_summary[element - 1][13] = "%.1f" % forward_power_max
            self.results_summary[element - 1][14] = "%.1f" % water_temperature_c
            if test_result.upper() == 'FAIL':
                comment = f"High frequency test failed: {comment}"
        else:  # Default to low frequency
            # Low Frequency
            self.results_summary[element - 1][3] = "%.2f" % (frequency_hz / 1000000)
            # LF efficiency (%)
            self.results_summary[element - 1][7] = "%.1f" % efficiency_percent
            self.results_summary[element - 1][8] = "%.1f" % reflected_power_percent
            self.results_summary[element - 1][9] = "%.1f" % forward_power_max
            self.results_summary[element - 1][10] = "%.1f" % water_temperature_c
            if test_result.upper() == 'FAIL':
                comment = f"Low frequency test failed: {comment}"

        # If the element already failed do not overwrite the entry
        if self.results_summary[element - 1][15].upper() != 'FAIL':
            self.results_summary[element - 1][15] = test_result.upper()

        self.update_comment(element, comment)

        self.show_results_summary.emit(self.results_summary)

    def update_comment(self, element, comment):
        """Append the comment to the existing comment if there is one and they are different"""
        if len(self.results_summary[element - 1][16]) > 0 and len(comment) != 0 and \
                comment not in self.results_summary[element - 1][16]:
            self.results_summary[element - 1][16] = self.results_summary[element - 1][16] + ' | ' + comment
        elif len(comment) > 0:
            self.results_summary[element - 1][16] = comment

    def update_results_summary_with_frequency_sweep(self, frequency_range: FrequencyRange, element: int,
                                                    frequency_mHz: float, vsi: float, units_str: str, ):
        """Add frequency sweep data to the results_summary table"""
        if 'RMS'.upper() in units_str.upper():
            self.results_summary[element - 1][0] = 'Vrms'
        else:
            self.results_summary[element - 1][0] = 'V^2s'

        if frequency_range == FrequencyRange.high_frequency:
            # High frequency
            self.results_summary[element - 1][5] = "%.2f" % frequency_mHz
            self.results_summary[element - 1][6] = "%.2f" % vsi
            # HF efficiency (%)
        else:  # Default to low frequency
            # Low Frequency
            self.results_summary[element - 1][3] = "%.2f" % (frequency_mHz / 1000000)
            self.results_summary[element - 1][4] = "%.2f" % vsi
            # LF efficiency (%)
        self.show_results_summary.emit(self.results_summary)

    def calculate_angle_average(self, measured_element_r_coords: List[Union[float, None]]):
        """Calculates the average of all measured element theta positions from find element"""
        angle_average = mean_of_non_none_values(measured_element_r_coords)

        if not angle_average == float('nan'):
            self.angle_average = angle_average
        else:
            self.angle_average = -90

        self.results_summary[10][2] = '%.2f' % self.angle_average

        # update UI representation
        self.show_results_summary.emit(self.results_summary)

    def log_script(self, entry: List[str]):
        self.script_log.append(entry)
        self.show_script_log.emit(self.script_log)

    def set_pass_result(self, element: int, test_result: str) -> None:
        """
        Used in measure_element_efficiency_rfb(); simply sets the pass/fail
        value to the passed result regarding the passed element.

        :param element: the element that needs its test result updated in the class' results_summary list
        :param test_result: should be either PASS, FAIL, or DNF
        """
        # If the element already failed do not overwrite the entry
        # results_summary and element are offset by 1; 15 is the pass/fail position
        if self.results_summary[element - 1][15].upper() != 'FAIL':
            self.results_summary[element - 1][15] = test_result.upper()

        # update UI representation
        self.show_results_summary.emit(self.results_summary)

    def __repr__(self):
        to_return = 'TestData\n'
        to_return += f'script_log (type: {type(self.script_log)} length: {len(self.script_log)}): {pformat(self.script_log)}\n'
        to_return += f'results_summary (type: {type(self.results_summary)} length: {len(self.results_summary)}):' \
                     f' {pformat(self.results_summary)}\n'
        to_return += '\n'
        to_return += f'test_date_time (type: {type(self.test_date_time)}): {self.test_date_time}\n'
        to_return += f'software_version (type: {type(self.software_version)}): {self.software_version}\n'
        to_return += f'test_comment (type: {type(self.test_comment)}): {self.test_comment}\n'
        to_return += f'serial_number (type: {type(self.serial_number)}): {self.serial_number}\n'
        to_return += f'operator_name (type: {type(self.operator_name)}): {self.operator_name}\n'
        to_return += f'script_name (type: {type(self.script_name)}): {self.script_name}\n'
        to_return += f'script_log (type: {type(self.script_log)}): {self.script_log}\n'
        to_return += f'low_frequency_MHz (type: {type(self.low_frequency_MHz)}): {self.low_frequency_MHz}\n'
        to_return += f'high_frequency_MHz (type: {type(self.high_frequency_MHz)}): {self.high_frequency_MHz}\n'
        to_return += f'hardware_code (type: {type(self.hardware_code)}): {self.hardware_code}\n'
        to_return += f'write_result (type: {type(self.write_result)}): {self.write_result}\n'
        to_return += f'skip_write_to_ua (type: {type(self.skip_write_to_ua)}): {self.skip_write_to_ua}\n'
        to_return += f'schema (type: {type(self.schema)}): {self.schema}\n'
        to_return += f'angle_average (type: {type(self.angle_average)}): {self.angle_average}\n'

        return to_return

    def element_failed(self, element_number: int, description: str) -> None:
        self.results_summary[element_number - 1][15] = 'FAIL'
        self.update_comment(element_number, description)
