import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from Utilities.rfb_data_logger import RFBDataLogger
from test import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.configure_signals()
        self.logger = RFBDataLogger()
        self.thread_list = list()
        self.thread_list.append(self.logger)

    def configure_signals(self):
        self.pushButton.clicked.connect(self.run_routine)

    def run_routine(self):
        self.logger.start(priority=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    I = MainWindow()
    app.setStyle("fusion")
    I.show()
    sys.exit(app.exec_())
