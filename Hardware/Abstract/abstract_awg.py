from abc import abstractmethod
from typing import Tuple, Union

from PyQt5.QtCore import pyqtSignal

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractAWG(AbstractDevice):
    output_signal = pyqtSignal(bool)
    frequency_signal = pyqtSignal(float)
    state: dict

    def __init__(self, config=None, device_key="Keysight_AWG", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

    @abstractmethod
    def set_to_defaults(self):
        """Call self.setup using config file settings"""
        ...

    @abstractmethod
    def setup(self, frequency_Hz: float, amplitude_V: float, burst: bool, ext_trig: bool, burst_period_s: float,
              burst_cycles: int, output: bool, output_Impedance: int, offset_V: float):
        """Sets all settings of the awg with one command and wait until it is done configuring"""
        self.set_output(output)
        self.set_frequency_hz(frequency_Hz)
        self.set_amplitude_v(amplitude_V)
        self.set_cycles(burst_cycles)
        self.set_burst(burst)
        self.SetTriggerOutput(external=ext_trig, period_s=burst_period_s, delay_s=0)
        self.set_offset_v(offset_V)
        self.set_output_impedance(output_Impedance, HiZ=False)

    @abstractmethod
    def get_state(self):
        """Inquires all key AWG settings, and returns a dictionary containing their names and values"""
        self.get_output()
        self.get_frequency_hz()
        self.get_amplitude_v()
        self.get_burst()
        self.GetTriggerOutput()
        self.get_offset_v()
        self.get_output_impedance()
        return self.state

    @abstractmethod
    def reset(self) -> None:
        """Sends the reset signal to the acoustic wave generator"""
        ...

    @abstractmethod
    def wait_til_complete(self) -> None:
        """Sends the identify signal to the AWG and attempts to read the response"""
        ...

    @abstractmethod
    def set_output(self, on: bool) -> None:
        """Turns the output on or off"""
        ...

    @abstractmethod
    def get_output(self) -> str:
        """Returns the pending output data from the AWG"""
        ...

    @abstractmethod
    def set_frequency_hz(self, frequency: float):
        """Sets the frequency of the signal"""
        ...

    @abstractmethod
    def get_frequency_hz(self) -> float:
        """Retrieves the frequency of the AWG in hertz (float)"""
        ...

    @abstractmethod
    def set_amplitude_v(self, amplitude: float) -> None:
        """Sets the peak to peak amplitude of the waveform in volts"""
        ...

    @abstractmethod
    def get_amplitude_v(self) -> float:
        """Sets the dc offset of the waveform in volts"""
        ...

    @abstractmethod
    def set_offset_v(self, offset: float) -> None:
        """sets the vertical offset of the AWG in volts"""
        ...

    @abstractmethod
    def get_offset_v(self) -> float:
        """retrieves the vertical offset of the AWG in volts (float)"""
        ...

    @abstractmethod
    def set_burst(self, on: bool) -> None:
        """Simple method to toggle the burst mode of the AWG when given a boolean parameter"""
        self.state["burst_on"] = on

    @abstractmethod
    def get_burst(self) -> Tuple[bool, int]:
        """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""
        return self.state["burst_on"], self.state["burst_cycles"]

    @abstractmethod
    def set_output_impedance(self, impedance_ohms: int, HiZ: bool) -> None:
        """Sets the impedance (resistance in ohms) of the AWG when given an int value and boolean float for infinite resistance"""
        ...

    @abstractmethod
    def get_output_impedance(self) -> int:
        """Retrieves the output impedance (resistance in ohms) of the AWG as an int"""
        ...

    @abstractmethod
    def set_phase_degrees(self, phase_degrees: int) -> None:
        ...

    @abstractmethod
    def get_phase_degrees(self) -> int:
        ...

    @abstractmethod
    def set_cycles(self, cycles: int) -> None:
        """Sets the number of cycles the AWG is set to (cycles is the number of sine waves cycles inside each burst, assuming it's in burst mode)"""
        ...

    @abstractmethod
    def get_cycles(self) -> int:
        """Retrieves the number of cycles the AWG is set to (cycles is the number of sine waves cycles inside each burst, assuming it's in burst mode)"""
        ...

    @abstractmethod
    def set_trigger_output(self, trigger_out: bool) -> None:
        """Enables or disables the AWG trigger output signal"""
        ...

    @abstractmethod
    def get_trigger_output(self) -> Union[bool, None]:
        """Returns whether the trigger output is on, or None if the AWG is not connected"""
        ...

    def __str__(self):
        """Returns the last known state of the device. Use getstate to inquire the state before calling"""
        self.get_state()
        return "Waveform Generator\nSettings:\n" + str(self.state)

    def SetTriggerOutput(self, external: bool, period_s: float, delay_s: float):
        """
        Enables or disables the external trigger output of the AWG in burst mode, as well as the period of the burst
        and a delay between the beginning of the burst and the trigger signal if desired.
        """
        ...

    def GetTriggerOutput(self) -> bool:
        """Returns whether the AWG is outputting a trigger pulse in burst mode"""
        ...
