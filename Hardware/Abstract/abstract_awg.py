from abc import abstractmethod
from PyQt5.QtCore import pyqtSignal
from typing import Tuple

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractAWG(AbstractDevice):
    output_signal = pyqtSignal(bool)
    state: dict

    def __init__(self, config=None, device_key='Keysight_AWG', parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

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
        self.SetTriggerInput(external=ext_trig, period_s=burst_period_s, delay_s=0)
        self.SetOffset_V(offset_V)
        self.SetOutputImpedance(output_Impedance, HiZ=False)

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
        ...

    @abstractmethod
    def wait_til_complete(self):
        ...

    """Turns the output on or off"""

    @abstractmethod
    def SetOutput(self, on: bool):
        ...

    @abstractmethod
    def Get_Output(self):
        ...

    """Sets the frequency of the signal"""

    @abstractmethod
    def SetFrequency_Hz(self, frequency: float):
        ...

    @abstractmethod
    def GetFrequency_Hz(self) -> float:
        ...

    """Sets the peak to peak amplitude of the waveform in volts"""

    @abstractmethod
    def SetAmplitude_V(self, amplitude: float):
        ...

    @abstractmethod
    def GetAmplitude_V(self) -> float:
        ...

    """Sets the dc offset of the waveform in volts"""

    @abstractmethod
    def SetOffset_V(self, offset: float):
        ...

    @abstractmethod
    def GetOffset_V(self) -> float:
        ...

    """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""

    @abstractmethod
    def SetTriggerInput(self, external: bool, period_s: float, delay_s: float):
        ...

    """Returns info about the trigger: source, delay_s, period_s"""

    @abstractmethod
    def GetTriggerInput(self) -> Tuple[str, float, float]:
        ...

    @abstractmethod
    def SetBurst(self, on: bool):
        self.state["burst_on"] = on

    """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""

    @abstractmethod
    def GetBurst(self) -> Tuple[bool, int]:
        return self.state["burst_on"], self.state["burst_cycles"]

    @abstractmethod
    def SetOutputImpedance(self, impedance_ohms: int, HiZ: bool):
        ...

    @abstractmethod
    def GetOutputImpedance(self) -> int:
        ...

    @abstractmethod
    def SetPhaseDegrees(self, phase_degrees: int):
        ...

    @abstractmethod
    def GetPhaseDegrees(self) -> int:
        ...

    @abstractmethod
    def SetCycles(self, cycles: int):
        ...

    @abstractmethod
    def GetCycles(self) -> int:
        ...

    '''Enables or disables the AWG trigger output signal'''

    @abstractmethod
    def SetTriggerOutput(self, trigger_out: bool):
        ...

    """Returns the last known state of the device. Use getstate to inquire the state before calling"""

    def __str__(self):
        self.get_state()
        return "Waveform Generator\nSettings:\n" + str(self.state)
