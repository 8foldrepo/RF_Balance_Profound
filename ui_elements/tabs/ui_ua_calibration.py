from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView, QApplication
from PyQt5.QtWidgets import QTableWidgetItem

from Hardware.ua_interface import UAInterface
from Widget_Library.widget_ua_calibration import Ui_Form
from ui_elements.my_qwidget import MyQWidget


class UACalibration(MyQWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.data = None
        self.main_window = None
        self.ua_interface = None
        self.setupUi(self)
        self.manager = None
        self.config = None

        self.high_frequency_mhz = float("nan")
        self.low_frequency_mhz = float("nan")

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.element_frequencies_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setEnabled(False)
        self.element_frequencies_table.setEnabled(False)

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def set_ua_interface(self, ua_interface_source):
        self.ua_interface = ua_interface_source
        self.ua_interface.cal_data_signal.connect(self.populate_results_table)
        self.read_from_ua_button.clicked.connect(self.ua_interface.read_data)

        try:
            self.main_window = self.parent().parent().parent().parent().parent()
        except Exception:
            self.main_window = self

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        self.read_from_ua_button.setEnabled(enabled)

    def get_high_frequency_Mhz(self) -> float:
        return float(self.tableWidget.item(5, 0).text())

    def get_low_frequency_Mhz(self) -> float:
        return float(self.tableWidget.item(4, 0).text())

    @pyqtSlot(list, int)
    def populate_results_table(self, data=None, status=None):
        if status == -1 or status == 2:
            self.main_window.dialog_critical(
                "UA not found, please connect UA to interface box and try again"
            )
            self.main_window.log(
                level="Error", message="No UA connected, plug one in and try again"
            )
            return
        # data, status = self.ua_interface.read_data() #todo is this line needed?
        if status == -2:
            self.main_window.dialog_critical(
                "WTFiB is not connected (check power and ethernet connection)"
            )
            self.main_window.log(
                level="Error", message="No UA connected, plug one in and try again"
            )
            return
        elif status == 0:
            self.tableWidget.setEnabled(True)
            self.element_frequencies_table.setEnabled(True)
            self.data = data

        status = 0

        for i in range(7):  # INFO: populates calibration data table
            item = QTableWidgetItem()
            item.setText(data[i])
            self.tableWidget.setItem(i, 0, item)

        item = QTableWidgetItem()
        item.setText("CalRead")
        self.tableWidget.setItem(7, 0, item)

        item = QTableWidgetItem()
        item.setText(str(status))
        self.tableWidget.setItem(8, 0, item)

        item = QTableWidgetItem()
        item.setText(data[7])
        self.tableWidget.setItem(9, 0, item)

        for i in range(10):  # INFO: populates low frequency column
            item = QTableWidgetItem()
            item.setText(data[i + 8])
            self.element_frequencies_table.setItem(i, 0, item)

        for i in range(10):  # INFO: populates high frequency column
            item = QTableWidgetItem()
            item.setText(data[i + 18])
            self.element_frequencies_table.setItem(i, 1, item)

        self.high_frequency_mhz = float(self.tableWidget.item(5, 0).text())
        self.low_frequency_mhz = float(self.tableWidget.item(4, 0).text())

    def dialog_critical(self, text):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Error")
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Critical)
        dlg.exec()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = UACalibration()
    ua_interface = UAInterface(config=None)
    ui.set_ua_interface(ua_interface)
    ui.show()
    sys.exit(app.exec_())
