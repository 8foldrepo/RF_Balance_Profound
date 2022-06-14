import time as t
from typing import Union, List, Tuple

import pyvisa

from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope
from Utilities.useful_methods import error_acceptable
from data_structures.variable_containers import OscilloscopePreamble


class KeysightOscilloscope(AbstractOscilloscope):
    """Class for interfacing with a Keysight InfiniVision 2002A Oscilloscope"""

    # These are not the only class variables, there are ones inherited from AbstractOscilloscope and AbstractDevice
    timeout_s: float

    autoset_timebase = "Autoset_timebase"

    def __init__(self, device_key='Keysight_Oscilloscope', config=None, resource_manager=None, parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)
        self.external_trigger = None
        self.average_count = None
        self.autorange_v = None
        self.time_of_flight_window = None
        self.connected = False
        if resource_manager is not None:
            self.rm = resource_manager
        else:
            self.rm = pyvisa.ResourceManager()
        self.inst = None

    def connect_hardware(self) -> Tuple[bool, str]:
        """Attempts to connect to the oscilloscope, handles errors and returns connection status and feedback"""
        self.log("Attempting to connect to oscilloscope...")
        feedback = ""
        try:
            resources = self.rm.list_resources()
        except pyvisa.errors.InvalidSession:
            self.rm = pyvisa.ResourceManager()
            resources = self.rm.list_resources()

        self.inst = None
        for resource in resources:
            if self.config[self.device_key]["identifier"] in str(resource):
                retries = 1
                while retries <= self.config[self.device_key]["retries"]:
                    try:
                        self.inst = self.rm.open_resource(resource)
                        self.connected = True
                        self.connected_signal.emit(True)
                        if self.config[self.device_key]["set_on_startup"]:
                            self.set_to_defaults()
                        self.log("Oscilloscope connected and set to default settings")
                        break
                    except pyvisa.errors.VisaIOError as e:
                        self.connected = False
                        self.connected_signal.emit(False)

                        if 'VI_ERROR_RSRC_NFOUND' in str(e):
                            feedback = f'Oscilloscope not connected, connect and retry: {e}'
                            # Do not retry
                            break
                        elif 'Unknown system error' in str(e):
                            feedback = f"Unknown oscilloscope system error, connect and retry"
                            # Do not retry
                            break
                        elif 'Device reported an input protocol error during transfer.' in str(e):
                            feedback = f"retry:{retries} Input protocol error, retrying"
                            # Retry
                        elif 'not currently the controller in charge' in str(e):
                            feedback = f"retry:{retries} Oscilloscope appears to be disconnected, " \
                                       f"retrying, otherwise check connection and restart it"
                            # Retry
                        elif 'Timeout' in str(e):
                            feedback = f"retry:{retries} Communication with the oscilloscope timed out, " \
                                       f"try restarting it"
                            # Retry
                        else:
                            feedback = f"retry:{retries} Unknown error: {e}"
                            # Retry
                        retries = retries + 1

        if not self.connected:
            self.log(level="error", message=feedback)
        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def clear(self) -> None:
        """Sends the pre-written Keysight clear command to the oscilloscope"""
        self.inst.clear()

    def reset(self) -> None:
        """Sends the pre-written Keysight reset command to the oscilloscope"""
        self.command("*RST")

    def disconnect_hardware(self) -> bool:
        """
        Checks if already disconnected, if not, attempts to disconnect with exception handling.
        Sets connected variable to false and emits signal
        """
        if self.inst is None:
            self.connected = False
            self.connected_signal.emit(False)
            return True  # already disconnected
        try:
            self.inst.close()
            self.connected = False
            self.connected_signal.emit(False)
            return True
        except pyvisa.errors.VisaIOError as e:
            self.log(level='error', message=f'could not disconnect oscilloscope: {e}')
            return False

    def set_to_defaults(self) -> None:
        """
        Sets all the internal class variables to default values specified in the config file.
        """
        self.reset()
        self.channel = self.config[self.device_key]['channel']
        self.range_s = (self.config['Oscilloscope_timebase']["Horizontal scale (us)"] * 10 ** -6) * 8
        self.offset_s = self.config['Oscilloscope_timebase']['Time offset (us)'] * 10 ** -6
        self.autorange_v = self.config[self.device_key]["autorange_v_startup"]
        self.range_mV = self.config[self.device_key]["range_mV"]
        self.average_count = self.config[self.device_key]["averages"]
        self.external_trigger = self.config[self.device_key]["ext_trigger"]
        self.timeout_s = self.config[self.device_key]["timeout_s"]

        self.setup(channel=self.channel, range_s=self.range_s, offset_s=self.offset_s, autorange_v=self.autorange_v,
                   range_v=self.range_mV / 1000,
                   ext_trigger=self.external_trigger, average_count=self.average_count)

    def setup(self, channel: int, range_s: float, offset_s: float, autorange_v: float, range_v: float, ext_trigger: bool, average_count: int) -> None:
        """
        This method relays to the oscilloscope a given set of parameters
        """
        self.set_horizontal_range_sec(range_s)
        self.set_horizontal_offset_sec(offset_s)
        if autorange_v:
            self.autoScale()
        else:
            self.set_vertical_range_V(channel=channel, volts=range_v)

        # Set averaging count
        self.set_averaging(averages=average_count)

        # Set trigger
        self.set_trigger(ext_trigger)

    def set_trigger(self, external: bool) -> None:
        """
        Define the conditions for an internal trigger of the oscilloscope.
        """
        # INFO: EDGE = identifies a trigger by looking for a specified slope and voltage level on a waveform.
        self.command(":TRIG:EDGE:SLOP POS")
        self.command(":TRIG:MODE EDGE")
        if external:
            self.command(":TRIG:EDGE:SOUR EXT")  # sets the trigger source to external
            self.command(
                ":TRIG:EDGE:LEV 2.5")  # INFO: LEV = sets the trigger level voltage for the active trigger source
        else:  # trigger is internal
            self.command(":TRIG:EDGE:SOUR CHAN1")
            self.command(":TRIG:EDGE:LEV .1")

    def set_averaging(self, averages: int = 1) -> None:
        """Sets the number of waveforms for the oscilloscope to average together (occurs in the oscilloscope itself)"""
        self.averages = averages
        if averages > 1:
            self.command(":ACQ:TYPE AVER")
            self.command(f":ACQ:COUN {averages}")
        else:
            self.command(":ACQ:TYPE HRES")  # sets oscilloscope in high resolution mode aka smoothing

    def get_vertical_scale_V(self, channel: int) -> float:
        """
        Retrieves the vertical scale in volts
        """
        return float(self.ask(f":CHAN{channel}:SCAL?"))

    def set_vertical_scale_V(self, volts_per_div: float, channel: int) -> None:
        """
        Sets the vertical scale of the oscilloscope screen when given the volts per division
        """
        self.command(f":CHAN{channel}:SCAL {volts_per_div}")
        self.range_mV = volts_per_div * 1000 * 8

    def get_vertical_range_V(self, channel: int) -> float:
        """
        Retrieves the vertical range in volts
        """
        return float(self.ask(f":CHAN{channel}:RANG?"))

    def set_vertical_range_V(self, channel: int, volts: float) -> None:
        """
        Sets the vertical range on the oscilloscope screen
        when given a volts and channel parameter
        """
        self.range_mV = volts * 1000
        self.command(f":CHAN{channel}:RANG {volts}")

    def get_vertical_offset_V(self, channel: int) -> float:
        """
        Retrieves the vertical offset in volts from 0 (the origin),
        parameter is int and return value is float
        """
        return float(self.ask(f":CHAN{channel}:OFFS?"))

    def set_vertical_offset_V(self, channel: int, offset: float) -> bool:
        """
        When given the channel and offset, this method changes the vertical
        offset of the screen to the given value
        """
        self.command(f":CHAN{channel}:OFFS {offset}")
        actual_offset_v = self.get_vertical_offset_V(channel=channel)
        if not error_acceptable(actual_offset_v, offset, 3, print_msg=False):
            self.log(level='error', message=f'Offset of {offset} V out of range, '
                                            f'oscilloscope voltage offset set to: {actual_offset_v} Volts')
            return False

    def get_horizontal_scale_sec(self) -> float:
        """
        Retrieves the horizontal scale in seconds as a float
        """
        scale_s = float(self.ask(f":TIM:SCAL?"))
        self.range_s = scale_s * 8
        return scale_s

    def set_horizontal_scale_sec(self, seconds: float) -> None:
        """Sets the horizontal scale in seconds with it being passed as a parameter"""
        self.command(f":TIM:SCAL {seconds}")
        self.range_s = 8 * seconds

    def get_horizontal_range_sec(self) -> float:
        """
        The range is 8 times the horizontal scale in seconds,
        so it returns the range in seconds as a float
        """
        self.range_s = float(self.ask(":TIM:RANG?"))
        return self.range_s

    def set_horizontal_range_sec(self, seconds: float) -> None:
        """Sets the horizontal range in seconds with it being passed as a float parameter"""
        self.range_s = seconds
        command = f":TIM:RANG {seconds}"
        self.command(command)

    def get_horizontal_offset_sec(self) -> float:
        """
        Retrieves the horizontal offset from 0 seconds (origin) from the oscilloscope. Return value is a float
        """
        self.offset_s = float(self.ask(":TIM:POS?"))
        return self.offset_s

    def set_horizontal_offset_sec(self, offset_s: float) -> bool:
        """
        Sets the horizontal offset of the oscilloscope screen in seconds when passed
        as a float parameter. Checks to ensure that offset does not exceed range
        """
        self.offset_s = offset_s
        self.command(f":TIM:POS {offset_s}")
        t.sleep(.03)
        actual_offset_s = self.get_horizontal_offset_sec()
        if not error_acceptable(actual_offset_s, offset_s, 2, print_msg=False):
            self.log(level='error', message=f'Offset of {offset_s}s out of range, '
                                            f'oscilloscope time offset set to: {actual_offset_s} seconds')
            return False
        return True

    # stretch: add automatic waveform finding
    def autoset_oscilloscope_timebase(self) -> None:
        """
        Sets the range and offset of the oscilloscope's time axis according to the config
        """
        range_s = (self.config['Oscilloscope_timebase']["Horizontal scale (us)"] * 10 ** -6) * 8
        offset_s = self.config['Oscilloscope_timebase']["Time offset (us)"]* 10 ** -6
        self.set_horizontal_range_sec(range_s)
        self.set_horizontal_offset_sec(offset_s)

    def get_frequency_Hz(self) -> float:
        """Returns the current frequency in Hz as a float value of the oscilloscope"""
        return float(self.ask(":MEAS:FREQ?"))

    def get_amplitude_V(self) -> float:
        """Returns the amplitude of the oscilloscope window in volts as a float"""
        return float(self.ask(":MEAS:VAMP?"))

    def autoScale(self) -> None:
        """Issues Keysight's built-in auto-scale command to the oscilloscope"""
        self.command(":AUT")

    def capture(self, channel: int) -> Tuple[List[float], List[float]]:
        """
        Captures the x-axis (seconds) and y-axis (volts) and returns the two respective float lists
        """
        if not self.connected:
            self.log(f"Could not capture, {self.device_key} is not connected")
            return [0.0], [0.0]

        # Ensure mode is ascii and read metadata
        preamble: Union[OscilloscopePreamble, None]
        preamble = None
        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            try:
                preamble = OscilloscopePreamble(self.ask("WAV:PRE?").split(","))

            except pyvisa.errors.VisaIOError as e:
                if "Timeout" not in str(e):
                    self.log(level="error",
                             message=f"Unknown error when asking for waveform preamble, retrying: {e}")
            if preamble is not None:
                if preamble.format_str == "+4":
                    break
                else:
                    preamble = None
                    self.command(f"WAV:FORM ASC")

        if preamble is None:
            self.log(level='error', message='preamble is none')
            return [0.0], [0.0]

        # self.command("WAV:POIN:MODE RAW")
        # Set capture source
        self.command(f"WAV:SOUR:CHAN{channel}")
        # self.command(f"WAV:FORM ASC")

        # Capture data
        voltages_v_strings = None
        start_time_2 = t.time()
        while t.time() - start_time_2 < self.timeout_s:
            try:
                voltages_v_strings = self.ask("WAV:DATA?").split(",")
            except pyvisa.errors.VisaIOError as e:
                if "Timeout" not in str(e):
                    self.log(level="error", message="Unknown error when asking for waveform preamble")
            if voltages_v_strings is not None:
                break

        # temp = voltages_v[0].split()[-1]  # QUESTION: do we need these two lines?
        # voltages_v[0] = temp
        # removes the metadata at the beginning
        if "#" in voltages_v_strings[0]:
            voltages_v_strings[0] = voltages_v_strings[0][10:]

        voltages_v = list()
        time_s = list()

        for i in range(len(voltages_v_strings)):
            try:
                voltages_v.append(float(voltages_v_strings[i]))
                time_s.append((i - preamble.x_reference) * preamble.sample_interval_s + preamble.x_origin)
            except ValueError:
                self.log(level="Error", message="An oscilloscope sample was not sent in a float format")

        return time_s, voltages_v

    # Waveform generator methods, unused, untested
    # def SetPeriod_s(self, channel, period_s):
    #     self.period_s = period_s
    #     Peri = "C" + channel + ":BTWV PRD,{}".format(self.period_s)
    #     self.command(Peri)
    #
    # def SetCycles(self, channel, cycle):
    #     self.cycles = cycle
    #     Cycl = "C" + channel + ":BTWV TIME," + self.cycles
    #     self.command(Cycl)

    def command(self, command: str) -> None:
        """
        Generic method that takes a command parameter and writes it to the oscilloscope, does not read the response,
        handles device not being
        """
        try:
            self.inst.write(command)
            t.sleep(.02)
        except AttributeError as e:
            if str(e) == "\'NoneType\' object has no attribute \'write\'":
                self.log(f"Could not send command {command}, {self.device_key} not connected")

    def read(self) -> str:
        """reads the current data that the oscilloscope has pending, handles device not being connected """
        try:
            return self.inst.read()
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'read'":
                self.log(level='error', message=f"Could not read reply, {self.device_key} Not connected")

    def ask(self, command: str) -> Union[str, None]:
        """generic method to send a command to the oscilloscope and return its response"""
        if not self.connected:
            self.log(level='error', message='cannot ask, oscilloscope is not connected')
            return None
        reply = self.inst.query(command)
        t.sleep(.02)
        return reply

    def get_serial_number(self) -> Union[str, None]:
        """Returns the serial number device reports after issuing Keysight command"""
        if not self.connected:
            return None

        out_str = self.ask("*IDN?")
        return out_str.split(",")[2]

    def get_rms(self) -> float:
        """
        asks the oscilloscope what the voltage root mean squared
        of the current window is and returns it as a float
        """
        rms = self.ask(":MEASure:VRMS?")
        return float(rms)

    def wrap_up(self) -> None:
        """Calls the disconnect hardware method"""
        self.disconnect_hardware()

    def __del__(self):
        if self.inst is not None:
            self.inst.close()


if __name__ == "__main__":
    osc = KeysightOscilloscope()
    osc.connect_hardware()

    while True:
        osc.capture(1)
