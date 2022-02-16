import os
import time as t
import numpy as np
import yaml
named_devices = {
    "USB0::0x1AB1::0x0643::DG8A223502685::INSTR": "Rigol 1",
    "USB0::0x1AB1::0x0643::DG8A221701373::INSTR": "Rigol 2",
    "USB0::0x1AB1::0x0643::DG8A223502698::INSTR": "Rigol 3",
    "USB0::0x1AB1::0x0643::DG8A221701383::INSTR": "Rigol 4",
    "USB0::0x1AB1::0x0643::DG8A223502692::INSTR": "Rigol 5",
}

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

def load_config():
    current_directory = os.path.dirname(__file__)
    # Determine the parent directory using os.path.split:
    parent_directory = os.path.split(current_directory)[0]  # Repeat as needed
    grandparent_directory = os.path.split(parent_directory)[0]  # Repeat as needed
    config = None

    try:
        file_path = search_for("default.yaml")

        with open(file_path) as file:
            print("Loading parameters from default.yaml")
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            config = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("Default.yaml not found")

    try:
        file_path = search_for("local.yaml")

        with open(file_path) as file:
            print("Overriding parameters from local.yaml")
            try:
                changes = yaml.load(file, Loader=yaml.FullLoader)
                config.update(changes)
            except:
                print("No changes made")
    except FileNotFoundError:
        print("Local.yaml not found, no changes made")
    return config

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

if __name__ == '__main__':
    rigols, names = get_rigol_addresses()

    print(rigols)
    print(names)
