from typing import Tuple, Union

from PyQt5 import QtCore

from Hardware.Abstract.abstract_awg import AbstractAWG
from Utilities.load_config import *


class SimulatedAWG(AbstractAWG):
    output_signal = QtCore.pyqtSignal(bool)

    def __init__(self, config=None, device_key="Keysight_AWG", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        self.function = None
        self.offset = None
        self.state = dict()
        self.fields_setup()
        self.set_to_defaults()

    def fields_setup(self) -> None:
        """
        sets internal config variable to return result of load_configuration
        in Utilities/load_config if class' internal config is none
        """
        if self.config is None:
            self.config = load_configuration()

    def set_to_defaults(self) -> None:
        """
        Calls the setup() method in this class, passing default values from the config's function generator section
        """
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

    def connect_hardware(self) -> Tuple[bool, str]:
        """
        Calls the setup method with 4.29 MHz and 0.1V, sets connected flag to true and emits it. User

        :return: A tuple, first value being a bool of whether it's connected, second value being an empty string
        """
        self.setup(frequency_Hz=4290000, amplitude_V=0.1)
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self) -> None:
        """
        sets connected flag to false and emits false via 'connected_signal'
        """
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
        self.set_trigger_output(True)
        self.set_offset_v(offset_V)
        self.set_output_impedance(output_Impedance)
        self.wait_til_complete()

    def get_state(self) -> dict:
        """
        Inquires all key AWG settings, and returns a dictionary containing their names and values

        :returns: dictionary representing all configuration variables from the AWG
        """
        self.get_output()
        self.get_frequency_hz()
        self.get_amplitude_v()
        self.get_burst()
        self.get_trigger_output()
        self.get_offset_v()
        self.get_output_impedance()
        return self.state

    def reset(self) -> None:
        """
        Relay method for set_to_default() and wait_til_complete()
        """
        self.set_to_defaults()
        self.wait_til_complete()

    def wait_til_complete(self) -> None:
        """
        Currently does nothing; placeholder for abstract_awg compliance
        """
        pass

    def set_output(self, on: bool) -> None:
        """
        Turns the output on or off

        :param on: boolean value representing whether function generator output is on or off
        """
        self.state["on"] = on
        self.output_signal.emit(on)

    def get_output(self) -> bool:
        """
        Getter for 'on' value in self.state dictionary, also emits output_signal
        (connected to main window indicator and RFB logger method)

        :return: if true, output is on and vice versa
        """
        self.output_signal.emit(self.state["on"])
        return self.state["on"]

    def set_frequency_hz(self, frequency_hz: float) -> None:
        """
        Sets the frequency of the AWG function, emits frequency
        signal (connected to update_frequency_field() in main window)

        :param frequency_hz: The frequency in hertz you want to set the function generator to
        """
        self.state["frequency_Hz"] = frequency_hz
        self.frequency_signal.emit(frequency_hz / 1000000)

    def get_frequency_hz(self) -> float:
        """
        getter method for the 'frequency_Hz' value class' state dictionary

        :return: the frequency in hertz the function generator is set to
        """
        return float(self.state["frequency_Hz"])

    def set_amplitude_v(self, amplitude: float) -> None:
        """
        Sets the peak to peak amplitude of the waveform in volts

        :param amplitude: in volts, the range of the function outputted
        """
        self.state["amplitude_V"] = amplitude

    def get_amplitude_v(self) -> float:
        """
        Getter method for AWG's voltage amplitude

        :return: Amplitude in volts that the AWG currently has stored within it
        """
        return float(self.state["amplitude_V"])

    def set_offset_v(self, offset: Union[int, float]) -> None:
        """Sets the dc offset of the waveform in volts"""
        self.offset = float(offset)
        self.state['offset'] = float(offset)

    def get_offset_v(self) -> float:
        """
        Getter for vertical range offset (voltage axis) in floats

        :return: Voltage offset in volts, float type
        """
        return self.offset

    def set_functions(self, func: str = "SIN"):
        """
        sets the general function formation mode; can be SIN (sine), SQU (square), RAMP, PULS
        (pulse), ARB (arbitrary), TRI (triangle), DC, NOIS, PRBS (pseudo-random noise)

        :param func: default value is "SIN"; general shape of the output function
        """
        import re
        match_list = re.findall(r'SIN|SQU|RAMP|PULS|ARB|TRI|DC|NOIS|PRBS', func, re.IGNORECASE)
        if not any(match_list):
            self.log(message=f"invalid function '{func}' passed to set_function() in "
                             f"simulated_awg.py, defaulting to SIN", level='warning')
            self.function = 'SIN'
            self.state['function'] = 'SIN'
            return
        self.function = func
        self.state['function'] = func

    def get_function(self) -> str:
        """
        Returns the function form the AWG is currently using (i.e. sine, triangle, square, etc.)
        """
        return self.function

    def set_burst(self, on: bool = True) -> None:
        """
        Setter for the burst key in the state dictionary

        :param on: bool value to be passed representing user's intention of turning on burst on or not
        """
        self.state["burst_on"] = on

    def get_burst(self) -> Tuple[bool, int]:
        """
        getter for the burst toggle in the state dictionary and integer representation of the number of cycles

        :return: (bool, int) indicating if the AWG is in burst mode; integer containing the number of cycles per burst
        """

        return self.state["burst_on"], int(self.state["burst_cycles"])

    def set_output_impedance(self, impedance_ohms: Union[int, float] = 50, hi_z: bool = False) -> None:
        """
        Setter for the AWG's output resistance/impedance

        :param impedance_ohms: The output resistance to pass to the AWG's state dict in ohms (int or float)
        :param hi_z: flag for maximum impedance
        """
        if hi_z:
            self.state["output impedance"] = float(99999999)
        else:
            self.state["output impedance"] = float(impedance_ohms)

    def get_output_impedance(self) -> float:
        """
        Getter for the output resistance/impedance of the AWG
        :return: output resistance/impedance of the AWG in float type format
        """
        return float(self.state["output impedance"])

    def set_phase_degrees(self, phase_degrees: Union[int, float] = 0) -> None:
        """
        Setter for the AWG's phase shift in degrees

        :param phase_degrees: the phase degrees you want the AWG's state dict to have (int or float); default 0
        """
        self.state["phase degrees"] = float(phase_degrees)

    def get_phase_degrees(self) -> float:
        """
        Getter for the AWG's phase shift in degrees

        :return: the float representation of the AWG's phase degrees via its state dict
        """
        return float(self.state["phase degrees"])

    def set_cycles(self, cycles: int) -> None:
        """
        Setter for the number of cycles to display/capture from the AWG in a single frame

        :param cycles: integer representing the number of cycles to display/capture from the AWG in a single frame.
        """
        self.state["burst_cycles"] = cycles

    def get_cycles(self) -> int:
        """
        Getter for the number of cycles in the AWG's state dictionary

        :return: integer representation of the number of cycles in the AWG's state dictionary'
        """
        return int(self.state["burst_cycles"])

    def set_trigger_output(self, trigger_out: bool):
        self.state["trig_out"] = trigger_out

    def get_trigger_output(self) -> bool:
        return self.state["trig_out"]

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
