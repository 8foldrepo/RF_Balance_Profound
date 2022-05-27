import time as t

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_rfb import Ui_Form
from ui_elements.my_qwidget import MyQWidget


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

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        # all buttons are already disabled by default
        pass

    def style_ui(self):
        # add default data to plots
        self.rfb_graph.setLabel("left", "Power (W)", **self.rfb_graph.styles)
        y = range(0, 100)
        x = range(0, 100)
        self.rfb_graph.refresh(x, y)
        # INFO: for some reason the bottom three elements' Pixmap don't copy over correctly
        # INFO: in widget_rfb.py when using the pyuic command, fixed via manually overriding here
        self.reverse_pwr_img.setPixmap(QtGui.QPixmap("ui_elements/images/reverse power.png"))
        self.xsition_pwr_img.setPixmap(QtGui.QPixmap("ui_elements/images/xsition pts.png"))
        self.forward_pwr_img.setPixmap(QtGui.QPixmap("ui_elements/images/forward power.png"))


    @pyqtSlot()
    def update_rfb_tab(self):
        """
        Updates the rfb tab, including the plot and all spinboxes.
        Takes three time vs wattage pairs of lists for forward, reflected, and acoustic power. awg on is a
        list of booleans indicating if the output was on, grams is a float of the latest balance reading.
        """
        if not self.plot_ready:
            return

        start_time = t.time()

        # print("graphing")
        self.plot_ready = False
        self.app.processEvents()

        rfb_data = self.manager.rfb_data

        times_s = rfb_data.times_s
        forward_w = rfb_data.f_meter_readings_w
        reflected_w = rfb_data.r_meter_readings_w
        acoustic_w = rfb_data.acoustic_powers_w
        awg_on = rfb_data.awg_on_ray
        grams = rfb_data.grams
        forward_power_w = rfb_data.forward_power_w
        reflected_power_w = rfb_data.reflected_power_w
        p_on_rand_unc = rfb_data.p_on_rand_unc
        p_off_rand_unc = rfb_data.p_off_rand_unc
        p_on_total_unc = rfb_data.p_on_total_unc
        p_off_total_unc = rfb_data.p_off_total_unc
        p_com_rand_unc = rfb_data.p_com_rand_unc
        p_com_total_unc = rfb_data.p_com_total_unc
        acoustic_power_off_mean = rfb_data.acoustic_power_off_mean
        acoustic_power_on_mean = rfb_data.acoustic_power_on_mean
        acoustic_power_mean = rfb_data.acoustic_power_mean

        if grams is not None:
            self.mass_mg_field.setText(str(round(grams * 1000, 2)))

        self.power_on_w_field.setText(str(round(acoustic_power_on_mean, 2)))
        self.power_on_rand_uc_field.setText(str(round(p_on_rand_unc, 2)))
        self.power_on_total_uc_field.setText(str(round(p_on_total_unc, 2)))

        self.power_off_w_field.setText(str(round(acoustic_power_off_mean, 2)))
        self.power_off_rand_uc_field.setText(str(round(p_off_rand_unc, 2)))
        self.power_off_total_uc_field.setText(str(round(p_off_total_unc, 2)))

        self.power_combined_field.setText(str(round(acoustic_power_mean, 2)))
        self.power_combined_rand_uc_field.setText(str(round(p_com_rand_unc, 2)))
        self.power_combined_total_uc_field.setText(str(round(p_com_total_unc, 2)))

        if not (len(times_s) == 0 or len(acoustic_w) == 0):
            self.power_w_field.setText(str(round((acoustic_w[len(acoustic_w) - 1]), 2)))
            self.time_s_field.setText(str(round((times_s[len(times_s) - 1]), 2)))

        self.forward_power_w_field.setText(str(round(forward_power_w, 2)))
        self.reflected_power_w_field.setText(str(round(reflected_power_w, 2)))

        min_length = min(len(times_s), len(forward_w), len(reflected_w), len(acoustic_w))
        self.rfb_graph.refresh(times_s, forward_w[0:min_length], pen="k", clear=True)
        self.rfb_graph.refresh(times_s[0:min_length], reflected_w[0:min_length], pen="g", clear=False)
        self.rfb_graph.refresh(times_s[0:min_length], acoustic_w[0:min_length], pen="r", clear=False)
        self.app.processEvents()
        self.plot_ready = True
