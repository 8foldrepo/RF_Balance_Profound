import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import log_msg
from definitions import ROOT_DIR

log_formatter = logging.Formatter(LOGGER_FORMAT)
balance_logger = logging.getLogger("wtf_log")
with open(ROOT_DIR + "\\Program_Data\\logs\\wtf.log", 'w') as f:
    pass
file_handler = logging.FileHandler(ROOT_DIR + "\\Program_Data\\logs\\wtf.log", mode="w")
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)


# Features common to all custom widgets in this project
class MyQWidget(QWidget):
    set_buttons_enabled_signal = QtCore.pyqtSignal(bool)

    def __init__(
            self,
            parent=None,
    ):
        super().__init__(parent=parent)

    # Ability to log data
    def log(self, message, level="info"):
        log_msg(self, root_logger, message=message, level=level)
