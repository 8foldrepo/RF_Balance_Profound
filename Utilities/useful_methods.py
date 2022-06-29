"""
A class that provides a wide variety of useful methods throughout the entire project
"""
import collections.abc
import datetime
import os
from logging import Logger
from typing import Tuple, List, Union
from PyQt5.QtWidgets import QTabWidget
from termcolor import colored


def create_coord_rays(coordinates: str, ax_letters: list) -> Tuple[list, List[str]]:
    """ For use with the galil motion controller class

    :param coordinates: A string containing comma delimited coordinates, some of which may be empty, for example [,,3,2]
    :param ax_letters:
        A list containing the letters of all axes. The length must be greater than the number of commas. Ex: [X,Y,Z,R]

    :returns:
        A list containing the axis letters of the coordinates provided, and a list of equal length containing
        the coordinates. With the given inputs the output should be axes: [Z,R] coordinates [3,2]
    """
    axes = list()
    coordinates = coordinates.split(",")
    for i in range(len(coordinates)):
        if coordinates[i] != "":
            axes.append(ax_letters[i])

    # Remove empty elements
    coordinates = list(filter(lambda val: val != "", coordinates))
    return axes, coordinates


def create_comma_string(axes: list, numbers: list, ax_letters: list) -> str:
    """
    For use with the galil motion controller class
    Inverse of create coord_rays

    :param axes: list of axis/axes user wants to create command string for galil motor controller
    :param numbers: the list of steps/coordinate(s) the user wants to turn into a list for given axis/axes
    :param ax_letters:
        the letters representing the axis/axes the user wants to make a list for (can be same as axes
        parameter)
    :returns: string representation of axis/axes step(s)/coordinate(s)
    """
    answer = ""
    for i in range(len(ax_letters)):
        if ax_letters[i] in axes:
            index = axes.index(ax_letters[i])
            if len(numbers) == len(axes):
                answer += str((numbers[index]))

        answer += ","
    return answer


def find_int(string_with_int: str) -> int:
    """
    Returns the first whole number in a given string (chops off decimal if there is one)
    Raises AttributeError if no whole numbers exist

    :param string_with_int: the string that contains the integer we are going to extract with this method
    :returns: integer from passed string; or raises attribute error if no such integer exists
    """
    from re import search
    return int(search(r"\d+", str(string_with_int)).group())


def mean_of_non_none_values(list_of_values: List[Union[int, float, None]]) -> float:
    """
    Returns the average of all values that are not None. Returns float('nan') if there are no non-None values.

    :param list_of_values: 1D-list of integer/float values to calculate the mean from
    :returns: mean of the passed ints/floats list
    """
    sum_to_return = 0
    count = 0
    for value in list_of_values:
        if value is not None:
            sum_to_return += value
            count += 1

    if count < 1:
        return float('nan')

    return sum_to_return / count


def get_element_distances(element_1_index: float, element_pitch: float) -> list:
    """Generate presumed x positions for all elements given the pitch and the position of element 1, used by manager"""
    # length of 11, so index can equal element number. item zero will remain 'nan' and will cause errors if used
    element_coordinates = [None, None, None, None, None, None, None, None, None, None, None]
    for i in range(10):
        element_number = 10-i
        offset = -1 * (element_number-1) * element_pitch
        element_coordinates[element_number] = element_1_index + offset

    return element_coordinates


def error_acceptable(value1: float, value2: float, acceptable_error_percent: float = 6, print_msg=True) -> bool:
    """Returns whether the two values are approximately equal with a given acceptable error percentage"""
    if print_msg:
        print(colored(f'value1 = {value1}, value2 = {value2}', 'yellow'))

    if value1 == 0:
        print("value is 0")
        return False
    return abs((value1 - value2) / value1) * 100 < acceptable_error_percent


def get_bit(num: int, bit_num: int) -> bool:
    """Get a specified bit from an integer. 1 is the LSB, and so on."""
    return bool((num & (1 << bit_num)) >> bit_num)


def update(dictionary: dict, u) -> dict:
    """Updates a nested dictionary with another nested dictionary"""
    for key, value in u.items():
        if isinstance(value, collections.abc.Mapping):
            dictionary[key] = update(dictionary.get(key, {}), value)
        else:
            dictionary[key] = value
    return dictionary


def is_number(s) -> bool:
    """Returns whether the given variable can be typecast as a float"""
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


def in_range(my_index: int, my_list: list) -> bool:
    """returns whether the given index is valid for the given list"""
    return 0 <= my_index < len(my_list)


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

    :param list_to_analyze: list that may have duplicate elements in it
    :returns: list that does not have duplicate elements in it guaranteed
    """
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list_to_analyze:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)

    return unique_list


'''
tab_widget[0].tabText: Welcome
tab_widget[1].tabText: System Info
tab_widget[2].tabText: Edit Script
tab_widget[3].tabText: RFB
tab_widget[4].tabText: UA Calibration
tab_widget[5].tabText: Results
tab_widget[6].tabText: Scan
tab_widget[7].tabText: Position
tab_widget[8].tabText: System Config
'''


def tab_text_to_index(text: str, tab_widget: QTabWidget) -> int:
    """
    Returns the index of the tab with specified text in the main tab widget.
    If no match exists, returns -1. Not case sensitive.

    :param text: the name of the tab one wishes to switch to
    :param tab_widget: the tab widget to scan and see if there's a match between passed text and name of tabs
    :returns: integer representing the tab number of tabWidget if found, -1 if not found
    """
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i).upper() == text.upper():
            return i
    return -1


def clear_layout(layout) -> None:
    """
    Clears contents of passed layout widget

    :param layout: layout QWidget to be cleared
    """
    while layout.count():
        child = layout.takeAt(0)
        if child.edit_menu():
            child.edit_menu().setParent(None)


def trim(lists: List[List]) -> Tuple:
    """
    Cut a tuple of lists to their minimum length, removing elements at the end

    :param lists: the list of lists you would like to equalize in size to the smallest one w/ deletion of element
    :returns: the lists that are now equal in length to the initially-shortest one
    """
    # initialize a list of zeros to the length of the number of lists passed to this method; call it 'lengths'
    lengths = [0] * len(lists)  # INFO: cannot change [None] to [] without errors
    # initialize a list of empty lists to the length of the number of lists passed
    trimmed_lists = [[]] * len(lists)

    # populate the lengths list we made above with the lengths of each list passed in the lists parameter
    for i in range(len(lists)):
        lengths[i] = len(lists[i])

    min_length = min(lengths)

    # chop off any additional items in all lists past the length of the smallest list; store them into 'trimmed_lists'
    for i in range(len(lists)):
        trimmed_lists[i] = (lists[i][0:min_length])

    return tuple(trimmed_lists)


def search_for(filename: str) -> Union[bytes, str]:
    """
    Searches from current directory to grandparent directory for the specified file

    :param filename: The name of the file you are searching for
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


def log_msg(self, root_logger: Logger, message: str, level: str = None, line_number=None) -> None:
    """
    Convenience function to log messages in a compact way with useful info.

    :param self: auto-passed scope of caller
    :param root_logger: logger instance passed from the calling class
    :param level: A string indicating the logger level, can be either 'info', 'debug' or 'error'; case-insensitive
    :param message: A string that contains the message to be logged
    :param line_number: number of the line that called this log method
    """
    from PyQt5.QtCore import QThread

    thread_name = QThread.currentThread().objectName()
    log_entry = f"[{type(self).__name__}] [{line_number}] [{thread_name}] : {message}"
    if level.upper() == "DEBUG":
        if self.config['Debugging']['print_detailed_verbose']:
            root_logger.debug(log_entry)
            color = 'magenta'
        else:
            return
    elif level.upper() == "ERROR" or level.upper() == 'ERR':
        color = 'red'
        root_logger.error(log_entry)
    elif level.upper() == "WARNING" or level.upper() == 'WARN':
        color = 'yellow'
        root_logger.warning(log_entry)
    elif level.upper() == 'INFO':
        color = 'green'
        root_logger.info(log_entry)
    else:
        color = 'cyan'
        level = 'other'
        root_logger.info(log_entry)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{colored(level, color)}] [{type(self).__name__}]"
          f" [{line_number}] [{thread_name}] : " + colored(message, color))


def print_list(list2: list) -> None:
    """
    Vertically prints a list using a for range loop

    :param list2: The list you want to print
    """
    for x in range(len(list2)):
        print(list2[x])


def print_list_2(list2: list) -> None:
    """
    prints a list horizontally using the built-in print method and casts
    what ever is inside the list to a string

    :param list2: The list you want to be printed
    """
    print(str(list2)[1:-1])


def cast_as_bool(var) -> bool:
    """Attemts to cast a given variable as a boolean."""

    if isinstance(var, str):
        return 'T' in var.upper() or '1' in var

    if isinstance(var, int) or isinstance(var, int):
        return var != 0

    return bool(var)


if __name__ == "__main__":
    pass
