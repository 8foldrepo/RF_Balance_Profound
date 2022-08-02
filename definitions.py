import os

ROOT_DIR = os.getcwd()
DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, "default.yaml")  # requires `import os`
LOCAL_CONFIG_PATH = os.path.join(ROOT_DIR, "local.yaml")
POWER_METER_DLL_PATH = os.path.join(ROOT_DIR)
SYSTEM_INFO_INI_PATH = os.path.join(ROOT_DIR, "systeminfo.ini")

