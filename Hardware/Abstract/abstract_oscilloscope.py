from abc import  abstractmethod
from PyQt5.QtCore import *
from Utilities.useful_methods import bound
import numpy as np
from Hardware.Abstract.abstract_device import AbstractDevice

class AbstractOscilloscope(AbstractDevice):
        """
        """

        # Dummy code, replace when developing a hardware interface
        dummy_command_signal = pyqtSignal(str)

        def __init__(self, device_key = 'Keysight_Oscilloscope', config: dict = None, parent = None):
            super().__init__(device_key = device_key, config = config, parent = parent)
            self.connected = False
            self.fields_setup()

        @abstractmethod
        def fields_setup(self):
            self.range_mv = self.config[self.device_key]['range_mV']
            self.channel = self.config[self.device_key]['channel']
            self.averages = self.config[self.device_key]['averages']
            self.capture_period_ns = self.config[self.device_key]['capture_period_ns']
            self.signal_frequency_MHz = 4.2
            self.signal_period_ns = 1/self.signal_frequency_MHz * 1000
            self.cycles = self.config[self.device_key]['cycles']
            self.delay_cycles = self.config[self.device_key]['delay_cycles']
            self.captures = int(self.cycles*self.signal_period_ns/self.capture_period_ns)

        @property
        def configure(self, parameters:dict):
            for key in parameters:
                if key == 'range_mv':
                    self.range_mv = parameters[key]
                if key == 'channel':
                    self.channel = parameters[key]
                if key == 'averages':
                    self.averages = parameters[key]
                if key == 'capture_period_ns':
                    self.capture_period_ns = parameters[key]
                if key == 'signal_frequency_MHz':
                    self.signal_frequency_MHz = parameters[key]
                    self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                    self.captures = int(self.cycles*self.signal_period_ns/self.capture_period_ns)
                if key == 'cycles':
                    self.cycles = parameters[key]
                    self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                    self.captures = int(self.cycles * self.signal_period_ns / self.capture_period_ns)
                if key == 'delay_cycles':
                    self.delay_cycles = parameters[key]

        @abstractmethod
        def toggle_connection(self):
            if self.connected():
                return self.connect()
            else:
                return self.disconnect()

        @abstractmethod
        def connect_hardware(self):
            self.connected = True
            self.connected_signal.emit(self.connected)

        @abstractmethod
        def disconnect_hardware(self):
            self.connected = False
            self.connected_signal.emit(self.connected)

        @abstractmethod
        def capture(self, channel):
            start_time = self.delay_cycles*self.signal_period_ns
            end_time = start_time + self.captures * self.capture_period_ns
            time = np.linspace(start_time, end_time, self.captures)

            signal = np.sin(time)

            noise = np.random.rand(self.captures)*.1

            voltage = signal + noise

            return list(time), list(voltage)
