import random
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, pyqtSlot
import time as t
from Hardware.Abstract.abstract_sensor import AbstractSensor


class SensorThread(QThread):
    reading_signal = pyqtSignal(float)


    def __init__(self, sensor: AbstractSensor, parent=None):
        super().__init__(parent=parent)
        self.name = sensor.device_key
        self.sensor = sensor

        self.capture_command = False
        self.ready = False
        self.mutex = QMutex()
        self.condition = None
        self.stay_alive = None
        self.start_time = None

    def run(self):
        QThread.currentThread().setObjectName(f"{self.name}_thread")
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
        #print(f"Beginning capture of {QThread.currentThread().objectName()}, time = {t.time()-self.start_time}, index = {self.index}")
        reading = None
        while reading == None:
            reading = self.sensor.get_reading()

        self.reading_signal.emit(reading)
        #print(f"Finishing capture of {QThread.currentThread().objectName()}, time = {t.time() - self.start_time}, index = {self.index}")
        self.ready = True

    # Trigger a capture
    @pyqtSlot()
    def trigger_capture_slot(self):
        self.capture_command = True
