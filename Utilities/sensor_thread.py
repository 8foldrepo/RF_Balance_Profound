import time as t

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, pyqtSlot

from Hardware.Abstract.abstract_sensor import AbstractSensor


class SensorThread(QThread):
    reading_signal = pyqtSignal(float)
    error_signal = pyqtSignal(str)

    def __init__(self, config, sensor: AbstractSensor, parent=None):
        super().__init__(parent=parent)
        self.name = sensor.device_key
        self.sensor = sensor
        self.config = config
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
            # Core event loop
            wait_bool = self.condition.wait(self.mutex, 1)

            if self.capture_command:
                # As soon as the capture_command flag is true, capture the sensor
                self.capture()
                self.capture_command = False

            if self.stay_alive is False:
                break
        self.mutex.unlock()
        return super().run()

    def capture(self):
        """Capture the sensor reading and emit it to the logger"""
        self.ready = False
        reading = float('nan')

        startTime = t.time()

        while t.time() - startTime < self.config["MT_Balance"]["timeout_s"]:
            reading = self.sensor.get_reading()

            if reading is not None:
                break

        if reading is None:
            self.error_signal.emit(f"Error capturing reading from {self.name}.")
            self.ready = True
            self.reading_signal.emit(None)
            return

        self.reading_signal.emit(reading)
        self.ready = True

    @pyqtSlot()
    def trigger_capture_slot(self):
        """Trigger a capture (which will initate via the run loop of the sensor thread)"""
        self.capture_command = True
