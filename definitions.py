import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, "Program_Data/default.yaml")  # requires `import os`
LOCAL_CONFIG_PATH = os.path.join(ROOT_DIR, "Program_Data/local.yaml")
POWER_METER_DLL_PATH = os.path.join(ROOT_DIR, "Program_Data")
SYSTEM_INFO_INI_PATH = os.path.join(ROOT_DIR, "Program_Data/systeminfo.ini")
