import pyvisa
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from Hardware.Simulated.simulated_awg import AbstractAWG
from Utilities.load_config import *


class KeysightAWG(AbstractAWG):
    output_signal = QtCore.pyqtSignal(bool)

    def __init__(self, resource_manager=None, config=None, device_key='Keysight_AWG', parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        if resource_manager is not None:
            self.rm = resource_manager
        else:
            self.rm = pyvisa.ResourceManager()

        self.address = None
        self.inst = None
        self.state = dict()
        self.fields_setup()

    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()

    def set_to_defaults(self):
        self.setup(
            frequency_Hz=self.config[self.device_key]["frequency_Hz"],
            amplitude_V=self.config[self.device_key]["amplitude_V"],
            burst=self.config[self.device_key]["burst_on"],
            burst_cycles=self.config[self.device_key]["burst_cycles"],
            ext_trig=self.config[self.device_key]["trig_in"],
            burst_period_s=self.config[self.device_key]["burst_period_s"],
            offset_V=self.config[self.device_key]["offset_V"],
            output=False,
            output_Impedance=self.config[self.device_key]["output_Impedance"],
            trigger_out=self.config[self.device_key]["trig_out"],
        )

    def connect_hardware(self):
        resources = self.rm.list_resources()
        feedback = ""
        self.inst = None
        for resource in resources:
            if self.config[self.device_key]["identifier"] in resource:
                self.address = resource
                try:
                    self.inst = self.rm.open_resource(resource)
                except pyvisa.errors.VisaIOError as e:
                    feedback = f"Keysight 33509B Series function generator not found: {e}",
                    self.log(level='error', message=feedback)
                    break

                if self.config[self.device_key]["set_on_startup"]:
                    self.set_to_defaults()
                else:
                    self.get_state()

                self.connected = True
                self.connected_signal.emit(self.connected)
                return self.connected, feedback

        self.log("Keysight 33509B Series function generator not found", level="error")
        self.connected = False
        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def disconnect_hardware(self):
        self.inst.close()

        self.connected_signal.emit(False)



    def setup(self, frequency_Hz, amplitude_V, burst=False, ext_trig=False, burst_period_s=.00001, burst_cycles=50,
              offset_V=0, output=False, output_Impedance=50, trigger_out=True):
        """Sets all settings of the awg with one command and wait until it is done configuring"""
        self.set_output(output)
        self.set_frequency_hz(frequency_Hz)
        self.set_amplitude_v(amplitude_V)
        self.set_cycles(burst_cycles)
        self.set_burst(burst)
        self.SetTriggerInput(external=ext_trig, period_s=burst_period_s, delay_s=0)
        self.set_trigger_output(trigger_out=trigger_out)
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
        self.command(f"*RST")
        self.wait_til_complete()

    def wait_til_complete(self):
        self.command("*IDN?")
        self.read()

    def set_output(self, on: bool):
        """Turns the output on or off"""
        if on:
            self.command("OUTP ON")
            self.output_signal.emit(True)
        else:
            self.command("OUTP OFF")
            self.output_signal.emit(False)

    def get_output(self):
        self.command("OUTP?")
        reply = self.read()
        self.state["output"] = "1" in reply
        self.output_signal.emit(self.state["output"])
        return self.state["output"]

    def set_frequency_hz(self, frequency):
        """Sets the frequency of the signal"""
        self.state["frequency_Hz"] = frequency
        self.command(f"FREQ {frequency}")

        if self.get_frequency_hz() != frequency:
            self.log(level="error", message="frequency not set")
            return False
        return True

    def get_frequency_hz(self):
        self.command(f"FREQ?")
        self.state["frequency_Hz"] = float(self.read())
        self.frequency_signal.emit(self.state["frequency_Hz"] / 1000000)
        return self.state["frequency_Hz"]

    """Sets the peak to peak amplitude of the waveform in volts"""

    def set_amplitude_v(self, amplitude):
        self.command(f"VOLT {amplitude}")
        if not self.get_amplitude_v() == amplitude:
            self.log(level="error", message="frequency not set")
            return False
        return True

    def get_amplitude_v(self):
        self.command(f"VOLT?")
        self.state["amplitude_V"] = float(self.read())
        return self.state["amplitude_V"]

    """Sets the dc offset of the waveform in volts"""

    def set_offset_v(self, offset):
        self.state["offset_V"] = offset
        self.command(f"VOLT:OFFS {offset}")

    def get_offset_v(self):
        self.command(f"VOLT:OFFS?")
        self.state["offset_V"] = float(self.read())
        return self.state["offset_V"]

    """Shows text_item on the AWG screen"""

    def DisplayText(self, text):
        self.command(f"DISP:TEXT {text}")

    def SetFunction(self, func="SIN"):
        self.command(f"FUNC {func}:")

    def GetFunction(self):
        self.command(f"FUNC?")
        return self.read()

    def set_trigger_output(self, trigger_out=True):
        if trigger_out:
            self.command("OUTP:TRIG ON")
            self.command("OUTP:TRIG:SLOP POS")
        else:
            self.command("OUTP:TRIG OFF")

    def set_burst(self, on=True):
        self.state["burst_on"] = on
        if "Phase_degrees" in self.state.keys():
            self.command(f"BURS:PHAS {self.state['Phase_degrees']}")
        if on:
            self.command("BURS ON")
        else:
            self.command("BURS OFF")

    def get_burst(self):
        """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""
        self.command(f"BURS?")
        self.state["burst_on"] = "1" in self.read()
        self.command(f"BURS:NCYC?")
        self.state["burst_cycles"] = int(float(self.read()))
        return self.state["burst_on"], self.state["burst_cycles"]

    def set_output_impedance(self, impedance_ohms=50, HiZ=False):
        if HiZ:
            self.command("OUTP:LOAD INF")
        else:
            self.command(f"OUTP:LOAD {impedance_ohms}")

    def get_output_impedance(self):
        self.command(f"OUTP:LOAD?")
        return float(self.read())

    def set_phase_degrees(self, phase_degrees=0):
        self.command(f"UNIT:ANGL DEG")
        self.command(f"SOUR:PHASE{phase_degrees}")
        return self.get_phase_degrees() == phase_degrees

    def get_phase_degrees(self):
        self.command(f"UNIT:ANGL DEG")
        self.command(f"SOUR:PHASE?")
        self.state["phase degrees"] = self.read()
        return self.state["phase degrees"]

    def set_cycles(self, cycles):
        self.state["burst_cycles"] = cycles
        self.command(f"BURS:NCYC {cycles}")
        return self.get_cycles == cycles

    def get_cycles(self):
        self.command(f"BURS:NCYC?")
        self.state["burst_cycles"] = self.read()
        return self.state["burst_cycles"]

    def command(self, command):
        try:
            self.inst.write(command)
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'write'":
                self.log(f"{self.device_key} Not connected")
            else:
                self.log(level="error", message=f"error in command: {e}")

    def read(self):
        try:
            return self.inst.read()
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'read'":
                self.log(f"Could not read reply, {self.device_key} Not connected")
            else:
                self.log(level="error", message=f"error in read: {e}")

    def check_connected(self):
        return self.inst is not None

    # Trigger input methods, unused, untested
    # """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""
    #
    # def SetTriggerInput(self, external: bool, period_s=.000010, delay_s=0):
    #     self.command(f"TRIG1:DEL {delay_s}")
    #     if external:
    #         self.command(f"TRIG1:SOUR EXT")
    #     else:
    #         self.command(f"TRIG1:SOUR TIM")
    #         self.command(f"TRIG1:TIM {period_s}")

    # """Returns info about the trigger: source, delay_s, period_s"""
    #
    # def GetTriggerInput(self):
    #     self.command(f"TRIG:SOUR?")
    #     self.state['trig_source'] = self.read().strip('\n')
    #     self.command(f"TRIG:DEL?")
    #     self.state['trig_delay_s'] = float(self.read())
    #     self.command(f"TRIG:TIM?")
    #     self.state['trig_period_s'] = float(self.read())
    #     return self.state['trig_source'], self.state['trig_delay_s'], self.state['trig_period_s']

    def wrap_up(self):
        self.set_output(False)
        self.disconnect_hardware()

    def get_serial_number(self) -> str:
        if not self.connected:
            return None

        self.command("*IDN?")
        str = self.read()

        return str.split(",")[2]

    def __str__(self):
        """Returns the last known state of the device. Use getstate to inquire the state before calling"""

        self.get_state()
        return "Keysight 33500B Series Waveform Generator\nSettings:\n" + str(self.state)


if __name__ == "__main__":
    import random

    awg = KeysightAWG()
    awg.connect_hardware()

    # test a random sequence of operations 10 times
    for i in range(10):
        step_sequence = list(range(5))
        random.shuffle(step_sequence)

        for step_number in step_sequence:
            if step_number == 0:  # TEST: output
                on = bool(random.getrandbits(1))
                awg.set_output(on=on)
                if on:
                    assert awg.get_output() is not None
                else:
                    assert awg.get_output() is None
            if step_number == 1:  # TEST: frequency
                frequency = random.uniform(1, 9999999)
                awg.set_frequency_hz(frequency=frequency)
                assert awg.get_frequency_hz() == frequency
            if step_number == 2:  # TEST: offset (V)
                offset = random.uniform(1, 10)
                awg.set_offset_v(offset=offset)
                assert offset == awg.get_offset_v()
            if step_number == 3:
                ...
            if step_number == 4:
                ...
            if step_number == 5:
                ...

    print("Test passed :)")