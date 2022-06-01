from typing import Tuple, Union

import pyvisa
from PyQt5 import QtCore

from Hardware.Simulated.simulated_awg import AbstractAWG
from Utilities.load_config import *
from Utilities.useful_methods import error_acceptable
import time as t


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
        self.command("*RST")
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
        self.connected = False
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
        """Returns true or false depending on the whether the waveform generator is on or off"""
        self.command("OUTP?")
        reply = self.read()
        self.state["output"] = "1" in reply
        self.output_signal.emit(self.state["output"])

        return self.state["output"]

    def set_frequency_hz(self, frequency):
        """Sets the frequency of the signal"""
        self.state["frequency_Hz"] = frequency
        self.command(f"FREQ {frequency}")

        actual_frequency = self.get_frequency_hz()
        if not error_acceptable(actual_frequency, frequency, 2, print_msg=False):
            self.log(level="error", message=f"Frequency {frequency}Hz out of range "
                                            f"with current settings. Frequency is {actual_frequency}")
            return False
        return True

    def get_frequency_hz(self):
        self.command(f"FREQ?")
        self.state["frequency_Hz"] = float(self.read())
        self.frequency_signal.emit(self.state["frequency_Hz"] / 1000000)
        return self.state["frequency_Hz"]

    def set_amplitude_v(self, amplitude):
        """Sets the peak to peak amplitude of the waveform in volts"""
        self.command(f"VOLT {amplitude}")
        actual_amplitude_v = self.get_amplitude_v()
        if error_acceptable(actual_amplitude_v, amplitude, 6, print_msg=False):
            self.log(level="error",
                     message=f"Amplitude {amplitude} V is out of range with current settings. Amplitude is {actual_amplitude_v} V")
            return False
        return True

    def get_amplitude_v(self):
        self.command(f"VOLT?")
        self.state["amplitude_V"] = float(self.read())
        return self.state["amplitude_V"]

    def set_offset_v(self, offset):
        """Sets the dc offset of the waveform in volts"""
        self.state["offset_V"] = offset
        self.command(f"VOLT:OFFS {offset}")

    def get_offset_v(self):
        """Shows text_item on the AWG screen"""
        self.command(f"VOLT:OFFS?")
        self.state["offset_V"] = float(self.read())
        return self.state["offset_V"]

    def set_function(self, func="SIN"):
        """Sets the shape of the source waveform"""
        command_str = f"SOUR:FUNC {func}"
        print(command_str)
        self.command(command_str)
        t.sleep(.05)

    def get_function(self):
        self.command(f"SOUR:FUNC?")
        return self.read().replace("\n", "")

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

    def get_burst(self) -> Tuple[bool, int]:
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

    def get_output_impedance(self) -> Union[float, None]:
        self.command(f"OUTP:LOAD?")
        return float(self.read())

    def set_phase_degrees(self, phase_degrees: float = 0) -> bool:
        self.command(f"UNIT:ANGL DEG")
        self.command(f"BURS:PHASE {phase_degrees}")
        t.sleep(.05)
        return error_acceptable(self.get_phase_degrees(), phase_degrees, 2, print_msg=False)

    def get_phase_degrees(self) -> float:
        self.command(f"UNIT:ANGL DEG")
        self.command(f"BURS:PHASE?")
        self.state["phase degrees"] = float(self.read())
        return self.state["phase degrees"]

    def set_cycles(self, cycles: int):
        self.state["burst_cycles"] = cycles
        self.command(f"BURS:NCYC {cycles}")
        return self.get_cycles == cycles

    def get_cycles(self) -> int:
        self.command(f"BURS:NCYC?")
        self.state["burst_cycles"] = self.read()
        return int(float(self.state["burst_cycles"]))

    def command(self, command: str):
        try:
            self.inst.write(command)
            t.sleep(.03)
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'write'":
                self.log(f"{self.device_key} Not connected")
            else:
                self.log(level="error", message=f"error in command: {e}")

    def read(self) -> str:
        try:
            return self.inst.read()
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'read'":
                self.log(f"Could not read reply, {self.device_key} Not connected")
            else:
                self.log(level="error", message=f"error in read: {e}")

    def check_connected(self) -> bool:
        connected = False
        try:
            Output = self.get_output()
            if Output is not None:
                connected = True
        except AssertionError:
            pass
        except pyvisa.errors.InvalidSession:
            pass
        self.connected = connected
        return connected

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
        t.sleep(.05)

    def get_serial_number(self) -> Union[str, None]:
        self.command("*IDN?")
        str = self.read()

        return str.split(",")[2]

    def __str__(self):
        """Returns the last known state of the device. Use getstate to inquire the state before calling"""

        self.get_state()
        return "Keysight 33500B Series Waveform Generator\nSettings:\n" + str(self.state)


def unit_test():
    """
    Tests all key features of the waveform generator in a random order with random parameters 10 times.
    Run in debug mode with a breakpoint on any exception to search for bugs.
    If the test passes the test will print "test passed :)"
    """
    import random

    awg = KeysightAWG()
    awg.connect_hardware()

    # test a random sequence of operations 10 times
    for i in range(10):
        step_sequence = list(range(10))
        random.shuffle(step_sequence)

        for step_number in step_sequence:
            if step_number == 0:  # TEST: output
                on = bool(random.getrandbits(1))
                awg.set_output(on=on)
                if on:
                    assert awg.get_output() is True
                else:
                    assert awg.get_output() is False
            if step_number == 1:  # TEST: frequency (Hz)
                frequency = round(random.uniform(.0001, 19999999), 2)
                successful = awg.set_frequency_hz(frequency=frequency)
                freq = awg.get_frequency_hz()
                assert error_acceptable(freq, frequency, 2) or not successful
            if step_number == 2:  # TEST: offset (V)
                offset = random.uniform(-5, 5)
                awg.set_offset_v(offset=offset)
                assert error_acceptable(offset, awg.get_offset_v())
            if step_number == 3:  # TEST: function
                possible_funcs = ['SIN', 'SQU', 'RAMP', 'TRI', 'NOIS', 'PRBS']
                func = random.choice(possible_funcs)
                awg.set_function(func=func)
                func2 = awg.get_function()
                assert func2 == func
            if step_number == 4:  # TEST: check connected
                awg.disconnect_hardware()
                assert not awg.check_connected()
                awg.connect_hardware()
                assert awg.check_connected()
            if step_number == 5:  # TEST: wrap up
                awg.wrap_up()
                assert not awg.check_connected()
                awg.connect_hardware()
                assert awg.check_connected()
            if step_number == 6:  # TEST: amplitude (V)
                amplitude = round(random.uniform(1, 9.9999), 2)
                awg.set_amplitude_v(amplitude=amplitude)
                assert amplitude == awg.get_amplitude_v()
            if step_number == 7:  # TEST: burst
                on = bool(random.getrandbits(1))
                awg.set_burst(on=on)
                response = awg.get_burst()[0]
                if on:
                    assert response
                else:
                    assert not response
            if step_number == 8:  # TEST: number of cycles
                cycles = random.randint(1, 99)
                awg.set_cycles(cycles=cycles)
                cycles2 = awg.get_cycles()
                assert cycles2 == cycles
            if step_number == 9:  # TEST: phase degrees
                phase_degrees = random.randint(0, 180)
                awg.set_phase_degrees(phase_degrees=phase_degrees)
                phase = awg.get_phase_degrees()
                assert error_acceptable(phase, phase_degrees, 2)
            # if step_number == 10:  # TEST: output impedance
            #     ...
    print("Test passed :)")


if __name__ == "__main__":
    unit_test()
