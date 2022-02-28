import sys

from PyQt5.QtCore import QThread, qRegisterResourceData
from PyQt5.QtWidgets import *
from MainWindow import MainWindow
from manager import Manager

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT

# from resources import resources  # load our qrc bundled resources
from resources.resources import qt_resource_data, qt_resource_struct, qt_resource_name

import sys
import logging

#Set up logger
fmt_str = LOGGER_FORMAT
log_formatter = logging.Formatter(fmt_str)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

file_handler = logging.FileHandler("./logs/WTF.log", mode='w')
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

root_logger.setLevel(logging.INFO)

# ==> Alternate way to load our qrc bundled resources, directly
qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def main(args):
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    window = MainWindow()

    QThread.currentThread().setObjectName("ui_thread")
    
    window.show()
    window.populate_config_ui()
    #window.prompt_for_password()


    code = app.exec_()

    root_logger.info(f"[{QThread.currentThread().objectName()}] : app exited with code {code}")
    sys.exit(code)
# ==> end of main

if __name__ == "__main__":
    main(sys.argv)
