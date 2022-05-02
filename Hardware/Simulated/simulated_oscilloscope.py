from abc import abstractmethod

import numpy as np

from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope

"""Class providing a crude simulation of an oscilloscope so programs can be tested without one"""


class SimulatedOscilloscope(AbstractOscilloscope):
    def __init__(self, config: dict, device_key="Keysight_Oscilloscope", parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)
        self.connected = False
        self.fields_setup()

    @abstractmethod
    def fields_setup(self):
        self.range_mv = self.config[self.device_key]["range_mV"]
        self.channel = self.config[self.device_key]["channel"]
        self.averages = self.config[self.device_key]["averages"]
        self.capture_period_ns = self.config[self.device_key]["capture_period_ns"]
        self.signal_frequency_MHz = 4.2
        self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
        self.cycles = self.config[self.device_key]["cycles"]
        self.delay_cycles = self.config[self.device_key]["delay_cycles"]
        self.captures = int(
            self.cycles * self.signal_period_ns / self.capture_period_ns
        )

    def configure(self, parameters: dict):
        for key in parameters:
            if key == "range_mv":
                self.range_mv = parameters[key]
            if key == "channel":
                self.channel = parameters[key]
            if key == "averages":
                self.averages = parameters[key]
            if key == "capture_period_ns":
                self.capture_period_ns = parameters[key]
            if key == "signal_frequency_MHz":
                self.signal_frequency_MHz = parameters[key]
                self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                self.captures = int(
                    self.cycles * self.signal_period_ns / self.capture_period_ns
                )
            if key == "cycles":
                self.cycles = parameters[key]
                self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                self.captures = int(
                    self.cycles * self.signal_period_ns / self.capture_period_ns
                )
            if key == "delay_cycles":
                self.delay_cycles = parameters[key]

    def SetAveraging(self, averages=1):
        pass

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def capture(self, channel):
        start_time = self.delay_cycles * self.signal_period_ns
        end_time = start_time + self.captures * self.capture_period_ns
        time = np.linspace(start_time, end_time, self.captures)

        signal = np.sin(time)
        noise = np.random.rand(self.captures) * 0.1
        voltage = signal + noise

        return list(time), list(voltage)

    def get_serial_number(self) -> str:
        return '"Simulated"'
