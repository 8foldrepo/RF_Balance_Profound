import os
import numpy as np
import collections.abc

named_devices = {
    "USB0::0x1AB1::0x0643::DG8A223502685::INSTR": "Rigol 1",
    "USB0::0x1AB1::0x0643::DG8A221701373::INSTR": "Rigol 2",
    "USB0::0x1AB1::0x0643::DG8A223502698::INSTR": "Rigol 3",
    "USB0::0x1AB1::0x0643::DG8A221701383::INSTR": "Rigol 4",
    "USB0::0x1AB1::0x0643::DG8A223502692::INSTR": "Rigol 5",
}

#Inputs:
#A string containing comma delimited coordinates, some of which may be empty, for example ,,3,2
#A list containing the letters of all axes. The length must be greater than the number of commas. Ex: [X,Y,Z,R]
#Output:
#A list containing the axis letters of the coordinates provided, and a list of equal length containing the coordinates.
#With the given inputs the output should be axes: [Z,R] coords [3,2]

def create_coord_rays(coords:str,ax_letters:list):
    axes = list()
    coords = coords.split(',')
    for i in range(len(coords)):
        if not coords[i] == '':
            axes.append(ax_letters[i])

    # Remove empty elements
    coords = list(filter(lambda val: val != '', coords))
    return axes, coords

def get_element_distances(element_1_index, element_pitch):
    # length of 11, so index can equal element number. item zero will remain 'nan' and will cause errors if used
    element_coords = [None,None,None,None,None,None,None,None,None,None,None]
    for i in range(1,11):
        offset = i * element_pitch
        element_coords[i] = element_1_index + offset

    return element_coords

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
    rigols, names = get_rigol_addresses()

    print(rigols)
    print(names)
