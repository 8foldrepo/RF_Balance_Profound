import random
import sys
import time as t

from PyQt5.QtWidgets import QMainWindow, QApplication

from test import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.configure_signals()

    def configure_signals(self):
        self.pushButton.clicked.connect(self.run_routine)

    def capture_a(self):
        t.sleep(random.random())
        return random.random()

    def capture_b(self):
        t.sleep(random.random())
        return random.random()

    def capture_c(self):
        t.sleep(random.random())
        return random.random()

    def run_routine(self):
        start_time = t.time()

        a = list()
        b = list()
        c = list()

        while t.time() - start_time < 30:
            a.append(self.capture_a())
            b.append(self.capture_b())
            c.append(self.capture_c())
            print(f'Items in A: {len(a)}, Items in B: {len(b)}, Items in C: {len(c)}')

        finish_time = t.time()

        print(finish_time - start_time)
        print(len(c))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    I = MainWindow()
    app.setStyle("fusion")
    I.show()
    sys.exit(app.exec_())
