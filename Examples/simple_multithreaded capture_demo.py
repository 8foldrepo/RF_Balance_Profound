import random
import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QWaitCondition, QMutex
from PyQt5.QtWidgets import QMainWindow, QApplication
from Examples.test import Ui_MainWindow


class SimpleRFBDataLogger(QThread):
    """A simplified example of how multithreading is used in the measure_element_efficiency_rfb method"""

    # Float is time in s, int is the index of the capture
    trigger_capture_signal = pyqtSignal(float, int)

    # Lists containing readings from 3 different sensors, they all share the same time array
    a = list()
    b = list()
    c = list()
    times_s = list()

    # Variables keeping track of when the sensors are ready for the next capture
    a_ready = True
    b_ready = True
    c_ready = True

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Event loop control vars
        self.mutex = QMutex()
        self.sensor_mutex = QMutex()
        self.condition = QWaitCondition()
        # QThread.currentThread().setObjectName("Manager_thread")
        self.sensor_mutex.lock()
        self.sensor_mutex.unlock()

        # Create the sensor threads, connect the trigger capture signal, and reading signal, and start the threads
        self.A = SimpleSensorThread(device_key='A')
        self.B = SimpleSensorThread(device_key='B')
        self.C = SimpleSensorThread(device_key='C')
        self.trigger_capture_signal.connect(self.A.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.B.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.C.trigger_capture_slot)
        self.A.reading_signal.connect(self.log_a)
        self.B.reading_signal.connect(self.log_b)
        self.C.reading_signal.connect(self.log_c)
        self.A.start(priority=QThread.HighPriority)
        self.B.start(priority=QThread.HighPriority)
        self.C.start(priority=QThread.HighPriority)

    def run(self) -> None:
        print("Running")
        start_time = time.time()
        stay_alive = True
        self.mutex.lock()
        while stay_alive is True:
            # Core event loop of logger

            # Repeat every 1 ms
            wait_bool = self.condition.wait(self.mutex, 1)
            if time.time() - start_time < 30 and self.sensors_ready():
                current_time = time.time() - start_time
                self.trigger_capture_signal.emit(current_time, len(self.times_s))
                self.a_ready = self.b_ready = self.c_ready = False

                # Keep track of the times captures were initiated
                self.times_s.append(current_time)

                # Print the number of items and current time for demonstration
                print(f"Capture time: {'%.2f' % current_time}")
                print(f'Items in A: {len(self.a)}, Items in B: {len(self.b)}, Items in C: {len(self.c)}')
            # Setting stay_alive to false with a slot is a way to end the logger prematurely
            if stay_alive is False:
                break

        print(f'Items in A: {len(self.a)}, Items in B: {len(self.b)}, Items in C: {len(self.c)}')
        self.mutex.unlock()
        return super().run()

    def sensors_ready(self):
        """Returns true if all of the sensors are ready"""
        return self.a_ready and self.b_ready and self.c_ready

    @pyqtSlot(float)
    def log_a(self, reading: float):
        """If sensor A emits a reading, add it to the list and flag the sensor as ready to capture again"""
        self.a.append(reading)
        self.a_ready = True

    @pyqtSlot(float)
    def log_b(self, reading: float):
        """If sensor B emits a reading, add it to the list and flag the sensor as ready to capture again"""
        self.b.append(reading)
        self.b_ready = True

    @pyqtSlot(float)
    def log_c(self, reading: float):
        """If sensor C emits a reading, add it to the list and flag the sensor as ready to capture again"""
        self.c.append(reading)
        self.c_ready = True

class SimpleSensorThread(QThread):
    """Simplified version of a sensor thread"""
    reading_signal = pyqtSignal(float)
    capture_command = False

    def __init__(self, device_key, parent=None):
        super().__init__(parent=parent)
        self.name = device_key
        self.ready = False
        QThread.currentThread().setObjectName(f"{self.name}_thread")
        self.mutex = QMutex()
        self.condition = None
        self.stay_alive = None
        self.start_time = None

    def run(self):
        self.start_time = time.time()
        self.stay_alive = True
        self.condition = QWaitCondition()
        self.mutex.lock()
        self.ready = True
        while self.stay_alive is True:
            # Core event loop

            wait_bool = self.condition.wait(self.mutex, 1)

            # If capture flag has been activated by the signal from the logger
            if self.capture_command:
                self.capture()
                self.capture_command = False

            if self.stay_alive is False:
                break
        self.mutex.unlock()
        return super().run()

    def capture(self):
        #
        self.ready = False
        # print(f"Beginning capture of {self.name}, time = {time.time() - self.start_time}, index = {self.index}")
        #reading = random.random()

        #time.sleep(random.random() / 20)
        self.reading_signal.emit(1)
        # print(f"Finishing capture of {self.name}, time = {time.time() - self.start_time}, index = {self.index}")
        self.ready = True

    # Float is time in s, int is the index of the capture
    @pyqtSlot(float, int)
    def trigger_capture_slot(self, time_s, index):
        """If a signal from the logger is received, capture upon the next iteration of the run loop"""
        self.index = index
        self.capture_command = True


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.configure_signals()
        self.logger = SimpleRFBDataLogger()
        self.thread_list = list()
        self.thread_list.append(self.logger)

    def configure_signals(self):
        self.pushButton.clicked.connect(self.run_routine)

    def run_routine(self):
        self.logger.start(priority=QThread.HighPriority)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    I = MainWindow()
    app.setStyle("fusion")
    I.show()
    sys.exit(app.exec_())
