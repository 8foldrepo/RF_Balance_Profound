from PyQt5.QtCore import QThread, qRegisterResourceData
from PyQt5.QtWidgets import *
from MainWindow import MainWindow

# from resources import resources  # load our qrc bundled resources
from resources.resources import qt_resource_data, qt_resource_struct, qt_resource_name

import sys

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)
import os
from definitions import ROOT_DIR
balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR,"./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

# ==> Alternate way to load our qrc bundled resources, directly
qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def main(args):
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    window = MainWindow()

    QThread.currentThread().setObjectName("ui_thread")
    
    window.show()
    window.system_info_tab.load_system_info()
    window.system_config.populate_config_ui()
    #window.prompt_for_password()
    # Todo: For testing purposes, remove later
    #window.manager.test_code()

    code = app.exec_()

    root_logger.info(f"[{QThread.currentThread().objectName()}] : app exited with code {code}")
    sys.exit(code)
# ==> end of main

if __name__ == "__main__":
    main(sys.argv)
