from Widget_Library.widget_rfb import Ui_Form
from PyQt5.QtCore import pyqtSlot
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
import os
from definitions import ROOT_DIR
from ui_elements.my_qwidget import MyQWidget

log_formatter = logging.Formatter(LOGGER_FORMAT)
balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class RFB(MyQWidget, Ui_Form):
    def __init__(self, parent=None, manager=None, balance=None, config = None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.balance = balance
        self.manager = manager
        self.config = config
        self.style_ui()
        self.plot_ready = True

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager
        self.manager.rfb_plot_signal.connect(self.update_rfb_plot)

    def set_balance(self, balance):
        self.balance = balance

    def style_ui(self):
        # add default data to plots
        y = range(0, 100)
        x = range(0, 100)
        self.rfb_graph.refresh(x, y)

    @pyqtSlot(list,list,list,list,list)
    def update_rfb_plot(self, time_s, forward_power, reflected_power,balance_readings_g,oscilloscope_amplitude):
        if not self.plot_ready:
            return

        if time_s is None or forward_power is None or reflected_power is None:
            self.plot_ready = True
            return

        if len(forward_power) == 0 or len(forward_power) != len(time_s) or len(reflected_power) != len(time_s):
            #self.log(level="Error", message="Length mismatch")
            self.plot_ready = True
            return

        self.plot_ready = False
        self.rfb_graph.refresh(time_s, forward_power, pen='r', clear=True)
        self.rfb_graph.refresh(time_s, reflected_power, pen='k', clear=False)
        #todo, change to combined power
        self.rfb_graph.refresh(time_s, balance_readings_g, pen='b', clear=False)
        self.rfb_graph.refresh(time_s, oscilloscope_amplitude, pen='g', clear=False)
        self.plot_ready = True
