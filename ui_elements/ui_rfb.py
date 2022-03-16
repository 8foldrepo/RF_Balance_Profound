from PyQt5.QtWidgets import *

from Widget_Library.widget_rfb import Ui_Form

class RFB(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.balance = None
        self.manager = None
        self.config = None

        # add default data to plots
        y = range(0, 100)
        x = range(0, 100)
        self.rfb_graph.refresh(x, y)

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def set_balance(self, balance):
        self.balance = balance

    def style_ui(self):
        # add default data to plots
        y = range(0, 100)
        x = range(0, 100)
        self.profile_plot.refresh(x, y)
        self.rfb_graph.refresh(x, y)
