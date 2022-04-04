from PyQt5.QtWidgets import *

from Widget_Library.widget_scan import Ui_scan_tab_widget


class Scan(QWidget, Ui_scan_tab_widget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.manager = None
        self.config = None

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def style_ui(self):
        self.waveform_plot.setLabel("left", "Voltage Waveform (V)", **self.waveform_plot.styles)
        self.waveform_plot.setLabel("bottom", "Time (s)", **self.waveform_plot.styles)
        self.profile_plot.setLabel("left", "Voltage Squared Integral", **self.profile_plot.styles)
        self.profile_plot.setLabel("bottom", "Frequency (MHz)", **self.profile_plot.styles)

        #  add default data to plots
        y = range(0, 100)
        x = range(0, 100)
        self.waveform_plot.refresh(x, y)

    def plot(self, x, y, refresh_rate):
        self.last_aquired_waveform_plot_label.setText(f"Last Acquired Waveform - refresh rate: {refresh_rate}")
        if x is None or y is None:
            return
        if len(x) == 0 or len(x) != len(y):
            return

        self.plot_ready = False
        self.waveform_plot.refresh(x, y, pen='k', clear=True)
        self.plot_ready = True

    def update_profile_plot(self, x, y):
        if x is None or y is None:
            return
        if len(x) == 0 or len(x) != len(y):
            return

        self.plot_ready = False
        self.profile_plot.refresh(x, y, pen='k', clear=True)
        self.plot_ready = True