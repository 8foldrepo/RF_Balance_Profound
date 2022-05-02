from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, pyqtSlot
import time as t
from Hardware.Abstract.abstract_balance import AbstractBalance
from Utilities.formulas import (
    calculate_power_from_balance_reading,
    calculate_random_uncertainty_percent,
    calculate_total_uncertainty_percent,
)
from Utilities.sensor_thread import SensorThread
from Hardware.Abstract.abstract_sensor import AbstractSensor
from Utilities.useful_methods import get_awg_on_values, get_awg_off_values


class RFBDataLogger(QThread):
    # Trigger a capture from all sensors at once
    trigger_capture_signal = pyqtSignal()

    Balance: AbstractBalance
    Forward_Power_Meter: AbstractSensor
    Reflected_Power_Meter: AbstractSensor

    def __init__(
        self,
        Balance: AbstractBalance,
        Forward_Power_Meter: AbstractSensor,
        Reflected_Power_Meter: AbstractSensor,
        parent=None,
    ):
        super().__init__(parent=parent)
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

        # Encapsulates all data to be displayed in the RFB tab. Polled by the manager and shared with the
        # Ui thread by reference
        self.rfb_args = dict()
        self.update_ui_data()

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

        print("Beginning thread")

    def run(self) -> None:
        print("Running")
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
                print(current_time)
                self.trigger_capture_signal.emit()
                self.times_s.append(current_time)
                self.awg_on_ray.append(self.awg_on)
                print(
                    f"Items in A: {len(self.balance_readings_g)}, Items in B: {len(self.f_meter_readings_w)}, Items in C: {len(self.r_meter_readings_w)}"
                )
                self.update_ui_data()

            if self.stay_alive is False:
                break

        self.mutex.unlock()
        return super().run()

    def sensors_ready(self):
        return self.balance_ready and self.f_meter_ready and self.r_meter_ready

    def update_ui_data(self):
        # package data to send it to the rfb ui tab
        acoustic_power_on_data = get_awg_on_values(
            self.acoustic_powers_w, self.awg_on_ray
        )
        acoustic_power_off_data = get_awg_off_values(
            self.acoustic_powers_w, self.awg_on_ray
        )
        if len(acoustic_power_off_data) != 0:
            acoustic_power_off_mean = sum(acoustic_power_off_data) / len(
                acoustic_power_off_data
            )
        else:
            acoustic_power_off_mean = float("nan")

        if len(acoustic_power_on_data) != 0:
            acoustic_power_on_mean = sum(acoustic_power_on_data) / len(
                acoustic_power_on_data
            )
        else:
            acoustic_power_on_mean = float("nan")
        self.rfb_args["acoustic_power_off_mean"] = acoustic_power_off_mean
        self.rfb_args["acoustic_power_on_mean"] = acoustic_power_on_mean
        self.rfb_args["times_s"] = self.times_s
        self.rfb_args["forward_w"] = self.f_meter_readings_w
        self.rfb_args["reflected_w"] = self.r_meter_readings_w
        self.rfb_args["acoustic_w"] = self.acoustic_powers_w
        self.rfb_args["awg_on"] = self.awg_on_ray
        try:
            self.rfb_args["grams"] = self.balance_readings_g[
                len(self.balance_readings_g) - 1
            ]
        except IndexError:
            self.rfb_args["grams"] = float("nan")
        try:
            self.rfb_args["forward_power_w"] = self.f_meter_readings_w[
                len(self.f_meter_readings_w) - 1
            ]
        except IndexError:
            self.rfb_args["forward_power_w"] = float("nan")
        try:
            self.rfb_args["reflected_power_w"] = self.r_meter_readings_w[
                len(self.r_meter_readings_w) - 1
            ]
        except IndexError:
            self.rfb_args["reflected_power_w"] = float("nan")
        self.rfb_args["p_on_rand_unc"] = calculate_random_uncertainty_percent(
            acoustic_power_on_data
        )
        self.rfb_args["p_on_total_unc"] = calculate_total_uncertainty_percent(
            acoustic_power_on_data
        )
        self.rfb_args["p_off_rand_unc"] = calculate_random_uncertainty_percent(
            acoustic_power_off_data
        )
        self.rfb_args["p_off_total_unc"] = calculate_total_uncertainty_percent(
            acoustic_power_off_data
        )
        self.rfb_args["p_com_rand_unc"] = calculate_random_uncertainty_percent(
            self.acoustic_powers_w
        )
        self.rfb_args["p_com_total_unc"] = calculate_total_uncertainty_percent(
            self.acoustic_powers_w
        )

    @pyqtSlot(float)
    def log_balance(self, reading_g):
        self.balance_readings_g.append(reading_g)
        self.acoustic_powers_w.append(calculate_power_from_balance_reading(reading_g))
        self.balance_ready = True

    @pyqtSlot(float)
    def log_f_meter(self, reading_w):
        self.f_meter_readings_w.append(reading_w)
        self.f_meter_ready = True

    @pyqtSlot(float)
    def log_r_meter(self, reading_w):
        self.r_meter_readings_w.append(reading_w)
        self.r_meter_ready = True

    @pyqtSlot(bool)
    def update_awg_on(self, on):
        self.awg_on = on

    def trim(self):
        min_length = min(
            len(self.times_s),
            len(self.r_meter_readings_w),
            len(self.balance_readings_g),
            len(self.f_meter_readings_w),
            len(self.acoustic_powers_w),
        )
        self.times_s = self.times_s[0:min_length]
        self.f_meter_readings_w = self.f_meter_readings_w[0:min_length]
        self.r_meter_readings_w = self.r_meter_readings_w[0:min_length]
        self.acoustic_powers_w = self.acoustic_powers_w[0:min_length]
        self.balance_readings_g = self.balance_readings_g[0:min_length]

    def quit(self):
        self.trim()

        self.stay_alive = False
        super().quit()
