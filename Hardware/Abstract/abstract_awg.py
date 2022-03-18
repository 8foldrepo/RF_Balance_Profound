import pyvisa
from Utilities.load_config import *
from PyQt5.QtCore import pyqtSignal
from abc import  abstractmethod
from Hardware.Abstract.abstract_device import AbstractDevice

class AbstractAWG(AbstractDevice):
    output_signal = pyqtSignal(bool)

    def __init__(self, config = None, device_key = 'Keysight_AWG', parent = None):
        super().__init__(config = config, device_key= device_key, parent = parent)
        self.state = dict()
        self.fields_setup()

    #Todo: add default settings to config file and switch to them here
    @abstractmethod
    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

    @abstractmethod
    def set_to_defaults(self):
        self.setup(frequency_Hz=self.config[self.device_key]['frequency_Hz'],
                   amplitude_V=self.config[self.device_key]['amplitude_V'],
                   burst=self.config[self.device_key]['burst'],
                   burst_cycles=self.config[self.device_key]['burst_cycles'],
                   ext_trig=self.config[self.device_key]['ext_trig'],
                   burst_period_s=self.config[self.device_key]['burst_period_s'],
                   offset_V=self.config[self.device_key]['offset_V'],
                   output=self.config[self.device_key]['output'],
                   output_Impedance=self.config[self.device_key]['output_Impedance'])

    @abstractmethod
    def connect_hardware(self):
        self.connected_signal.emit(True)

    @abstractmethod
    def disconnect_hardware(self):
        self.connected_signal.emit(False)

    """Sets all settings of the awg with one command and wait until it is done configuring"""
    @abstractmethod
    def setup(self, frequency_Hz, amplitude_V, burst = False, ext_trig = False, burst_period_s=.00001,burst_cycles = 50,
              offset_V = 0, output=False, output_Impedance = 50):
        self.SetOutput(output)
        self.SetFrequency_Hz(frequency_Hz)
        self.SetAmplitude_V(amplitude_V)
        self.SetCycles(burst_cycles)
        self.SetBurst(burst)
        self.SetTrigger(external=ext_trig,period_s=burst_period_s)
        self.SetOffset_V(offset_V)
        self.SetOutputImpedence(output_Impedance)

        self.wait_til_complete()


    """Inquires all key AWG settings, and returns a dictionary containing their names and values"""
    @abstractmethod
    def get_state(self):
        self.Get_Output()
        self.GetFrequency_Hz()
        self.GetAmplitude_V()
        self.GetBurst()
        self.GetTrigger()
        self.GetOffset_V()
        self.GetOutputImpedence()
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
        pass

    @abstractmethod
    def GetFrequency_Hz(self):
        pass


    """Sets the peak to peak amplitude of the waveform in volts"""
    @abstractmethod
    def SetAmplitude_V(self, amplitude):
        pass

    @abstractmethod
    def GetAmplitude_V(self):
        pass

    """Sets the dc offset of the waveform in volts"""
    @abstractmethod
    def SetOffset_V(self, offset):
        pass

    @abstractmethod
    def GetOffset_V(self):
        pass

    @abstractmethod
    def SetFunction(self, func = "SIN"):
        pass

    @abstractmethod
    def GetFunction(self):
        pass

    """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""
    @abstractmethod
    def SetTrigger(self, external:bool, period_s = .000010, delay_s = 0):
        pass

    """Returns info about the trigger: source, delay_s, period_s"""
    @abstractmethod
    def GetTrigger(self):
        pass

    @abstractmethod
    def SetBurst(self, on = True):
        self.state["burst"] = on


    """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""
    @abstractmethod
    def GetBurst(self):
        return  self.state["burst"]

    @abstractmethod
    def SetOutputImpedence(self, impedence_ohms = 50, HiZ = False):
        self.state["output impedence"] = impedence_ohms

    @abstractmethod
    def GetOutputImpedence(self):
        return self.state["output impedence"]

    @abstractmethod
    def SetPhaseDegrees(self, phase_degrees=0):
        self.state["phase degrees"] = phase_degrees

    @abstractmethod
    def GetPhaseDegrees(self):
        return self.state["phase degrees"]

    @abstractmethod
    def SetCycles(self, cycles):
        self.state["burst_cycles"] = cycles

    @abstractmethod
    def GetCycles(self):
        return self.state["burst_cycles"]

    """Returns the last known state of the device. Use getstate to inquire the state before calling"""
    def __str__(self):
        self.get_state()
        return "Waveform Generator\nSettings:\n"+str(self.state)

if __name__ == "__main__":
    awg = AbstractAWG()
    awg.connect_hardware()
    awg.Reset()
    print(awg)
    awg.setup(frequency_Hz=4290000,amplitude_V=.2, burst=False,burst_cycles=50,ext_trig=False,
              burst_period_s=.10,offset_V=0,output=True,output_Impedance=50)
    print(awg)