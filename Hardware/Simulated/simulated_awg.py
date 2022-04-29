from Hardware.Abstract.abstract_awg import AbstractAWG
from Utilities.load_config import *
from PyQt5.QtCore import pyqtSignal


class SimulatedAWG(AbstractAWG):
    output_signal = pyqtSignal(bool)

    def __init__(self, config=None, device_key='Keysight_AWG', parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        self.state = dict()
        self.fields_setup()

    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

    def set_to_defaults(self):
        self.setup(frequency_Hz=self.config[self.device_key]['frequency_Hz'],
                   amplitude_V=self.config[self.device_key]['amplitude_V'],
                   burst=self.config[self.device_key]['burst'],
                   burst_cycles=self.config[self.device_key]['burst_cycles'],
                   ext_trig=self.config[self.device_key]['ext_trig'],
                   burst_period_s=self.config[self.device_key]['burst_period_s'],
                   offset_V=self.config[self.device_key]['offset_V'],
                   output=False,
                   output_Impedance=self.config[self.device_key]['output_Impedance'])

    def connect_hardware(self):
        self.setup(frequency_Hz=4290000, amplitude_V=.1)
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ''

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(False)

    """Sets all settings of the awg with one command and wait until it is done configuring"""

    def setup(self, frequency_Hz, amplitude_V, burst=False, ext_trig=False, burst_period_s=.00001, burst_cycles=50,
              offset_V=0, output=False, output_Impedance=50):
        self.SetOutput(output)
        self.SetFrequency_Hz(frequency_Hz)
        self.SetAmplitude_V(amplitude_V)
        self.SetCycles(burst_cycles)
        self.SetBurst(burst)
        self.SetTriggerInput(external=ext_trig, period_s=burst_period_s)
        self.SetOffset_V(offset_V)
        self.SetOutputImpedance(output_Impedance)

        self.wait_til_complete()

    """Inquires all key AWG settings, and returns a dictionary containing their names and values"""

    def get_state(self):
        self.Get_Output()
        self.GetFrequency_Hz()
        self.GetAmplitude_V()
        self.GetBurst()
        self.GetTriggerInput()
        self.GetOffset_V()
        self.GetOutputImpedance()
        return self.state

    def Reset(self):
        self.set_to_defaults()
        self.wait_til_complete()

    def wait_til_complete(self):
        pass

    """Turns the output on or off"""

    def SetOutput(self, on: bool):
        self.state["on"] = on
        self.output_signal.emit(on)

    def Get_Output(self):
        self.output_signal.emit(self.state["on"])
        return self.state["on"]

    """Sets the frequency of the signal"""

    def SetFrequency_Hz(self, frequency_Hz):
        self.state["frequency_Hz"] = frequency_Hz
        self.frequency_signal.emit(frequency_Hz/1000000)

    def GetFrequency_Hz(self):
        return self.state["frequency_Hz"]

    """Sets the peak to peak amplitude of the waveform in volts"""

    def SetAmplitude_V(self, amplitude):
        self.state["amplitude_V"] = amplitude

    def GetAmplitude_V(self):
        return self.state["amplitude_V"]

    """Sets the dc offset of the waveform in volts"""

    def SetOffset_V(self, offset):
        pass

    def GetOffset_V(self):
        pass

    def SetFunction(self, func="SIN"):
        pass

    def GetFunction(self):
        pass

    """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""

    def SetTriggerInput(self, external: bool, period_s=.000010, delay_s=0):
        pass

    """Returns info about the trigger: source, delay_s, period_s"""

    def GetTriggerInput(self):
        pass

    def SetBurst(self, on=True):
        self.state["burst_on"] = on

    """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""

    def GetBurst(self):
        return self.state["burst_on"], self.state["burst_cycles"]

    def SetOutputImpedance(self, impedance_ohms=50, HiZ=False):
        if HiZ:
            self.state["output impedance"] = impedance_ohms
        else:
            self.state["output impedance"] = 10000000

    def GetOutputImpedance(self):
        return self.state["output impedance"]

    def SetPhaseDegrees(self, phase_degrees=0):
        self.state["phase degrees"] = phase_degrees

    def GetPhaseDegrees(self):
        return self.state["phase degrees"]

    def SetCycles(self, cycles):
        self.state["burst_cycles"] = cycles

    def GetCycles(self):
        return self.state["burst_cycles"]

    """Returns the last known state of the device. Use getstate to inquire the state before calling"""

    def SetTriggerOutput(self, trigger_out: bool):
        pass

    def get_serial_number(self) -> str:
        return '\"Simulated\"'

    def __str__(self):
        self.get_state()
        return "Waveform Generator\nSettings:\n" + str(self.state)


if __name__ == "__main__":
    awg = SimulatedAWG()
    awg.connect_hardware()
    awg.Reset()
    print(awg)
    awg.setup(frequency_Hz=4290000, amplitude_V=.2, burst=False, burst_cycles=50, ext_trig=False,
              burst_period_s=.10, offset_V=0, output=True, output_Impedance=50)
    print(awg)
