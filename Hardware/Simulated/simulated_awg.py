from PyQt5.QtCore import pyqtSignal

from Hardware.Abstract.abstract_awg import AbstractAWG
from Utilities.load_config import *


class SimulatedAWG(AbstractAWG):
    output_signal = pyqtSignal(bool)

    def __init__(self, config=None, device_key="Keysight_AWG", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        self.state = dict()
        self.fields_setup()
        self.set_to_defaults()

    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

    def set_to_defaults(self):
        self.setup(
            frequency_Hz=self.config[self.device_key]["frequency_Hz"],
            amplitude_V=self.config[self.device_key]["amplitude_V"],
            burst=self.config[self.device_key]["burst_on"],
            burst_cycles=self.config[self.device_key]["burst_cycles"],
            ext_trig=self.config[self.device_key]["trig_out"],
            burst_period_s=self.config[self.device_key]["burst_period_s"],
            offset_V=self.config[self.device_key]["offset_V"],
            output=False,
            output_Impedance=self.config[self.device_key]["output_Impedance"],
        )

    def connect_hardware(self):
        self.setup(frequency_Hz=4290000, amplitude_V=0.1)
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(False)

    def setup(self, frequency_Hz, amplitude_V, burst=False, ext_trig=False, burst_period_s=.00001, burst_cycles=50,
              offset_V=0, output=False, output_Impedance=50):
        """Sets all settings of the awg with one command and wait until it is done configuring"""
        self.set_output(output)
        self.set_frequency_hz(frequency_Hz)
        self.set_amplitude_v(amplitude_V)
        self.set_cycles(burst_cycles)
        self.set_burst(burst)
        self.SetTriggerInput(external=ext_trig, period_s=burst_period_s)
        self.set_offset_v(offset_V)
        self.set_output_impedance(output_Impedance)

        self.wait_til_complete()

    def get_state(self):
        """Inquires all key AWG settings, and returns a dictionary containing their names and values"""
        self.get_output()
        self.get_frequency_hz()
        self.get_amplitude_v()
        self.get_burst()
        self.GetTriggerInput()
        self.get_offset_v()
        self.get_output_impedance()
        return self.state

    def reset(self):
        self.set_to_defaults()
        self.wait_til_complete()

    def wait_til_complete(self):
        pass

    def set_output(self, on: bool):
        """Turns the output on or off"""
        self.state["on"] = on
        self.output_signal.emit(on)

    def get_output(self):
        self.output_signal.emit(self.state["on"])
        return self.state["on"]

    def set_frequency_hz(self, frequency_Hz):
        """Sets the frequency of the signal"""
        self.state["frequency_Hz"] = frequency_Hz
        self.frequency_signal.emit(frequency_Hz / 1000000)

    def get_frequency_hz(self):
        return self.state["frequency_Hz"]

    def set_amplitude_v(self, amplitude):
        """Sets the peak to peak amplitude of the waveform in volts"""
        self.state["amplitude_V"] = amplitude

    def get_amplitude_v(self):
        return self.state["amplitude_V"]

    def set_offset_v(self, offset):
        """Sets the dc offset of the waveform in volts"""
        pass

    def get_offset_v(self):
        pass

    def SetFunction(self, func="SIN"):
        pass

    def GetFunction(self):
        pass

    def SetTriggerInput(self, external: bool, period_s=0.000010, delay_s=0):
        """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""
        pass

    def GetTriggerInput(self):
        """Returns info about the trigger: source, delay_s, period_s"""

        pass

    def set_burst(self, on=True):
        self.state["burst_on"] = on

    def get_burst(self):
        """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""

        return self.state["burst_on"], self.state["burst_cycles"]

    def set_output_impedance(self, impedance_ohms=50, HiZ=False):
        if HiZ:
            self.state["output impedance"] = impedance_ohms
        else:
            self.state["output impedance"] = 10000000

    def get_output_impedance(self):
        return self.state["output impedance"]

    def set_phase_degrees(self, phase_degrees=0):
        self.state["phase degrees"] = phase_degrees

    def get_phase_degrees(self):
        return self.state["phase degrees"]

    def set_cycles(self, cycles):
        self.state["burst_cycles"] = cycles

    def get_cycles(self):
        return self.state["burst_cycles"]

    def set_trigger_output(self, trigger_out: bool):
        """Returns the last known state of the device. Use getstate to inquire the state before calling"""

        pass

    def get_serial_number(self) -> str:
        return '"Simulated"'

    def wrap_up(self):
        self.set_output(False)
        self.disconnect_hardware()

    def __str__(self):
        self.get_state()
        return "Waveform Generator\nSettings:\n" + str(self.state)


if __name__ == "__main__":
    awg = SimulatedAWG()
    awg.connect_hardware()
    awg.reset()
    print(awg)
    awg.setup(frequency_Hz=4290000, amplitude_V=.2, burst=False, burst_cycles=50, ext_trig=False,
              burst_period_s=.10, offset_V=0, output=True, output_Impedance=50)
    print(awg)
