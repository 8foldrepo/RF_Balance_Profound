import os
from enum import Enum


class WaterLevel(Enum):
    below_level = 1
    level = 2
    above_level = 3


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, "default.yaml")  # requires `import os`
LOCAL_CONFIG_PATH = os.path.join(ROOT_DIR, "local.yaml")
POWER_METER_DLL_PATH = os.path.join(ROOT_DIR, "Hardware", "power_meter_dlls")
SYSTEM_INFO_INI_PATH = os.path.join(ROOT_DIR, "systeminfo.ini")
