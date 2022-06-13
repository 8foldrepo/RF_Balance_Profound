import random
import time
from PyQt5.QtCore import QThread, QMutex, QWaitCondition, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication


class SimpleSensor:
    """Representation of a simple simulated sensor"""

    def __init__(self, name):
        self.name = name

    def get_reading(self):
        """waits between 0 and .1 seconds and returns a random number"""
        capture_time = random.random() / 10
        time.sleep(capture_time)
        return random.random()


class SimpleSensorThread(QThread):
    reading_signal = pyqtSignal(float)

    def __init__(self, sensor: SimpleSensor, parent=None):
        super().__init__(parent=parent)
        self.sensor = sensor
        self.capture_command = False
        self.ready = False
        self.mutex = QMutex()
        self.condition = None
        self.stay_alive = None
        self.start_time = None

    def run(self):
        QThread.currentThread().setObjectName(f"{self.sensor.name}_thread")
        self.start_time = time.time()
        self.stay_alive = True
        self.condition = QWaitCondition()
        self.mutex.lock()
        self.ready = True

        # Core event loop
        while self.stay_alive is True:
            # repeat every 1 milliseconds
            wait_bool = self.condition.wait(self.mutex, 1)
            self.reading_signal.emit(5)
            # As soon as the capture_command flag is true, capture the sensor
            if self.capture_command:
                self.capture()
                self.capture_command = False

            if self.stay_alive is False:
                break
        self.mutex.unlock()
        return super().run()

    def capture(self):
        self.ready = False
        print(f"Capturing in {QThread.currentThread().objectName()}")
        reading = self.sensor.get_reading()
        self.reading_signal.emit(reading)
        self.ready = True

    @pyqtSlot()
    def trigger_capture_slot(self):
        """Trigger a capture (which will initiate via the run loop of the sensor thread)"""
        print("inititating capture")
        self.capture_command = True


class SimpleRFBDataLogger(QThread):
    # Trigger a capture from all sensors at once
    trigger_capture_signal = pyqtSignal()

    def __init__(self, s1: SimpleSensor, s2: SimpleSensor, s3: SimpleSensor, parent=None):
        super().__init__(parent=parent)
        self.stay_alive = None
        self.app = QApplication.instance()
        # Encapsulates all data relevant to the RFB efficiency test Polled by the manager and shared with the
        # Ui thread by reference
        # Event loop control vars
        self.mutex = QMutex()
        self.sensor_mutex = QMutex()
        self.condition = QWaitCondition()
        QThread.currentThread().setObjectName("rfb_logger_thread")
        self.sensor_mutex.lock()
        self.sensor_mutex.unlock()

        # These should all have the same length and the readings should begin being acquired within ~1ms of each other
        self.awg_on_ray = list()
        self.times_s = list()
        self.s1_readings = list()
        self.s2_readings = list()
        self.s3_readings = list()

        self.awg_on = False
        self.s1_ready = True
        self.s2_ready = True
        self.s3_ready = True

        self.S1_Thread = SimpleSensorThread(sensor=s1)
        self.S2_Thread = SimpleSensorThread(sensor=s2)
        self.S3_Thread = SimpleSensorThread(sensor=s3)

        self.trigger_capture_signal.connect(self.S1_Thread.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.S2_Thread.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.S3_Thread.trigger_capture_slot)

        self.S1_Thread.reading_signal.connect(self.log_s1)
        self.S2_Thread.reading_signal.connect(self.log_s2)
        self.S3_Thread.reading_signal.connect(self.log_s3)

        self.S1_Thread.start(priority=QThread.HighPriority)
        self.S2_Thread.start(priority=QThread.HighPriority)
        self.S3_Thread.start(priority=QThread.HighPriority)

    def run(self) -> None:
        """
        Starts capturing data from the waveform generator, uses mutexes to prevent
        race condition. Also appends values to awg_on_ray and times_s.
        """
        # Setup event loop
        start_time = time.time()
        self.stay_alive = True
        self.mutex.lock()
        while self.stay_alive is True:
            self.condition.wait(self.mutex, 50)
            # Inside event loop
            if self.sensors_ready():
                # self.s1_ready = self.s2_ready = self.s3_ready = False
                time.sleep(.1)
                print("triggering capture")
                self.trigger_capture_signal.emit()

            if self.stay_alive is False:
                break

        self.mutex.unlock()
        return super().run()

    def sensors_ready(self) -> bool:
        """
        Tells the calling scope whether all the logged devices: the balance, forward power meter,
        and reverse power meter are ready
        """
        return self.s1_ready and self.s2_ready and self.s3_ready

    @pyqtSlot(float)
    def log_s1(self, reading_g):
        """
        appends a balance reading to the balance_readings_g list, as well as
        append a calculated acoustic power reading to acoustic_powers_w
        """
        self.s1_readings.append(reading_g)
        self.s1_ready = True

    @pyqtSlot(float)
    def log_s2(self, reading_w):
        """
        adds reading from waveform generator in watts to a list called
        f_meter_readings_w, a variable contained in the rfb_data_logger class
        """
        self.s2_readings.append(reading_w)
        self.s2_ready = True

    @pyqtSlot(float)
    def log_s3(self, reading_w):
        self.s3_readings.append(reading_w)
        self.s3_ready = True

    def quit(self):
        self.stay_alive = False
        try:
            super().quit()  # closes the thread
        except RuntimeError:
            pass


if __name__ == "__main__":
    logger = SimpleRFBDataLogger(s1=SimpleSensor("S1"), s2=SimpleSensor("S2"), s3=SimpleSensor("S3"))
    logger.start(priority=QThread.HighPriority)

    while True:
        time.sleep(1)
