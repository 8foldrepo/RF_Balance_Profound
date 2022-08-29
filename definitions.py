import os
import sys

if getattr(sys, 'frozen', False):
    print("Running as frozen application")
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.path.dirname(__file__)
DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, "default.yaml")  # requires `import os`
LOCAL_CONFIG_PATH = os.path.join(ROOT_DIR, "local.yaml")
POWER_METER_DLL_PATH = os.path.join(ROOT_DIR, "Hardware", "power_meter_dlls")
SYSTEM_INFO_INI_PATH = os.path.join(ROOT_DIR, "systeminfo.ini")

