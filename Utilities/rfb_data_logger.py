from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, pyqtSlot
import time as t
from Hardware.Abstract.abstract_balance import AbstractBalance
from Utilities.sensor_thread import SensorThread
from Hardware.Abstract.abstract_sensor import AbstractSensor
from Utilities.useful_methods import trim
from Utilities.formulas import calculate_power_from_balance_reading
from data_structures.rfb_data import RFBData


class RFBDataLogger(QThread):
    # Trigger a capture from all sensors at once
    trigger_capture_signal = pyqtSignal()

    Balance: AbstractBalance
    Forward_Power_Meter: AbstractSensor
    Reflected_Power_Meter: AbstractSensor

    rfb_data: RFBData

    def __init__(self, rfb_data, Balance: AbstractBalance, Forward_Power_Meter: AbstractSensor,
                 Reflected_Power_Meter: AbstractSensor, parent=None):
        super().__init__(parent=parent)
        # Encapsulates all data relevent to the RFB efficiency test Polled by the manager and shared with the
        # Ui thread by reference
        self.rfb_data = rfb_data
        # Event loop control vars
        self.mutex = QMutex()
        self.sensor_mutex = QMutex()
        self.condition = QWaitCondition()
        # QThread.currentThread().setObjectName("Manager_thread")
        self.sensor_mutex.lock()
        self.sensor_mutex.unlock()

        # These should all have the same length and the readings should begin being aquired within ~1ms of each other
        self.awg_on_ray = list()
        self.times_s = list()
        self.balance_readings_g = list()
        self.acoustic_powers_w = list()
        self.f_meter_readings_w = list()
        self.r_meter_readings_w = list()

        self.update_realtime_data()

        self.awg_on = False
        self.balance_ready = True
        self.f_meter_ready = True
        self.r_meter_ready = True

        self.BalanceThread = SensorThread(sensor=Balance)
        self.F_Meter_Thread = SensorThread(sensor=Forward_Power_Meter)
        self.R_Meter_Thread = SensorThread(sensor=Reflected_Power_Meter)
        self.thread_list = list()
        self.thread_list.append(self.BalanceThread)
        self.thread_list.append(self.F_Meter_Thread)
        self.thread_list.append(self.R_Meter_Thread)

        self.trigger_capture_signal.connect(self.BalanceThread.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.F_Meter_Thread.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.R_Meter_Thread.trigger_capture_slot)
        self.BalanceThread.reading_signal.connect(self.log_balance)
        self.F_Meter_Thread.reading_signal.connect(self.log_f_meter)
        self.R_Meter_Thread.reading_signal.connect(self.log_r_meter)

        self.BalanceThread.start(priority=QThread.HighPriority)
        self.F_Meter_Thread.start(priority=QThread.HighPriority)
        self.R_Meter_Thread.start(priority=QThread.HighPriority)

    def run(self) -> None:
        # Setup event loop
        start_time = t.time()
        self.stay_alive = True
        self.mutex.lock()
        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 50)

            # Inside event loop
            if self.sensors_ready():
                self.balance_ready = self.f_meter_ready = self.r_meter_ready = False
                current_time = t.time() - start_time
                #print(f"current_time in rfb_data_logger.py is {current_time}")
                self.trigger_capture_signal.emit()
                self.times_s.append(current_time)
                self.awg_on_ray.append(self.awg_on)
                self.update_realtime_data()

            if self.stay_alive is False:
                break

        self.mutex.unlock()
        return super().run()

    def sensors_ready(self):
        return self.balance_ready and self.f_meter_ready and self.r_meter_ready

    def update_realtime_data(self):
        # copy lists by value to avoid length mismatch race condition
        times_s = list(self.times_s)
        acoustic_powers_w = list(self.acoustic_powers_w)
        awg_on_ray = list(self.awg_on_ray)
        f_meter_readings_w = list(self.f_meter_readings_w)
        r_meter_readings_w = list(self.r_meter_readings_w)
        balance_readings_g = list(self.balance_readings_g)

        # Make sure these lists are the same length
        times_s, acoustic_powers_w, awg_on_ray, f_meter_readings_w, r_meter_readings_w, balance_readings_g = \
            trim([times_s, acoustic_powers_w, awg_on_ray, f_meter_readings_w, r_meter_readings_w, balance_readings_g])

        # package data to send it to the rfb ui tab
        # pass by value to avoid race condition
        self.rfb_data.times_s = times_s
        self.rfb_data.f_meter_readings_w = f_meter_readings_w
        self.rfb_data.r_meter_readings_w = r_meter_readings_w
        self.rfb_data.acoustic_powers_w = acoustic_powers_w
        self.rfb_data.awg_on_ray = awg_on_ray
        self.rfb_data.balance_readings_g = balance_readings_g

        self.rfb_data.update_realtime_data()

    @pyqtSlot(float)
    def log_balance(self, reading_g):

        # todo: remove this line
        if self.awg_on:
            reading_g = reading_g / 500 + .053
        else:
            reading_g = reading_g / 500

        self.balance_readings_g.append(reading_g)
        self.acoustic_powers_w.append(calculate_power_from_balance_reading(reading_g))
        self.balance_ready = True

    @pyqtSlot(float)
    def log_f_meter(self, reading_w):

        # todo: remove this block
        if self.awg_on:
            reading_w = reading_w / 50 + 1
        else:
            reading_w = reading_w / 50

        self.f_meter_readings_w.append(reading_w )
        self.f_meter_ready = True

    @pyqtSlot(float)
    def log_r_meter(self, reading_w):

        # todo: remove this block
        if self.awg_on:
            reading_w = reading_w  / 50 + .4
        else:
            reading_w = reading_w / 50

        self.r_meter_readings_w.append(reading_w)
        self.r_meter_ready = True

    @pyqtSlot(bool)
    def update_awg_on(self, on):
        self.awg_on = on

    def quit(self):
        self.stay_alive = False
        super().quit()
        print("Done quiting thread")