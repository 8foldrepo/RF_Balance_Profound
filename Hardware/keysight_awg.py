import time as t
from typing import Tuple, Union

import pyvisa
from PyQt5 import QtCore

from Hardware.Simulated.simulated_awg import AbstractAWG
from Utilities.load_config import load_configuration
from Utilities.useful_methods import error_acceptable


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
            frequency_hz=self.config[self.device_key]["frequency_Hz"],
            amplitude_v=self.config[self.device_key]["amplitude_V"],
            burst=self.config[self.device_key]["burst_on"],
            burst_cycles=self.config[self.device_key]["burst_cycles"],
            ext_trig=self.config[self.device_key]["trig_in"],
            burst_period_s=self.config[self.device_key]["burst_period_s"],
            offset_v=self.config[self.device_key]["offset_V"],
            output=False,
            output_impedance=self.config[self.device_key]["output_Impedance"],
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
                    self.log('error', str(feedback))
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

    def setup(self, frequency_hz, amplitude_v, burst=False, ext_trig=False, burst_period_s=.00001, burst_cycles=50,
              offset_v=0, output=False, output_impedance=50, trigger_out=True):
        """Sets all settings of the awg with one command and wait until it is done configuring"""
        self.reset()
        self.set_output(output)
        self.set_frequency_hz(frequency_hz)
        self.set_amplitude_v(amplitude_v)
        self.set_cycles(burst_cycles)
        self.set_burst(burst)
        self.set_trigger_output(trigger_out=trigger_out)
        self.set_offset_v(offset_v)
        self.set_output_impedance(output_impedance)
        self.wait_til_complete()

    def get_state(self):
        """Inquires all key AWG settings, and returns a dictionary containing their names and values"""
        self.get_output()
        self.get_frequency_hz()
        self.get_amplitude_v()
        self.get_burst()
        self.get_trigger_output()
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
        if not error_acceptable(actual_amplitude_v, amplitude, 2, print_msg=False):
            self.log(level="error",
                     message=f"Amplitude {amplitude} V is out of range with current settings. Amplitude is "
                             f"{actual_amplitude_v} V")
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

    def get_trigger_output(self) -> Union[bool, None]:
        """Returns whether the trigger output is on, or None if the AWG is not connected"""
        if not self.connected:
            return None

        self.command("OUTP:TRIG?")
        on_str = self.read()
        self.state["trig_out"] = '1' in on_str
        return self.state["trig_out"]

    def set_burst(self, on=True):
        self.state["burst_on"] = on
        if "Phase_degrees" in self.state.keys():
            self.command(f"BURS:PHAS {self.state['Phase_degrees']}")
        if on:
            self.command("BURS ON")
        else:
            self.command("BURS OFF")
        t.sleep(.1)

    def get_burst(self) -> Tuple[bool, int]:
        """Returns: bool: indicating if the AWG is in burst mode, integer containing the number of cycles per burst"""
        self.command(f"BURS?")
        self.state["burst_on"] = "1" in self.read()
        self.command(f"BURS:NCYC?")
        self.state["burst_cycles"] = int(float(self.read()))
        return self.state["burst_on"], self.state["burst_cycles"]

    def set_output_impedance(self, impedance_ohms: int = 50, high_impedance: bool = False) -> None:
        if high_impedance:
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

    def set_cycles(self, cycles: int) -> bool:
        self.state["burst_cycles"] = cycles
        self.command(f"BURS:NCYC {cycles}")
        return self.get_cycles == cycles

    def get_cycles(self) -> int:
        """
        Getter method to get number of cycles stored in the
        hardware, returns the result as an int and stores it
        """
        self.command(f"BURS:NCYC?")
        self.state["burst_cycles"] = self.read()
        return int(float(self.state["burst_cycles"]))

    def command(self, command: str) -> None:
        """
        Uses pyvisa's write command to send a string to the device, handles errors/exceptions
        """
        try:
            self.inst.write(command)
            t.sleep(.03)
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'write'":
                self.log(f"{self.device_key} Not connected")
            else:
                self.log(level="error", message=f"error in command: {e}")

    def read(self) -> str:
        """
        calls pyvisa's read method for the AWG, return type is string, handles errors/exceptions
        """
        try:
            return self.inst.read()
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'read'":
                self.log(f"Could not read reply, {self.device_key} Not connected")
            else:
                self.log(level="error", message=f"error in read: {e}")

    def check_connected(self) -> bool:
        """
        Checks and returns whether the function generator is
        connected via looking at its output, handlers exceptions/errors
        """
        connected = False
        try:
            output = self.get_output()
            if output is not None:
                connected = True
        except AssertionError:
            pass
        except pyvisa.errors.InvalidSession:
            pass
        self.connected = connected
        return connected

    def get_serial_number(self) -> Union[str, None]:
        """
        Returns the serial number via issuing the standard Keysight '*IDN?' command,
        return nothing if not connected.
        """
        if not self.connected:
            self.log(message="get_serial_number method in keysight_awg class called while function generator"
                             "is disconnected.")
            return None

        self.command("*IDN?")
        read_str = self.read()
        return read_str.split(",")[2]

    def wrap_up(self) -> None:
        """
        Turns off the function generator via setting its output variable to false,
        calling its disconnect hardware method, and sleep for half a millisecond before
        program continues.
        """
        self.log(f"Wrapping up {self.device_key}")
        self.set_output(False)
        self.disconnect_hardware()
        t.sleep(.05)

    def __str__(self):
        """Returns the last known state of the device. Use getstate to inquire the state before calling"""
        self.get_state()
        return "Keysight 33500B Series Waveform Generator\nSettings:\n" + str(self.state)
