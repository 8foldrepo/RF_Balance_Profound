import os
import numpy as np
import collections.abc

'''
Inputs:
A string containing comma delimited coordinates, some of which may be empty, for example ,,3,2
A list containing the letters of all axes. The length must be greater than the number of commas. Ex: [X,Y,Z,R]
Output:
A list containing the axis letters of the coordinates provided, and a list of equal length containing the coordinates.
With the given inputs the output should be axes: [Z,R] coords [3,2]
'''

def create_coord_rays(coords:str,ax_letters:list):
    axes = list()
    coords = coords.split(',')
    for i in range(len(coords)):
        if not coords[i] == '':
            axes.append(ax_letters[i])

    # Remove empty elements
    coords = list(filter(lambda val: val != '', coords))
    return axes, coords


'''Generate presumed x positions for all elements given the pitch and the position of element 1, used by manager'''

def get_element_distances(element_1_index, element_pitch):
    # length of 11, so index can equal element number. item zero will remain 'nan' and will cause errors if used
    element_coords = [None,None,None,None,None,None,None,None,None,None,None]
    for i in range(10):
        offset = i * element_pitch
        element_coords[i+1] = element_1_index + offset

    return element_coords


'''Create a dictionary containing all the fields available for UA test data, to be filled in by the manager class'''

def blank_test_data() -> dict:
    from datetime import datetime

    test_data = dict()

    #add formatted date
    now = datetime.now()
    formatted_date = now.strftime("%Y.%m.%d-%H.%M")
    test_data['test_date_time'] = formatted_date
    test_data['software_version'] = ""
    test_data['test_comment'] = ""
    test_data['serial_number'] = ""
    test_data['operator_name'] = ""
    test_data['script_name'] = ""
    test_data['script_log'] = list()
    test_data['low_frequency_MHz'] = float('nan')
    test_data['high_frequency_MHz'] = float('nan')
    test_data['hardware_code'] = ""
    test_data['results_summary'] = list()
    test_data["write_result"] = False
    test_data["script_name"] = ""
    lf = str(test_data['low_frequency_MHz'])
    hf = str(test_data['high_frequency_MHz'])

    #Create reults_summary table
    table = [None] * 13
    #Default values, will be updated during test
    table[0] = ['Element_01','0','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[1] = ['Element_02','5','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[2] = ['Element_03','10','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[3] = ['Element_04','15','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[4] = ['Element_05','20','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[5] = ['Element_06','25','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[6] = ['Element_07','30','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[7] = ['Element_08','35','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[8] = ['Element_09','40','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']
    table[9] = ['Element_10','45','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']

    table[10] = ['UA Common','NaN','-90',lf,'NaN',hf,'NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','Pass','']

    elements_with_manual_lf = ['00','01','02','03','04','05','06','07','08','09','10']
    elements_with_manual_hf = ['00','01','02','03','04','05','06','07','08','09','10']

    #Todo: add ability to set manual frequencies per element
    table[11] = elements_with_manual_lf
    table[12] = elements_with_manual_hf

    test_data['results_summary'] = table

    return test_data


'''Create UA calibration data compatible with the UA_Interface_Box class given test_data from the manager class'''

def generate_calibration_data(test_data):
    #Todo: populate this array according to the test_data
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

#Inverse of create coord_rays
def create_comma_string(axes:list,coords:list,ax_letters:list):
    answer = ""
    for i in range(len(ax_letters)):
        if ax_letters[i] in axes:
            index = axes.index(ax_letters[i])
            if len(coords) == len(axes):
                answer = answer + str((coords[index]))

        answer = answer + ","
    return  answer

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

    acoustic_power_on_data = list()

    for i in range(len(acoustic_power_trace_w)):
        if awg_on_ray[i]:
            acoustic_power_on_data.append(acoustic_power_trace_w[i])

    return acoustic_power_on_data

# Additional feature: add smart transition detection
def get_awg_off_values(acoustic_power_trace_w, awg_on_ray):
    if len(acoustic_power_trace_w) == 0:
        return [float('nan')]

    acoustic_power_off_data = list()

    for i in range(len(acoustic_power_trace_w)):
        if not awg_on_ray[i]:
            acoustic_power_off_data.append(acoustic_power_trace_w[i])

    return acoustic_power_off_data

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().setParent(None)


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

#Searches from current directory to grandparent directory for the specified file
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

def get_rigol_addresses(rm = None):
    import pyvisa

    if rm is None:
        rm = pyvisa.ResourceManager()

    devices = rm.list_resources()

    rigols = []
    names = []

    for device in devices:
        if "DG8" in str(device):
            # Checks if the device is in the dictionary of named devices, otherwise gives it the next number
            if str(device) in named_devices:
                device_name = named_devices[str(device)]
                # If the device name is "Rigol number <x>" the next unknown rigol will be "Rigol number <x+1>"
                # This prevents duplicate names.
                r = int(device_name[6:]) + 1
            else:
                device_name = str(device)

            rigols = rigols + [device]
            names = names + [device_name]

    return rigols, names

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
    data = blank_test_data()
    print(data["results_summary"][10])
