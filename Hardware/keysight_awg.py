import pyvisa
from Utilities.load_config import *
from PyQt5.QtCore import pyqtSignal

from Hardware.Abstract.abstract_awg import AbstractAWG

class KeysightAWG(AbstractAWG):
    output_signal = pyqtSignal(bool)

    def __init__(self, resource_manager = None, config = None, device_key = 'Keysight_AWG', parent = None):
        super().__init__(config = config, device_key= device_key, parent = parent)
        if resource_manager is not None:
            self.rm = resource_manager
        else:
            self.rm = pyvisa.ResourceManager()

        self.address = None
        self.inst = None
        self.state = dict()
        self.fields_setup()

    #Todo: add default settings to config file and switch to them here
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
                   output=self.config[self.device_key]['output'],
                   output_Impedance=self.config[self.device_key]['output_Impedance'])

    def connect_hardware(self):
        resources = self.rm.list_resources()
        self.inst = None
        for resource in resources:
            if self.config[self.device_key]["identifier"] in resource:
                self.address = resource
                try:
                    self.inst = self.rm.open_resource(resource)
                except pyvisa.errors.VisaIOError as e:
                    self.log("Keysight 33509B Series function generator not found", level='error')
                    self.connected_signal.emit(False)
                    return

                if self.config[self.device_key]['set_on_startup']:
                    self.set_to_defaults()
                else:
                    self.get_state()

                self.connected_signal.emit(True)
                return

        self.log("Keysight 33509B Series function generator not found", level='error')
        self.connected_signal.emit(False)

    def disconnect_hardware(self):
        try:
            self.inst.close()
        except:
            pass
        self.connected_signal.emit(False)

    """Sets all settings of the awg with one command and wait until it is done configuring"""
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
    def get_state(self):
        self.Get_Output()
        self.GetFrequency_Hz()
        self.GetAmplitude_V()
        self.GetBurst()
        self.GetTrigger()
        self.GetOffset_V()
        self.GetOutputImpedence()
        return self.state

    def Reset(self):
        self.inst.write(f"*RST")
        self.wait_til_complete()

    def wait_til_complete(self):
        self.inst.write("*IDN?")
        self.inst.read()

    """Turns the output on or off"""
    def SetOutput(self, on: bool):
        if on:
            self.inst.write('OUTP ON')
            self.output_signal.emit(True)
        else:
            self.inst.write('OUTP OFF')
            self.output_signal.emit(False)

    def Get_Output(self):
        self.inst.write('OUTP?')
        reply = self.inst.read()
        self.state["output"] = "1" in reply
        self.output_signal.emit(self.state["output"])
        return self.state["output"]

    """Sets the frequency of the signal"""
    def SetFrequency_Hz(self, frequency):
        self.inst.write(f"FREQ {frequency}")

    def GetFrequency_Hz(self):
        self.inst.write(f"FREQ?")
        self.state["frequency_Hz"] = float(self.inst.read())
        return self.state["frequency_Hz"]

    """Sets the peak to peak amplitude of the waveform in volts"""
    def SetAmplitude_V(self, amplitude):
        self.inst.write(f"VOLT {amplitude}")

    def GetAmplitude_V(self):
        self.inst.write(f"VOLT?")
        self.state["amplitude_V"] = float(self.inst.read())
        return self.state["amplitude_V"]

    """Sets the dc offset of the waveform in volts"""
    def SetOffset_V(self, offset):
        self.inst.write(f"VOLT:OFFS {offset}")

    def GetOffset_V(self):
        self.inst.write(f"VOLT:OFFS?")
        return float(self.inst.read())

    """Shows text_item on the AWG screen"""
    def DisplayText(self, text):
        self.inst.write(f"DISP:TEXT {text}")

    def SetFunction(self, func = "SIN"):
        self.inst.write(f"FUNC {func}:")

    def GetFunction(self):
        self.inst.write(f"FUNC?")
        return self.inst.read()

    """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""
    def SetTrigger(self, external:bool, period_s = .000010, delay_s = 0):
        self.inst.write(f"TRIG1:DEL {delay_s}")
        if external:
            self.inst.write(f"TRIG1:SOUR EXT")
        else:
            self.inst.write(f"TRIG1:SOUR TIM")
            self.inst.write(f"TRIG1:TIM {period_s}")

    """Returns info about the trigger: source, delay_s, period_s"""
    def GetTrigger(self):
        self.inst.write(f"TRIG:SOUR?")
        self.state['trig_source'] = self.inst.read().strip('\n')
        self.inst.write(f"TRIG:DEL?")
        self.state['trig_delay_s'] = float(self.inst.read())
        self.inst.write(f"TRIG:TIM?")
        self.state['trig_period_s'] = float(self.inst.read())
        return self.state['trig_source'],self.state['trig_delay_s'],self.state['trig_period_s']

    def SetBurst(self, on = True):
        if "Phase_degrees" in self.state.keys():
            self.inst.write(f"BURS:PHAS {self.state['Phase_degrees']}")
        if on:
            self.inst.write("BURS ON")
        else:
            self.inst.write("BURS OFF")

    """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""
    def GetBurst(self):
        self.inst.write(f"BURS?")
        self.state['burst_on'] = "1" in self.inst.read()
        self.inst.write(f"BURS:NCYC?")
        self.state['burst_ncyc'] = int(float(self.inst.read()))
        return self.state['burst_on'], self.state['burst_ncyc']

    def SetOutputImpedence(self, impedence_ohms = 50, HiZ = False):
        if HiZ:
            self.inst.write("OUTP:LOAD INF")
        else:
            self.inst.write(f"OUTP:LOAD {impedence_ohms}")

    def GetOutputImpedence(self):
        self.inst.write(f"OUTP:LOAD?")
        return float(self.inst.read())

    def SetPhaseDegrees(self, phase_degrees=0):
        self.phase_degrees = phase_degrees
        self.inst.write(f"UNIT:ANGL DEG")
        self.inst.write(f"SOUR:PHASE{self.phase_degrees}")

    def GetPhaseDegrees(self):
        self.inst.write(f"UNIT:ANGL DEG")
        self.inst.write(f"SOUR:PHASE?")
        self.state["phase degrees"] = self.inst.read()
        return self.state["phase degrees"]

    def SetCycles(self, cycles):
        self.inst.write(f"BURS:NCYC {cycles}")

    def GetCycles(self):
        self.inst.write(f"BURS:NCYC?")
        self.state["burst_cycles"] = self.inst.read()
        return self.state["burst_cycles"]

    """Returns the last known state of the device. Use getstate to inquire the state before calling"""
    def __str__(self):
        self.get_state()
        return "Keysight 33500B Series Waveform Generator\nSettings:\n"+str(self.state)

if __name__ == "__main__":
    awg = KeysightAWG()
    awg.connect_hardware()
    awg.Reset()
    print(awg)
    awg.setup(frequency_Hz=4290000,amplitude_V=.2, burst=False,burst_cycles=50,ext_trig=False,
              burst_period_s=.10,offset_V=0,output=True,output_Impedance=50)
    print(awg)