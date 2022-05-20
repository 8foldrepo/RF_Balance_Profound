import collections.abc
import datetime
import os
from typing import Tuple, List

import numpy as np
from PyQt5.QtWidgets import QTabWidget

from data_structures.test_data import TestData


def create_coord_rays(coordinates: str, ax_letters: list):
    """
    Inputs:
    A string containing comma delimited coordinates, some of which may be empty, for example [,,3,2]
    A list containing the letters of all axes. The length must be greater than the number of commas. Ex: [X,Y,Z,R]
    Output:
    A list containing the axis letters of the coordinates provided, and a list of equal length containing the
    coordinates. With the given inputs the output should be axes: [Z,R] coordinates [3,2]
    """
    axes = list()
    coordinates = coordinates.split(",")
    for i in range(len(coordinates)):
        if coordinates[i] != "":
            axes.append(ax_letters[i])

    # Remove empty elements
    coordinates = list(filter(lambda val: val != "", coordinates))
    return axes, coordinates


def get_element_distances(element_1_index, element_pitch):
    """Generate presumed x positions for all elements given the pitch and the position of element 1, used by manager"""
    # length of 11, so index can equal element number. item zero will remain 'nan' and will cause errors if used
    element_coordinates = [None, None, None, None, None, None, None, None, None, None, None]
    for i in range(10):
        offset = i * element_pitch
        element_coordinates[i + 1] = element_1_index + offset

    return element_coordinates


def generate_calibration_data(test_data: TestData) -> list[str]:
    """Create UA calibration data compatible with the UA_Interface_Box class given test_data from the manager class"""
    output = [] * 27
    output[0] = str(test_data.schema)
    output[1] = str(test_data.serial_number)
    date_str = test_data.test_date_time[0:4] + test_data.test_date_time[5:7] + test_data.test_date_time[8:10]
    print(date_str)
    output[2] = date_str
    output[3] = str(test_data.hardware_code)
    output[4] = str(test_data.low_frequency_MHz)
    output[5] = str(test_data.high_frequency_MHz)
    output[6] = str(test_data.results_summary[10][2])  # angle average
    for i in range(10):
        output[i + 7] = test_data.results_summary[i][7]  # LF efficiency percent
    for i in range(10):
        output[i + 17] = test_data.results_summary[i][11]  # LF efficiency percent

    return output


def create_comma_string(axes: list, coordinates: list, ax_letters: list):
    """
    Inverse of create coord_rays
    """
    answer = ""
    for i in range(len(ax_letters)):
        if ax_letters[i] in axes:
            index = axes.index(ax_letters[i])
            if len(coordinates) == len(axes):
                answer = answer + str((coordinates[index]))

        answer = answer + ","
    return answer


def update(dictionary: dict, u):
    for key, value in u.items():
        if isinstance(value, collections.abc.Mapping):
            dictionary[key] = update(dictionary.get(key, {}), value)
        else:
            dictionary[key] = value
    return dictionary


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def check_directory(path):
    """
    Check whether the specified path exists or not,
    create a new directory because it does not exist
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def precision_round(number: float, digits: int = 3) -> float:
    """
    takes a float number and the number of precision digits, then
    returns the float rounded to the specified precision
    """
    power = "{:e}".format(number).split("e")[1]
    return round(number, -(int(power) - digits))


def bound(x: float) -> float:
    """
    If passed int x is between -.001 and .001, it turns x to 0 and returns it,
    otherwise, returns x as is
    """
    if -0.001 < x < 0.001:
        x = 0
    return x


def unique(list_to_analyze: list) -> list:
    """
    Takes a list that might have duplicate elements in it and returns
    a list with the duplicates removed
    """
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list_to_analyze:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)

    return unique_list


def tab_text_to_index(text: str, tab_widget: QTabWidget) -> int:
    """
    Returns the index of the tab with specified text in the main tab widget.
    If no match exists, returns -1. Not case sensitive.
    """
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i).upper() == text.upper():
            return i
    return -1


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.edit_menu():
            child.edit_menu().setParent(None)


def trim(lists: List[List]) -> Tuple:
    """Cut a tuple of lists to their minimum length, removing elements at the end"""
    lengths = [] * len(lists)
    trimmed_lists = [None] * len(lists)

    for i in range(len(lists)):
        lengths[i: int] = len(lists[i])

    # Ensure that every list had its length checked
    assert None not in lengths

    min_length = min(lengths)

    for i in range(len(lists)):
        trimmed_lists[i] = (lists[i][0:min_length])

    # Ensure that every list was trimmed
    assert None not in trimmed_lists

    return tuple(trimmed_lists)


def list_to_ray(x_coordinates, y_coordinates, z_coordinates, intensity):
    unique_x_coordinates = unique(list_to_analyze=x_coordinates)
    unique_y_coordinates = unique(list_to_analyze=y_coordinates)
    unique_z_coordinates = unique(list_to_analyze=z_coordinates)

    coordinates = (unique_x_coordinates, unique_y_coordinates, unique_z_coordinates)
    coordinate_map = np.zeros((len(unique_x_coordinates), len(unique_y_coordinates), len(unique_z_coordinates)))

    for i in range(len(x_coordinates)):
        x = unique_x_coordinates.index(x_coordinates[i])
        y = unique_y_coordinates.index(y_coordinates[i])
        z = unique_z_coordinates.index(z_coordinates[i])

        coordinate_map[x][y][z] = intensity[i]

    return coordinate_map, coordinates


def search_for(filename):
    """
    Searches from current directory to grandparent directory for the specified file
    """
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


def create_test_results_summary_file(test_data: TestData, path):
    """Saves the dictionary containing test info to a specified path, formatted as a results summary"""
    f = open(path, "w")

    f.write(test_data.serial_number + "-" + test_data.test_date_time + "\n")
    f.write("Test operator\t" + test_data.operator_name + "\n")
    f.write("Comment\t" + test_data.test_comment + "\n")
    f.write("Software Version\t" + test_data.software_version + "\n")
    f.write("Script\t" + test_data.script_name + "\n")
    if test_data.write_result:
        f.write("UA Write\tOK\n")
    else:
        f.write("UA Write\tFAIL\n")
    f.write("UA hardware code\t" + test_data.hardware_code + "\n")
    f.write("\n")  # empty line
    f.write(
        "\tX\tTheta\tLF (MHz)\tLF.VSI (V^2s)\tHF (MHz)\tHF.VSI (V^2s)\tLF.Eff (%)\tLF.Rfl (%)\tLF.Pf(max) (W)\t"
        "LF.WTemp (degC)\tHF.Eff (%)\tHF.Rfl (%)\tHF.Pf(max) (W)\tHF.WTemp (degC)\tElement result\t"
        "Failure description\n"
    )

    element_data_list = test_data.results_summary
    for x in range(len(element_data_list)):
        if 0 <= x <= 10:  # for all the element lines and the UA Common line
            if x == 10:
                f.write("\n")  # there are empty lines around "UA Common" row
            f.write("\t".join(element_data_list[x]))
            f.write("\n")
        if x == 11:  # for the elements with manual LF...
            f.write("\n")
            f.write("Elements with manual LF\t" + ",".join(element_data_list[x]))
            f.write("\n")
        if x == 12:  # for the elements with manual HF...
            f.write("Elements with manual HF\t" + ",".join(element_data_list[x]))
    f.close()
    print(f'wrote to {path}')


def log_msg(self, root_logger, message: str, level: str = None, line_number=None) -> None:
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
    log_entry = f"[{type(self).__name__}] [{line_number}] [{thread_name}] : {message}"
    if level == "debug":
        root_logger.debug(log_entry)
    elif level == "error":
        root_logger.error(log_entry)
    elif level == "warning":
        root_logger.warning(log_entry)
    else:
        root_logger.info(log_entry)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{level}] {log_entry}")


def print_list(list2):
    """
    Prints a list using a for range loop
    """
    for x in range(len(list2)):
        print(list2[x])


def print_list_2(list2):
    """
    prints a list using the built-in print method and casts
    what ever is inside the list to a string
    """
    print(str(list2)[1:-1])


# if __name__ == "__main__":
#     pass
