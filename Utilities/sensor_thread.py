import random
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, pyqtSlot
import time as t

class SensorThread(QThread):
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
        self.start_time = t.time()
        self.stay_alive = True
        self.condition = QWaitCondition()
        self.mutex.lock()
        self.ready = True
        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 1)

            if self.capture_command:
                self.capture()
                self.capture_command = False

            if self.stay_alive is False:
                break
        self.mutex.unlock()
        return super().run()

    def capture(self):
        self.ready = False
        print(f"Beginning capture of {self.name}, time = {t.time()-self.start_time}, index = {self.index}")
        reading = random.random()
        self.reading_signal.emit(reading)
        print(f"Finishing capture of {self.name}, time = {t.time() - self.start_time}, index = {self.index}")
        self.ready = True

    # Float is time in s, int is the index of the capture
    @pyqtSlot(float, int)
    def capture_slot(self, time_s, index):
        self.index = index
        self.capture_command = True
