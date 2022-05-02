import random
import sys
import time as t

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QMutex, QWaitCondition
from PyQt5.QtWidgets import QMainWindow, QApplication

from test import Ui_MainWindow


class A(QThread):
    reading_signal = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Event loop control vars

    def run(self):
        self.stay_alive = True
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.mutex.lock()
        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 1)

            self.capture_a()

            if self.stay_alive is False:
                break
        self.mutex.unlock()
        return super().run()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        QThread.currentThread().setObjectName("A_thread")

    def capture_a(self):
        # 10% of the time
        if random.random() < .1:
            # Example of a failed read
            return None

        t.sleep(random.random())
        self.reading_signal.emit(random.random())


class B(QThread):
    reading_signal = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Event loop control vars

    def run(self):
        self.stay_alive = True
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.mutex.lock()
        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 1)

            self.capture_b()

            if self.stay_alive is False:
                break
        self.mutex.unlock()
        return super().run()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        QThread.currentThread().setObjectName("A_thread")

    def capture_b(self):
        # 10% of the time
        if random.random() < .1:
            # Example of a failed read
            return None

        t.sleep(random.random())
        self.reading_signal.emit(random.random())


class C(QThread):
    reading_signal = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Event loop control vars

    def run(self):
        self.stay_alive = True

        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.mutex.lock()
        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 1)

            self.capture_c()

            if self.stay_alive is False:
                break
        self.mutex.unlock()
        return super().run()

    def capture_c(self):
        t.sleep(random.random())
        self.reading_signal.emit(random.random())


class Data_Logger(QThread):
    capture_a_signal = pyqtSignal()
    capture_b_signal = pyqtSignal()
    capture_c_signal = pyqtSignal()

    a = list()
    b = list()
    c = list()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Event loop control vars
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # QThread.currentThread().setObjectName("Manager_thread")

        self.A = A()
        self.B = B()
        self.C = C()
        self.thread_list = list()
        self.thread_list.append(A)
        self.thread_list.append(B)
        self.thread_list.append(C)

        self.capture_a_signal.connect(self.A.capture_a)
        self.capture_b_signal.connect(self.B.capture_b)
        self.capture_c_signal.connect(self.C.capture_c)

        self.A.reading_signal.connect(self.log_a)
        self.B.reading_signal.connect(self.log_b)
        self.C.reading_signal.connect(self.log_c)
        self.A.start(priority=4)
        self.B.start(priority=4)
        self.C.start(priority=4)

    def run(self) -> None:
        print("Running")
        start_time = t.time()
        self.stay_alive = True

        self.mutex.lock()
        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 50)

            print(f'Items in A: {len(self.a)}, Items in B: {len(self.b)}, Items in C: {len(self.c)}')

            if t.time() - start_time > 30:
                print(f'Items in A: {len(self.a)}, Items in B: {len(self.b)}, Items in C: {len(self.c)}')
                self.stay_alive = False

            if self.stay_alive is False:
                break

        self.mutex.unlock()
        return super().run()

    @pyqtSlot(float)
    def log_a(self, reading):
        self.a.append(reading)

    @pyqtSlot(float)
    def log_b(self, reading):
        self.b.append(reading)

    @pyqtSlot(float)
    def log_c(self, reading):
        self.c.append(reading)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.configure_signals()
        self.logger = Data_Logger()
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
