from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from Utilities.formulas import calculate_total_uncertainty_percent, calculate_random_uncertainty_percent
from Utilities.useful_methods import get_awg_on_values, get_awg_off_values
from Widget_Library.widget_rfb import Ui_Form
from ui_elements.my_qwidget import MyQWidget
import time as t

class RFB(MyQWidget, Ui_Form):
    def __init__(self, parent=None, manager=None, balance=None, config=None):
        super().__init__(parent=parent)
        self.app = QApplication.instance()
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
        self.manager.update_rfb_tab_signal.connect(self.update_rfb_tab)

    def set_balance(self, balance):
        self.balance = balance

    def style_ui(self):
        # add default data to plots
        self.rfb_graph.setLabel("left", "Power (W)", **self.rfb_graph.styles)
        y = range(0, 100)
        x = range(0, 100)
        self.rfb_graph.refresh(x, y)



    @pyqtSlot()
    def update_rfb_tab(self):
        """
        Updates the rfb tab, including the plot and all spinboxes.
        Takes three time vs wattage pairs of lists for forward, reflected, and acoustic power. awg on is a
        list of booleans indicating if the output was on, grams is a float of the latest balance reading.
        """
        if not self.plot_ready:
            return
        self.plot_ready = False

        args = self.manager.rfb_args
        times_s = args['times_s']
        forward_w = args['forward_w']
        reflected_w = args['reflected_w']
        acoustic_w = args['acoustic_w']
        awg_on = args['awg_on']
        grams = args['grams']
        forward_power_w = args['forward_power_w']
        reflected_power_w = args['reflected_power_w']

        min_length = min(len(times_s),len(forward_w),len(reflected_w),len(acoustic_w))

        if grams is not None:
            self.mass_mg_field.setText(str(round(grams * 1000, 2)))

        acoustic_power_on_data = get_awg_on_values(acoustic_w, awg_on)
        acoustic_power_off_data = get_awg_off_values(acoustic_w, awg_on)

        if len(acoustic_power_off_data) != 0:
            acoustic_power_off_mean = sum(acoustic_power_off_data) / len(acoustic_power_off_data)
        else:
            acoustic_power_off_mean = float('nan')

        if len(acoustic_power_on_data) != 0:
            acoustic_power_on_mean = sum(acoustic_power_on_data) / len(acoustic_power_on_data)
        else:
            acoustic_power_on_mean = float('nan')

        if len(acoustic_w) != 0:
            acoustic_power_mean = sum(acoustic_w) / len(acoustic_w)
        else:
            acoustic_power_mean = float('nan')

        self.power_on_w_field.setText(str(round(acoustic_power_on_mean, 2)))
        self.power_on_rand_uc_field.setText(str(round(calculate_random_uncertainty_percent(acoustic_power_on_data), 2)))
        self.power_on_total_uc_field.setText(str(round(calculate_total_uncertainty_percent(acoustic_power_on_data), 2)))

        self.power_off_w_field.setText(str(round(acoustic_power_off_mean, 2)))
        self.power_off_rand_uc_field.setText(
            str(round(calculate_random_uncertainty_percent(acoustic_power_off_data), 2)))
        self.power_off_total_uc_field.setText(
            str(round(calculate_total_uncertainty_percent(acoustic_power_off_data), 2)))

        self.power_combined_field.setText(str(round(acoustic_power_mean, 2)))
        self.power_combined_rand_uc_field.setText(str(round(calculate_random_uncertainty_percent(acoustic_w), 2)))
        self.power_combined_total_uc_field.setText(str(round(calculate_total_uncertainty_percent(acoustic_w), 2)))

        if not (len(times_s) == 0 or len(acoustic_w) == 0):
            self.power_w_field.setText(str(round((acoustic_w[len(acoustic_w) - 1]), 2)))
            self.time_s_field.setText(str(round((times_s[len(times_s) - 1]), 2)))

        self.forward_power_w_field.setText(str(round(forward_power_w, 2)))
        self.reflected_power_w_field.setText(str(round(reflected_power_w, 2)))


        self.rfb_graph.refresh(times_s[0:min_length], forward_w[0:min_length], pen='k', clear=True)
        self.rfb_graph.refresh(times_s[0:min_length], reflected_w[0:min_length], pen='g', clear=False)
        self.rfb_graph.refresh(times_s[0:min_length], acoustic_w[0:min_length], pen='r', clear=False)
        self.app.processEvents()
        self.plot_ready = True
