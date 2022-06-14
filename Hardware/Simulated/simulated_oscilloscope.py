import random

import numpy as np

from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope


class SimulatedOscilloscope(AbstractOscilloscope):
    """Class providing a crude simulation of an oscilloscope so programs can be tested without one"""

    def __init__(self, config: dict, device_key="Keysight_Oscilloscope", parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)
        self.connected = False
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
        range_s = (self.config['Oscilloscope_timebase']["Horizontal scale (us)"] * 10 ** -6) * 8
        offset_s = self.config['Oscilloscope_timebase']["Time offset (us)"] * 10 ** -6
        self.set_horizontal_range_sec(range_s)
        self.set_horizontal_offset_sec(offset_s)

    def get_rms(self) -> float:
        return random.random()

    def reset(self) -> None:
        pass

    def set_to_defaults(self) -> None:
        pass

    def setup(self, channel: int, range_s: float, offset_s: float, autorange_v: float, range_v: float,
              ext_trigger: bool, average_count: int) -> None:
        pass

    def set_trigger(self, external: bool) -> None:
        pass

    def get_vertical_range_V(self, channel: int) -> float:
        return 1

    def set_vertical_range_V(self, channel: int, volts: float) -> None:
        pass

    def get_vertical_scale_V(self, channel: int) -> float:
        return 1

    def set_vertical_scale_V(self, volts_per_div: float, channel: int):
        pass

    def get_vertical_offset_V(self, channel: int) -> float:
        return 1

    def set_vertical_offset_V(self, channel: int, offset: float) -> None:
        pass

    def autoScale(self):
        pass

    def wrap_up(self):
        self.disconnect_hardware()
