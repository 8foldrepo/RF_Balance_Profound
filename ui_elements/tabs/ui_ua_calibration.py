from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QTableWidgetItem

from Hardware.ua_interface import UAInterface
from Widget_Library.widget_ua_calibration import Ui_Form
from ui_elements.my_qwidget import MyQWidget


class UACalibration(MyQWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ua_interface = None
        self.setupUi(self)
        self.manager = None
        self.config = None

        self.High_Frequency_MHz = float("nan")
        self.Low_Frequency_MHz = float("nan")

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def set_ua_interface(self, ua_interface):
        self.ua_interface = ua_interface
        self.ua_interface.cal_data_signal.connect(self.populate_results_table)
        self.read_from_ua_button.clicked.connect(self.ua_interface.read_data)

        try:
            self.main_window = self.parent().parent().parent().parent().parent()
        except:
            self.main_window = self

    def get_high_frequecy_Mhz(self) -> float:
        return float(self.tableWidget.item(5, 0).text())

    def get_low_frequecy_Mhz(self) -> float:
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
        # data, status = self.ua_interface.read_data()
        if status == -2:
            self.main_window.dialog_critical(
                "wtfib is not connected (check power and ethernet connection)"
            )
            self.main_window.log(
                level="Error", message="No UA connected, plug one in and try again"
            )
            return
        elif status == 0:
            self.data = data

        status = 0

        for i in range(7):
            item = QTableWidgetItem()
            item.setText(data[i])
            self.tableWidget.setItem(i, 0, item)

        item = QTableWidgetItem()
        item.setText("CalRead")
        self.tableWidget.setItem(7, 0, item)

        item = QTableWidgetItem()
        item.setText(str(status))
        self.tableWidget.setItem(8, 0, item)

        for i in range(10):
            item = QTableWidgetItem()
            item.setText(data[i + 7])
            self.tableWidget.setItem(i, 1, item)

        for i in range(10):
            item = QTableWidgetItem()
            item.setText(data[i + 17])
            self.tableWidget.setItem(i, 2, item)

        self.High_FrequencyMHz = float(self.tableWidget.item(5, 0).text())
        self.Low_FrequencyMHz = float(self.tableWidget.item(4, 0).text())

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
