from typing import List

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import *

from Utilities.formulas import calculate_random_uncertainty_percent
from Widget_Library.widget_scan import Ui_scan_tab_widget
from manager import Manager


class Scan(QWidget, Ui_scan_tab_widget):
    command_signal = pyqtSignal(str)
    manager: Manager

    x_data_type: str
    y_data_type: str
    x_data_: List[float]
    y_data: List[float]

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.app = QApplication.instance()
        self.setupUi(self)
        self.x_data = []
        self.y_data = []
        self.x_data_type = self.x_data_type_view.toPlainText()
        self.y_data_type = self.y_data_type_view.toPlainText()

        self.tabWidget = None
        self.manager = None
        self.config = None

        # True if the widget is not currently plotting
        self.plot_ready = True
        self.profile_plot_ready = True

        self.configure_signals()
        self.style_ui()

    def configure_signals(self):
        self.file_browser_button.clicked.connect(self.browse_clicked)
        # Tell the manager to capture a scope trace and emit back the plot data. This uses a command not a direct call
        # or a signal so it runs in the manager thread.
        self.acquire_scope_trace_button.clicked.connect(self.aquire_scope_trace_button_clicked)
        self.source_channel_combo_box.currentTextChanged.connect(self.source_channel_combo_changed)
        self.averages_spin_box.valueChanged.connect(self.averages_spin_box_changed)
        self.acquisition_type_combo_box.currentTextChanged.connect(self.aquisition_type_combo_changed)
        self.index_spinbox.valueChanged.connect(self.show_data_point)

    def show_data_point(self):
        index = self.index_spinbox.value()
        if not index > len(self.x_data):
            self.x_data_view.setText("{:.4e}".format(self.x_data[index]))
        if not index > len(self.y_data):
            self.y_data_view.setText("{:.4e}".format(self.y_data[index]))
            self.y_uncertainty_view.setText("{:.4e}".format(calculate_random_uncertainty_percent(self.y_data)))

    def source_channel_combo_changed(self):
        self.manager.oscilloscope_channel = int(self.source_channel_combo_box.currentText())

    def averages_spin_box_changed(self):
        self.manager.oscilloscope_averages = self.averages_spin_box.value()
        print(self.manager.oscilloscope_averages)

    def aquisition_type_combo_changed(self):
        if self.acquisition_type_combo_box.currentText() == "Single Waveform":
            self.manager.oscilloscope_averages = 1
            self.averages_spin_box.setEnabled(False)
        else:
            self.averages_spin_box.setEnabled(True)

    def aquire_scope_trace_button_clicked(self):
        self.command_signal.emit("CAPTURE")

    def browse_clicked(self):
        self.filename = QFileDialog.getExistingDirectory(self)
        self.data_directory_input.setText(self.filename)
        return self.filename

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager
        self.manager.plot_signal.connect(self.plot)
        self.manager.profile_plot_signal.connect(self.update_profile_plot)

    def set_tabWidget(self, tabWidget):
        self.tabWidget = tabWidget

    def style_ui(self):
        self.scan_tabs.setCurrentIndex(0)
        self.waveform_plot.setLabel("left", "Voltage Waveform (V)", **self.waveform_plot.styles)
        self.waveform_plot.setLabel("bottom", "Time (s)", **self.waveform_plot.styles)
        self.profile_plot.setLabel("left", "Voltage Squared Integral", **self.profile_plot.styles)
        self.profile_plot.setLabel("bottom", "Frequency (MHz)", **self.profile_plot.styles)
        self.voltage_time_plot.setLabel("left", "Voltage Waveform (V)", **self.voltage_time_plot.styles)
        self.voltage_time_plot.setLabel("bottom", "Time (s)", **self.voltage_time_plot.styles)

        #  add default data to plots
        y = range(0, 100)
        x = range(0, 100)
        self.waveform_plot.refresh(x, y)
        self.profile_plot.refresh(x, y)
        self.voltage_time_plot.refresh(x, y)
        self.app.processEvents()

    def plot(self, x, y, refresh_rate):
        self.x_data = x
        self.y_data = y
        # Cancel if this widget is not plot ready
        if not self.plot_ready:
            return

        # Cancel if the current tab is not visible
        if not self.tabWidget.tabText(self.tabWidget.currentIndex()) == "Scan":
            return

        self.last_aquired_waveform_plot_label.setText(
            f"Last Acquired Waveform - refresh rate: {refresh_rate}"
        )
        if x is None or y is None:
            return
        if len(x) == 0 or len(x) != len(y):
            return

        self.plot_ready = False
        self.waveform_plot.refresh(x, y, pen="k", clear=True)

        self.voltage_time_plot.refresh(x, y, pen='k', clear=True)
        self.x_data_type = "Time (s)"
        self.y_data_type = "Voltage (V)"
        self.update_type_labels()

        self.app.processEvents()
        self.plot_ready = True

    def update_type_labels(self):
        self.x_data_type_view.setText(self.x_data_type)
        self.y_data_type_view.setText(self.y_data_type)

    @pyqtSlot(list, list, str)
    def update_profile_plot(self, x, y, axis_label):
        # Cancel if this widget is not plot ready
        if not self.profile_plot_ready:
            return

        # Cancel if the current tab is not visible
        if not self.tabWidget.tabText(self.tabWidget.currentIndex()) == "Scan":
            return

        tabs = self.scan_tabs

        if not tabs.tabText(tabs.currentIndex()) == "1D Scan":
            return

        if x is None or y is None:
            return
        if len(x) == 0 or len(x) != len(y):
            return

        self.profile_plot.setLabel("bottom", axis_label, **self.profile_plot.styles)

        self.profile_plot_ready = False
        try:
            self.profile_plot.refresh(x, y, pen="k", clear=True)
            self.app.processEvents()
        except Exception:
            self.profile_plot_ready = True
        self.profile_plot_ready = True


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = Scan()
    ui.show()
    sys.exit(app.exec_())