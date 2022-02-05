import yaml
import os

ROOT_LOGGER_NAME = 'wtf_log'

LOGGER_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"


def load_configuration() -> dict:
    """
    Load the configuration .yaml file into a dictionary
    """

    with open(search_for('default.yaml'), 'r') as fh:
        configuration = yaml.load(fh, Loader=yaml.SafeLoader)

    local_config_path = search_for('local.yaml')

    if os.path.isfile(local_config_path) is False:  # -> file does not exist
        print(f"[-] File: {local_config_path} does not exist")

        with open('./config/local.yaml', 'r') as fh:
            update_dict_recursive(
                configuration, yaml.load(fh, Loader=yaml.SafeLoader)
            )

    else:
        with open(local_config_path, 'r') as fh:
            update_dict_recursive(
                configuration, yaml.load(fh, Loader=yaml.SafeLoader)
            )

    return configuration

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

def update_dict_recursive(d, u) -> dict:
    pass
