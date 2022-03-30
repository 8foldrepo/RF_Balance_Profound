import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, 'default.yaml')  # requires `import os`
LOCAL_CONFIG_PATH = os.path.join(ROOT_DIR, 'local.yaml')  # requires `import os`