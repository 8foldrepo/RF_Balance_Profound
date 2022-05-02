from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, pyqtSlot
import time as t

from Utilities.sensor_thread import SensorThread


class RFBDataLogger(QThread):
    # Float is time in s, int is the index of the capture
    capture_time_signal = pyqtSignal(float, int)

    a = list()
    b = list()
    c = list()

    a_ready = True
    b_ready = True
    c_ready = True

    times_s = list()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Event loop control vars
        self.mutex = QMutex()
        self.sensor_mutex = QMutex()

        self.condition = QWaitCondition()
        # QThread.currentThread().setObjectName("Manager_thread")
        self.sensor_mutex.lock()
        self.sensor_mutex.unlock()
        self.A = SensorThread(device_key='A')
        self.B = SensorThread(device_key='B')
        self.C = SensorThread(device_key='C')
        self.thread_list = list()
        self.thread_list.append(self.A)
        self.thread_list.append(self.B)
        self.thread_list.append(self.C)

        self.capture_time_signal.connect(self.A.capture_slot)
        self.capture_time_signal.connect(self.B.capture_slot)
        self.capture_time_signal.connect(self.C.capture_slot)
        self.A.reading_signal.connect(self.log_a)
        self.B.reading_signal.connect(self.log_b)
        self.C.reading_signal.connect(self.log_c)

        self.A.start(priority=QThread.HighPriority)
        self.B.start(priority=QThread.HighPriority)
        self.C.start(priority=QThread.HighPriority)

    def run(self) -> None:
        print("Running")
        start_time = t.time()
        self.stay_alive = True

        self.mutex.lock()
        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 50)

            if t.time() - start_time < 30 and self.sensors_ready():
                self.a_ready = self.b_ready = self.c_ready = False
                current_time = t.time()-start_time
                print(current_time)

                self.capture_time_signal.emit(current_time, len(self.times_s))
                self.times_s.append(current_time)
                print(f'Items in A: {len(self.a)}, Items in B: {len(self.b)}, Items in C: {len(self.c)}')

            if self.stay_alive is False:
                break

        self.mutex.unlock()
        return super().run()

    def sensors_ready(self):
        return self.a_ready and self.b_ready and self.c_ready

    @pyqtSlot(float)
    def log_a(self, reading):
        self.a.append(reading)
        self.a_ready = True

    @pyqtSlot(float)
    def log_b(self, reading):
        self.b.append(reading)
        self.b_ready = True

    @pyqtSlot(float)
    def log_c(self, reading):
        self.c.append(reading)
        self.c_ready = True