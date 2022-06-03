from typing import List

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import *

from Utilities.formulas import calculate_random_uncertainty_percent
from Utilities.useful_methods import tab_text_to_index
from Widget_Library.widget_scan import Ui_scan_tab_widget
from manager import Manager
from ui_elements.my_qwidget import MyQWidget


# noinspection PyUnresolvedReferences
class Scan(MyQWidget, Ui_scan_tab_widget):
    command_signal = pyqtSignal(str)
    manager: Manager

    x_data_type: str
    y_data_type: str
    x_data_: List[float]
    y_data: List[float]

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.filename = None
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
        self.acquire_scope_trace_button.clicked.connect(self.acquire_scope_trace_button_clicked)
        self.source_channel_combo_box.currentTextChanged.connect(self.source_channel_combo_changed)
        self.averages_spin_box.valueChanged.connect(self.averages_spin_box_changed)
        self.acquisition_type_combo_box.currentTextChanged.connect(self.acquisition_type_combo_changed)
        self.index_spinbox.valueChanged.connect(self.show_data_point)
        self.start_scan_button.clicked.connect(self.scan_clicked)

    def scan_clicked(self):
        """Retrieve scan settings from the UI and tell the manager to begin a 1d scan with those settings"""

        command_ray = [""] * 15
        command_ray[0] = "SCAN"
        command_ray[1] = self.axis_combo.currentText()
        command_ray[2] = str(self.pts_spin.value())
        command_ray[3] = str(self.increment_spin.value())
        command_ray[4] = self.ref_pos_combo.currentText()
        command_ray[5] = self.end_pos_combo.currentText()
        command_ray[6] = self.comments_input.text()
        command_ray[7] = self.filename_stub_input.text()
        command_ray[8] = self.data_directory_input.text()
        command_ray[9] = self.acquisition_type_combo.currentText()
        command_ray[10] = self.source_channel_combo.currentText()
        command_ray[11] = str(self.averages_spin_box.value())
        command_ray[12] = str(self.element_spinbox.value())
        command_ray[13] = self.store_state_combo.currentText()
        command_ray[14] = self.serial_input.text()

        command_string = "_".join(command_ray)
        self.command_signal.emit(command_string)

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        """Enables or disables UI elements that could interfere with a script being run"""

        self.acquire_scope_trace_button.setEnabled(enabled)
        # Acquire waveform tab
        # Acquisition arg. box
        self.acquisition_type_combo_box.setEnabled(enabled)
        self.source_channel_combo_box.setEnabled(enabled)
        self.averages_spin_box.setEnabled(enabled)
        # Waveform data out box
        self.index_spinbox.setEnabled(enabled)
        # Scan setup tab
        # Scan details box
        self.axis_combo.setEnabled(enabled)
        self.pts_spin.setEnabled(enabled)
        self.increment_spin.setEnabled(enabled)
        self.ref_pos_combo.setEnabled(enabled)
        self.end_pos_combo.setEnabled(enabled)
        self.comments_input.setEnabled(enabled)
        self.filename_stub_input.setEnabled(enabled)
        self.data_directory_input.setEnabled(enabled)
        self.file_browser_button.setEnabled(enabled)
        # Acquisition settings
        self.acquisition_type_combo.setEnabled(enabled)
        self.source_channel_combo_box.setEnabled(enabled)
        self.window_combo_box_2.setEnabled(enabled)
        self.averages_spin_box_2.setEnabled(enabled)
        self.start_scan_button.setEnabled(enabled)
        self.source_channel_combo.setEnabled(enabled)

    def show_data_point(self):
        """Display the waveform data at a specified index to the UI"""

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

    def acquisition_type_combo_changed(self):
        if self.acquisition_type_combo_box.currentText() == "Single Waveform":
            self.manager.oscilloscope_averages = 1
            self.averages_spin_box.setEnabled(False)
        else:
            self.averages_spin_box.setEnabled(True)

    def acquire_scope_trace_button_clicked(self):
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
        self.command_signal.connect(self.manager.exec_command)

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

        self.last_acquired_waveform_plot_label.setText(
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
        self.profile_plot_ready = False

        # Cancel if the current tab is not visible
        if not self.tabWidget.tabText(self.tabWidget.currentIndex()) == "Scan":
            self.profile_plot_ready = True
            return
        if x is None or y is None:
            self.profile_plot_ready = True
            return
        if len(x) == 0 or len(x) != len(y):
            self.profile_plot_ready = True
            return

        self.profile_plot.setLabel("bottom", axis_label, **self.profile_plot.styles)
        self.profile_plot.refresh(x, y, pen="k", clear=True)
        self.app.processEvents()
        self.profile_plot_ready = True

    @pyqtSlot(list)
    def set_tab_slot(self, tab_ray):
        if len(tab_ray) < 1:
            return
        index = tab_text_to_index(tab_ray[0], self.scan_tabs)
        if index == -1:
            return
        self.scan_tabs.setCurrentIndex(index)

        if tab_ray[0].upper() == "SCAN":
            if len(tab_ray) < 2:
                return

            self.set_scan_tab_signal.emit([tab_ray[1]])


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = Scan()
    ui.show()
    sys.exit(app.exec_())
