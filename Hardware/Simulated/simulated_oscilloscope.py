import random
from abc import abstractmethod

import numpy as np
from termcolor import colored

from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope


class SimulatedOscilloscope(AbstractOscilloscope):
    """Class providing a crude simulation of an oscilloscope so programs can be tested without one"""

    def __init__(self, config: dict, device_key="Keysight_Oscilloscope", parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)
        self.connected = False
        self.fields_setup()

    @abstractmethod
    def fields_setup(self):
        self.range_mV = self.config[self.device_key]["range_mV"]
        self.channel = self.config[self.device_key]["channel"]
        self.averages = self.config[self.device_key]["averages"]
        self.capture_period_ns = 100
        self.signal_frequency_MHz = 4.2
        self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
        self.cycles = self.config[self.device_key]["cycles"]
        self.delay_cycles = self.config[self.device_key]["delay_cycles"]
        self.captures = int(
            self.cycles * self.signal_period_ns / self.capture_period_ns
        )

    def configure(self, parameters: dict):
        for key in parameters:
            if key == "range_mV":
                self.range_mV = parameters[key]
            if key == "channel":
                self.channel = parameters[key]
            if key == "averages":
                self.averages = parameters[key]
            if key == "capture_period_ns":
                self.capture_period_ns = parameters[key]
            if key == "signal_frequency_MHz":
                self.signal_frequency_MHz = parameters[key]
                self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                self.captures = int(self.cycles * self.signal_period_ns / self.capture_period_ns)
            if key == 'cycles':
                self.cycles = parameters[key]
                self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                self.captures = int(self.cycles * self.signal_period_ns / self.capture_period_ns)
            if key == 'delay_cycles':
                self.delay_cycles = parameters[key]

    def set_averaging(self, averages=1):
        pass

    def get_horizontal_scale_sec(self) -> float:
        return self.range_s

    def set_horizontal_scale_sec(self, seconds: float) -> None:
        self.range_s = 8 * seconds

    def get_horizontal_offset_sec(self) -> float:
        return self.offset_s

    def set_horizontal_offset_sec(self, seconds: float) -> None:
        self.offset_s = seconds

    def get_horizontal_range_sec(self) -> float:
        return self.range_s

    def set_horizontal_range_sec(self, seconds: float) -> None:
        self.range_s = seconds

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def capture(self, channel):
        if self.config["Debugging"]["simulate_oscilloscope_error"]:
            return None

        start_time = self.delay_cycles * self.signal_period_ns
        end_time = start_time + self.captures * self.capture_period_ns
        time = np.linspace(start_time, end_time, self.captures)

        signal = np.sin(time)
        noise = np.random.rand(self.captures) * 0.1
        voltage = signal + noise

        return list(time), list(voltage)

    def get_serial_number(self) -> str:
        return '"Simulated"'

    def autoset_oscilloscope_timebase(self):
        self.max_time_of_flight = self.config['Autoset timebase']["Max time of flight (us)"]
        self.min_time_of_flight = self.config['Autoset timebase']["Min time of flight (us)"]
        range_s = self.config['Autoset timebase']["Horizontal scale (us)"] * 10 ** -6
        time_of_flight_window = (self.max_time_of_flight - self.min_time_of_flight) / 1000000
        offset_s = self.min_time_of_flight / 1000000 + time_of_flight_window / 2
        self.set_horizontal_range_sec(range_s)
        self.set_horizontal_offset_sec(offset_s)

    def get_rms(self) -> float:
        return random.random()
