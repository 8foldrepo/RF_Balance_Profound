import os
from definitions import DEFAULT_CONFIG_PATH
from definitions import LOCAL_CONFIG_PATH
import yaml
from Utilities import useful_methods

ROOT_LOGGER_NAME = "wtf_log"
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"



def load_configuration() -> dict:
    """
    Load the configuration .yaml file into a dictionary
    """

    with open(DEFAULT_CONFIG_PATH, "r") as fh:
        configuration = yaml.load(fh, Loader=yaml.SafeLoader)

    if os.path.isfile(LOCAL_CONFIG_PATH) is False:  # -> file does not exist
        print(f"[-] File: {LOCAL_CONFIG_PATH} does not exist")
    else:
        with open(LOCAL_CONFIG_PATH, "r") as fh:
            local_config = yaml.load(fh, Loader=yaml.SafeLoader)
            try:
                useful_methods.update(configuration, local_config)
            except AttributeError as e:
                if str(e) == "'NoneType' object has no attribute 'items'":
                    pass
                else:
                    print(f"AttributeError in load_config: {e}")

    return configuration


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
