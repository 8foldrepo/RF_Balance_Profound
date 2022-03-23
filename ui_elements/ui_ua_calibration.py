from PyQt5.QtWidgets import *

from Widget_Library.widget_ua_calibration import Ui_Form


class UACalibration(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ua_interface = None
        self.setupUi(self)
        self.manager = None
        self.config = None
        self.configure_signals()

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def set_ua_interface(self, ua_interface):
        self.ua_interface = ua_interface

    @pyqtSlot(list)
    def configure_signals(self):
        self.read_from_ua_button.clicked.connect(ua_interface.read())

    def fill_labels(self):
