from PyQt5.QtWidgets import QWidget
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
import logging
from Utilities.useful_methods import log_msg

log_formatter = logging.Formatter(LOGGER_FORMAT)
import os
from definitions import ROOT_DIR

balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class MyQWidget(QWidget):
    def __init__(self, parent=None, ):
        super().__init__(parent=parent)

    def log(self, message, level='info'):
        log_msg(self, self.root_logger, message=message, level=level)