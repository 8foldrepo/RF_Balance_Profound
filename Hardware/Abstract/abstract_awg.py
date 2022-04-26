from abc import abstractmethod, ABC
from PyQt5.QtCore import pyqtSignal
from typing import Tuple

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractAWG(AbstractDevice):
    output_signal = pyqtSignal(bool)

    def __init__(self, config=None, device_key='Keysight_AWG', parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        self.state = dict()

    '''Call self.setup using config file settings'''

    @abstractmethod
    def set_to_defaults(self):
        ...

    """Sets all settings of the awg with one command and wait until it is done configuring"""

    @abstractmethod
    def setup(self, frequency_Hz: float, amplitude_V: float, burst: bool, ext_trig: bool, burst_period_s: float,
              burst_cycles: int, output: bool, output_Impedance: int, offset_V: float):
        self.SetOutput(output)
        self.SetFrequency_Hz(frequency_Hz)
        self.SetAmplitude_V(amplitude_V)
        self.SetCycles(burst_cycles)
        self.SetBurst(burst)
        self.SetTriggerInput(external=ext_trig, period_s=burst_period_s)
        self.SetOffset_V(offset_V)
        self.SetOutputImpedance(output_Impedance)

    """Inquires all key AWG settings, and returns a dictionary containing their names and values"""

    @abstractmethod
    def get_state(self):
        self.Get_Output()
        self.GetFrequency_Hz()
        self.GetAmplitude_V()
        self.GetBurst()
        self.GetTriggerInput()
        self.GetOffset_V()
        self.GetOutputImpedance()
        return self.state

    @abstractmethod
    def Reset(self):
        self.set_to_defaults()
        self.wait_til_complete()

    @abstractmethod
    def wait_til_complete(self):
        pass

    """Turns the output on or off"""

    @abstractmethod
    def SetOutput(self, on: bool):
        self.state["on"] = on

    @abstractmethod
    def Get_Output(self):
        return self.state["on"]

    """Sets the frequency of the signal"""

    @abstractmethod
    def SetFrequency_Hz(self, frequency):
        self.state["frequency_Hz"] = frequency

    @abstractmethod
    def GetFrequency_Hz(self) -> float:
        return self.state["frequency_Hz"]

    """Sets the peak to peak amplitude of the waveform in volts"""

    @abstractmethod
    def SetAmplitude_V(self, amplitude):
        self.state["amplitude_V"] = amplitude

    @abstractmethod
    def GetAmplitude_V(self) -> float:
        return self.state["amplitude_V"]

    """Sets the dc offset of the waveform in volts"""

    @abstractmethod
    def SetOffset_V(self, offset):
        self.state["offset_V"] = offset

    @abstractmethod
    def GetOffset_V(self) -> float:
        return self.state["offset_V"]

    """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""

    @abstractmethod
    def SetTriggerInput(self, external: bool, period_s=.000010, delay_s=0):
        pass

    """Returns info about the trigger: source, delay_s, period_s"""

    @abstractmethod
    def GetTriggerInput(self) -> Tuple[str, float, float]:
        ...

    @abstractmethod
    def SetBurst(self, on=True):
        self.state["burst_on"] = on

    """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""

    @abstractmethod
    def GetBurst(self) -> Tuple[bool, int]:
        return self.state["burst_on"], self.state["burst_cycles"]

    @abstractmethod
    def SetOutputImpedance(self, impedance_ohms=50, HiZ=False):
        if HiZ:
            self.state["output impedance"] = impedance_ohms
        else:
            self.state["output impedance"] = 10000000

    @abstractmethod
    def GetOutputImpedance(self) -> int:
        return self.state["output impedance"]

    @abstractmethod
    def SetPhaseDegrees(self, phase_degrees=0):
        self.state["phase degrees"] = phase_degrees

    @abstractmethod
    def GetPhaseDegrees(self) -> int:
        return self.state["phase degrees"]

    @abstractmethod
    def SetCycles(self, cycles):
        self.state["burst_cycles"] = cycles

    @abstractmethod
    def GetCycles(self) -> int:
        return self.state["burst_cycles"]

    '''Enables or disables the awg's trigger output signal'''

    @abstractmethod
    def SetTriggerOutput(self, trigger_out: bool):
        ...

    """Returns the last known state of the device. Use getstate to inquire the state before calling"""

    def __str__(self):
        self.get_state()
        return "Waveform Generator\nSettings:\n" + str(self.state)
