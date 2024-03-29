"""The base class for almost all Qt dialogs created for this project"""
import logging
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
from Utilities.useful_methods import log_msg, check_directory
from definitions import ROOT_DIR

log_formatter = logging.Formatter(fmt=LOGGER_FORMAT)
balance_logger = logging.getLogger(name="wtf_log")
directory = os.path.join(ROOT_DIR, "Logs")
check_directory(directory)
with open(os.path.join(directory,"wtf.log"), 'w+') as f:
    pass
file_handler = logging.FileHandler(os.path.join(directory, 'wtf.log'), mode="w+")
file_handler.setFormatter(fmt=log_formatter)
balance_logger.addHandler(hdlr=file_handler)
balance_logger.setLevel(level=logging.INFO)


# Features common to all the dialogs in this project
class MyQDialog(QDialog):
    """Mainly controls logging functionality and abort handling"""
    abort_signal = QtCore.pyqtSignal()
    root_logger = logging.getLogger(name=ROOT_LOGGER_NAME)

    def __init__(self, config=None, parent=None, ):
        super().__init__(parent=parent)

        # If this flag is not true when the dialog is closed, the script will abort
        self.dialog_resolved = False

        if config is not None:
            self.config = config
        else:
            self.config = load_configuration()
        self.set_icon()

    def closeEvent(self, event: QEvent) -> None:
        """
        Abort the script if dialogs are closed without being addressed

        :param event: the close event to be accepted, automatically passed
        """
        if not self.dialog_resolved:
            self.abort_signal.emit()
        event.accept()

    def set_icon(self) -> None:
        """
        Set the icon to the 8Fold logo
        """
        path = os.path.join(ROOT_DIR, "images/8foldlogo.ico")
        self.setWindowIcon(QIcon(path))

    @pyqtSlot(float)
    def time_remaining_slot(self, time_remaining:float):
        """
        Update the time remaining label (when a signal is recieved from Manager)

        :param time_remaining: the time remaining in seconds
        """
        self.setWindowTitle(f"Time Remaining: {'%.0f' % time_remaining}")

    @pyqtSlot()
    def close_dialog_slot(self):
        """
        Consider the dialog resolved and close it (this occurs when the dialog times out)
        """
        self.dialog_resolved=True
        self.close()

    def log(self, message: str, level: str = "info") -> None:
        """
        Ability to log messages

        :param message: the message to be logged/printed
        :param level: the message's level of importance
        """
        log_msg(self, root_logger=self.root_logger, message=message, level=level)

    def reject(self) -> None:
        """
        If escape key is pressed
        """
        self.dialog_resolved = False
        self.abort_signal.emit()
        self.close()
