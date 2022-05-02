import collections.abc
import os

import numpy as np

from Utilities.variable_containers import TestData


def create_coord_rays(coords: str, ax_letters: list):
    """
    Inputs:
    A string containing comma delimited coordinates, some of which may be empty, for example ,,3,2
    A list containing the letters of all axes. The length must be greater than the number of commas. Ex: [X,Y,Z,R]
    Output:
    A list containing the axis letters of the coordinates provided, and a list of equal length containing the
    coordinates. With the given inputs the output should be axes: [Z,R] coords [3,2]
    """
    axes = list()
    coords = coords.split(',')
    for i in range(len(coords)):
        if not coords[i] == '':
            axes.append(ax_letters[i])

    # Remove empty elements
    coords = list(filter(lambda val: val != '', coords))
    return axes, coords


def get_element_distances(element_1_index, element_pitch):
    """Generate presumed x positions for all elements given the pitch and the position of element 1, used by manager"""
    # length of 11, so index can equal element number. item zero will remain 'nan' and will cause errors if used
    element_coords = [None, None, None, None, None, None, None, None, None, None, None]
    for i in range(10):
        offset = i * element_pitch
        element_coords[i + 1] = element_1_index + offset

    return element_coords


def generate_calibration_data(test_data: TestData):
    """Create UA calibration data compatible with the UA_Interface_Box class given test_data from the manager class"""
    # Todo: populate this array according to the test_data
    calibration_data = {
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


# Inverse of create coord_rays
def create_comma_string(axes: list, coords: list, ax_letters: list):
    answer = ""
    for i in range(len(ax_letters)):
        if ax_letters[i] in axes:
            index = axes.index(ax_letters[i])
            if len(coords) == len(axes):
                answer = answer + str((coords[index]))

        answer = answer + ","
    return answer


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def printList(self, list2):
    for x in range(len(list2)):
        print(list2[x])


def printList2(self, list2):
    print(str(list2)[1:-1])


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def check_directory(path):
    # Check whether the specified path exists or not
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)
    return path


def precision_round(number, digits=3):
    power = "{:e}".format(number).split("e")[1]
    return round(number, -(int(power) - digits))


def bound(x):
    if -.001 < x < .001:
        x = 0
    return x


def unique(list):
    # intilize a null list
    unique_list = []

    # traverse for all elements
    for x in list:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)

    return unique_list


# Additional feature: add smart transition detection
def get_awg_on_values(acoustic_power_trace_w, awg_on_ray):
    if len(acoustic_power_trace_w) == 0:
        return [float('nan')]
    if len(acoustic_power_trace_w) != len(awg_on_ray):
        return [float('nan')]
    acoustic_power_on_data = list()

    for i in range(len(acoustic_power_trace_w)):
        if awg_on_ray[i]:
            acoustic_power_on_data.append(acoustic_power_trace_w[i])

    return acoustic_power_on_data


# Additional feature: add smart transition detection
def get_awg_off_values(acoustic_power_trace_w, awg_on_ray):
    if len(acoustic_power_trace_w) == 0:
        return [float('nan')]
    if len(acoustic_power_trace_w) != len(awg_on_ray):
        return [float('nan')]

    acoustic_power_off_data = list()

    for i in range(len(acoustic_power_trace_w)):
        if not awg_on_ray[i]:
            acoustic_power_off_data.append(acoustic_power_trace_w[i])

    return acoustic_power_off_data


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.edit_menu():
            child.edit_menu().setParent(None)


def listToRay(xCoords, yCoords, zCoords, Intensity):
    unique_xCoords = unique(list=xCoords)
    unique_yCoords = unique(list=yCoords)
    unique_zCoords = unique(list=zCoords)

    coordinates = (unique_xCoords, unique_yCoords, unique_zCoords)
    map = np.zeros((len(unique_xCoords), len(unique_yCoords), len(unique_zCoords)))

    for i in range(len(xCoords)):
        x = unique_xCoords.index(xCoords[i])
        y = unique_yCoords.index(yCoords[i])
        z = unique_zCoords.index(zCoords[i])

        map[x][y][z] = Intensity[i]

    return map, coordinates


# Searches from current directory to grandparent directory for the specified file
def search_for(filename):
    # This program configures all rigols to settings from a csv file
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.split(current_directory)[0]  # Repeat as needed
    grandparent_directory = os.path.split(parent_directory)[0]  # Repeat as needed

    file_path = os.path.join(current_directory, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(parent_directory, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(grandparent_directory, filename)

    return file_path


"""Saves the dictionary containing test info to a specified path, formatted as a results summary"""


def create_test_results_summary_file(test_data: TestData, path):
    f = open(path, "w")

    f.write(test_data.serial_number + '-' + test_data.test_date_time + '\n')
    f.write("Test operator\t" + test_data.operator_name + '\n')
    f.write("Comment\t" + test_data.test_comment + '\n')
    f.write("Software Version\t" + test_data.software_version + '\n')
    f.write("Script\t" + test_data.script_name + '\n')
    if test_data.write_result:
        f.write("UA Write\tOK\n")
    else:
        f.write("UA Write\tFAIL\n")
    f.write("UA hardware code\t" + test_data.hardware_code + '\n')
    f.write('\n')  # empty line
    f.write(
        "\tX\tTheta\tLF (MHz)\tLF.VSI (V^2s)\tHF (MHz)\tHF.VSI (V^2s)\tLF.Eff (%)\tLF.Rfl (%)\tLF.Pf(max) (W)\t"
        "LF.WTemp (degC)\tHF.Eff (%)\tHF.Rfl (%)\tHF.Pf(max) (W)\tHF.WTemp (degC)\tElement result\t"
        "Failure description\n")

    element_data_list = test_data.results_summary
    for x in range(len(element_data_list)):
        if 0 <= x <= 10:  # for all the element lines and the UA Common line
            if x == 10:
                f.write('\n')  # there are empty lines around "UA Common" row
            f.write('\t'.join(element_data_list[x]))
            f.write('\n')
        if x == 11:  # for the elements with manual LF...
            f.write('\n')
            f.write('Elements with manual LF\t' + ','.join(element_data_list[x]))
            f.write('\n')
        if x == 12:  # for the elements with manual HF...
            f.write('Elements with manual HF\t' + ','.join(element_data_list[x]))


def log_msg(self, root_logger, message: str, level: str = None) -> None:
    from PyQt5.QtCore import QThread
    """
    Convenience function to log messages in a compact way with useful info.

        Parameters:
            level (str): A string indicating the logger level, can be either
            'info', 'debug' or 'error'
            message (str): A string that contains the message to be logged

        Returns:
            None
    """

    thread_name = QThread.currentThread().objectName()
    log_entry = f"[{type(self).__name__}] [{thread_name}] : {message}"
    if level == 'debug':
        root_logger.debug(log_entry)
    elif level == 'error':
        root_logger.error(log_entry)
    elif level == 'warning':
        root_logger.warning(log_entry)
    else:
        root_logger.info(log_entry)
    print(f'[{level}] {log_entry}')


if __name__ == '__main__':
    pass
