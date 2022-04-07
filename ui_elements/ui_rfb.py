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

    """Updates one of the plots of the graph, first list is time, second list is the measurement,
    the string is the color letter, the boolean is whether or not to clear the plot."""
    @pyqtSlot(list, list, list, list,list, list)
    def update_rfb_plot(self, forward_s, forward_w, reflected_s, reflected_w, acoustic_s, acoustic_w):
        if not self.plot_ready:
            return

        if forward_w is None:
            return

        if len(forward_w) != len(forward_s) or len(reflected_w) != len(reflected_s) or len(acoustic_w) != len(acoustic_s):
            return

        self.plot_ready = False
        self.rfb_graph.refresh(forward_s, forward_w, pen='k', clear=True)
        if reflected_w is not None:
            self.rfb_graph.refresh(reflected_s, reflected_w, pen='g', clear=False)
        if acoustic_w is not None:
            self.rfb_graph.refresh(acoustic_s, acoustic_w, pen='r', clear=False)
        self.plot_ready = True
