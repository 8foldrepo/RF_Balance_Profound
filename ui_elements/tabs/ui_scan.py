from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import *

from Widget_Library.widget_scan import Ui_scan_tab_widget


class Scan(QWidget, Ui_scan_tab_widget):
    command_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.app = QApplication.instance()
        self.setupUi(self)
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
        self.command_signal.connect(self.manager.exec_command)

    def set_tabWidget(self, tabWidget):
        self.tabWidget = tabWidget

    def style_ui(self):
        self.scan_tabs.setCurrentIndex(0)
        self.waveform_plot.setLabel(
            "left", "Voltage Waveform (V)", **self.waveform_plot.styles
        )
        self.waveform_plot.setLabel("bottom", "Time (s)", **self.waveform_plot.styles)
        self.profile_plot.setLabel(
            "left", "Voltage Squared Integral", **self.profile_plot.styles
        )
        self.profile_plot.setLabel(
            "bottom", "Frequency (MHz)", **self.profile_plot.styles
        )
        self.voltage_time_plot.setLabel(
            "left", "Voltage Waveform (V)", **self.voltage_time_plot.styles
        )
        self.voltage_time_plot.setLabel(
            "bottom", "Time (s)", **self.voltage_time_plot.styles
        )

        #  add default data to plots
        y = range(0, 100)
        x = range(0, 100)
        self.waveform_plot.refresh(x, y)
        self.profile_plot.refresh(x, y)
        self.voltage_time_plot.refresh(x, y)
        self.app.processEvents()

    def plot(self, x, y, refresh_rate):
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
        self.app.processEvents()
        self.plot_ready = True

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
