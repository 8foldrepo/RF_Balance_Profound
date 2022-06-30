import time as t

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QMutex, QWaitCondition, pyqtSlot
from PyQt5.QtWidgets import QApplication

from Hardware.Abstract.abstract_balance import AbstractBalance
from Hardware.Abstract.abstract_sensor import AbstractSensor
from Utilities.formulas import calculate_power_from_balance_reading
from Utilities.sensor_thread import SensorThread
from Utilities.useful_methods import trim
from data_structures.rfb_data import RFBData


class RFBDataLogger(QThread):
    # INFO: Trigger a capture from all sensors at once
    # needed for communication with the three power meters in parallel and being synchronized
    trigger_capture_signal = QtCore.pyqtSignal()
    error_signal = QtCore.pyqtSignal(str)

    Balance: AbstractBalance
    Forward_Power_Meter: AbstractSensor
    Reflected_Power_Meter: AbstractSensor
    rfb_data: RFBData

    # noinspection PyTypeChecker
    def __init__(self, rfb_data, balance: AbstractBalance, forward_power_meter: AbstractSensor,
                 reflected_power_meter: AbstractSensor, config, parent=None):
        super().__init__(parent=parent)
        self.stay_alive = None  # initialize stay alive variable
        self.app = QApplication.instance()
        self.config = config
        # Encapsulates all data relevant to the RFB efficiency test Polled by the manager and shared with the
        # Ui thread by reference
        self.rfb_data = rfb_data
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
        self.balance_readings_g = list()
        self.acoustic_powers_w = list()
        self.f_meter_readings_w = list()
        self.r_meter_readings_w = list()

        self.update_realtime_data()

        self.awg_on = False
        self.balance_ready = True
        self.f_meter_ready = True
        self.r_meter_ready = True

        self.Balance_Thread = SensorThread(config=self.config, sensor=balance)
        self.F_Meter_Thread = SensorThread(config=self.config, sensor=forward_power_meter)
        self.R_Meter_Thread = SensorThread(config=self.config, sensor=reflected_power_meter)
        self.thread_list = list()
        self.thread_list.append(self.Balance_Thread)
        self.thread_list.append(self.F_Meter_Thread)
        self.thread_list.append(self.R_Meter_Thread)

        self.trigger_capture_signal.connect(self.Balance_Thread.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.F_Meter_Thread.trigger_capture_slot)
        self.trigger_capture_signal.connect(self.R_Meter_Thread.trigger_capture_slot)
        self.Balance_Thread.reading_signal.connect(self.log_balance)
        self.F_Meter_Thread.reading_signal.connect(self.log_f_meter)
        self.R_Meter_Thread.reading_signal.connect(self.log_r_meter)
        self.Balance_Thread.error_signal.connect(self.report_error)
        self.F_Meter_Thread.error_signal.connect(self.report_error)
        self.R_Meter_Thread.error_signal.connect(self.report_error)

        self.Balance_Thread.start(priority=QThread.HighPriority)
        self.F_Meter_Thread.start(priority=QThread.HighPriority)
        self.R_Meter_Thread.start(priority=QThread.HighPriority)

    def run(self) -> None:
        """
        Starts capturing data from the waveform generator, uses mutexes to prevent
        race condition. Also appends values to awg_on_ray and times_s.
        """
        # Setup event loop
        start_time = t.time()  # capture current time
        self.stay_alive = True
        self.mutex.lock()
        while self.stay_alive is True:
            self.condition.wait(self.mutex, 50)

            # Inside event loop
            if self.sensors_ready():
                self.balance_ready = self.f_meter_ready = self.r_meter_ready = False
                current_time = t.time() - start_time
                self.times_s.append(current_time)
                self.awg_on_ray.append(self.awg_on)
                self.trigger_capture_signal.emit()
                self.update_realtime_data()

            if self.stay_alive is False:
                break

        self.mutex.unlock()
        return super().run()

    @pyqtSlot(str)
    def report_error(self, error_str) -> None:
        """Emits an error signal to be shown to the user. This also triggers an interrupt action in Manager"""
        self.error_signal.emit(error_str)

    def sensors_ready(self) -> bool:
        """
        Tells the calling scope whether all the logged devices: the balance, forward power meter,
        and reverse power meter are ready
        """
        return self.balance_ready and self.f_meter_ready and self.r_meter_ready

    def update_realtime_data(self) -> None:
        """copy lists by value to avoid length mismatch race condition"""

        # create method contained variables that mirror class-wide variables
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
    def log_balance(self, reading_g: float):
        """
        appends a balance reading to the balance_readings_g list, as well as
        append a calculated acoustic power reading to acoustic_powers_w

        :param reading_g: Balance reading in grams (float)
        """
        if reading_g > 1:
            pass  # todo: remove

        self.balance_readings_g.append(reading_g)
        self.acoustic_powers_w.append(calculate_power_from_balance_reading(reading_g))
        self.balance_ready = True

    @pyqtSlot(float)
    def log_f_meter(self, reading_w: float) -> None:
        """
        adds reading from waveform generator in watts to a list called
        f_meter_readings_w, a variable contained in the rfb_data_logger class

        :param reading_w: forward power reading in watts
        """

        self.f_meter_readings_w.append(reading_w)
        self.f_meter_ready = True

    @pyqtSlot(float)
    def log_r_meter(self, reading_w: float) -> None:
        """
        If the AWG is on, updates the internal reading variable to passed variable / 50 + .1; if off: same as
        previous but without adding .1; Passed value is appended to list of reverse readings and reverse meter ready
        flag is set to true

        :param reading_w: Reverse power meter reading in watts
        """

        self.r_meter_readings_w.append(reading_w)
        self.r_meter_ready = True

    @pyqtSlot(bool)
    def update_awg_on(self, on: bool):
        """
        Set the boolean awg_on flag to passed value

        :param on: Should represent whether the AWG is on/active or not
        """
        self.awg_on = on

    def quit(self) -> None:
        """
        Sets the stay alive flag to false, and issues a close thread command while excepting runtime errors
        """
        self.stay_alive = False
        try:
            super().quit()  # closes the thread
        except RuntimeError:
            pass
