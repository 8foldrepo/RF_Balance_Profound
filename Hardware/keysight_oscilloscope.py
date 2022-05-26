
from sys import exit
import time as t
from typing import Union

import pyvisa
from termcolor import colored

from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope


class KeysightOscilloscope(AbstractOscilloscope):
    max_time_of_flight: float
    min_time_of_flight: float
    timeout_s: float
    range_mV: float
    channel: int
    averages: int
    range_s: float
    offset_s: float

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

    def connect_hardware(self):
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
                        else:
                            feedback = f"retry:{retries} Unknown error: {e}"
                            # Retry
                        retries = retries + 1

        if not self.connected:
            self.log(level="error", message=feedback)
        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def clear(self):
        self.inst.clear()

    def reset(self):
        self.command("*RST")

    def disconnect_hardware(self):
        if type(self.inst) is None:
            self.connected = False
            self.connected_signal.emit(False)
            return  # already disconnected
        try:
            self.inst.close()
            self.rm.close()
        except pyvisa.errors.VisaIOError:
            pass
        self.connected = False
        self.connected_signal.emit(False)
        pass  # todo: is this pass needed? sonarlint says otherwise

    def set_to_defaults(self):
        self.reset()
        self.channel = self.config[self.device_key]['channel']
        self.max_time_of_flight = self.config['Autoset timebase']["Max time of flight (us)"]
        self.min_time_of_flight = self.config['Autoset timebase']["Min time of flight (us)"]
        self.range_s = self.config['Autoset timebase']["Horizontal scale (us)"] * 10 ** -6
        self.time_of_flight_window = (self.max_time_of_flight - self.min_time_of_flight) / 1000000
        self.offset_s = self.min_time_of_flight / 1000000 + self.time_of_flight_window / 2
        self.autorange_v = self.config[self.device_key]["autorange_v_startup"]
        self.range_mV = self.config[self.device_key]["range_mV"]
        self.average_count = self.config[self.device_key]["averages"]
        self.external_trigger = self.config[self.device_key]["ext_trigger"]
        self.timeout_s = self.config[self.device_key]["timeout_s"]

        self.setup(channel=self.channel, range_s=self.range_s, offset_s=self.offset_s, autorange_v=self.autorange_v,
                   range_v=self.range_mV / 1000,
                   ext_trigger=self.external_trigger, average_count=self.average_count)

    def setup(self, channel, range_s, offset_s, autorange_v, range_v, ext_trigger, average_count):
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

    def set_trigger(self, external):
        self.command(":TRIG:EDGE:SLOP POS")
        self.command(":TRIG:MODE EDGE")
        if external:
            self.command(":TRIG:EDGE:SOUR EXT")
        else:
            self.command(":TRIG:EDGE:SOUR CHAN1")

    def set_averaging(self, averages=1):
        self.averages = averages
        if averages > 1:
            self.command(":ACQ:TYPE AVER")
            self.command(f":ACQ:COUN {averages}")
        else:
            self.command(":ACQ:TYPE HRES")

    def get_vertical_scale_V(self, channel):
        return float(self.ask(f":CHAN{channel}:SCAL?"))

    def set_vertical_scale_V(self, volts_per_div, channel: int) -> None:
        self.command(f":CHAN{channel}:SCAL {volts_per_div}")
        self.range_mV = volts_per_div * 1000 * 8

    def get_vertical_range_V(self, channel):
        return float(self.ask(f":CHAN{channel}:RANG?"))

    def set_vertical_range_V(self, channel: int, volts: float) -> None:
        self.range_mV = volts * 1000
        self.command(f":CHAN{channel}:RANG {volts}")

    def get_vertical_offset_V(self, channel: int) -> float:
        return float(self.ask(f":CHAN{channel}:OFFS?"))

    def set_vertical_offset_V(self, channel: int, offset: float) -> None:
        self.command(f":CHAN{channel}:OFFS {offset}")

        actual_offset_v = self.get_vertical_offset_V(channel=channel)
        if not actual_offset_v == offset:
            self.log(level='error', message=f'Value out of range, '
                                            f'oscilloscope voltage offset set to: {actual_offset_v} Volts')
            return False

    def get_horizontal_scale_sec(self) -> float:
        self.command(f":TIM:SCAL?")
        scale_s = float(self.inst.read())
        self.range_s = scale_s * 8
        return scale_s

    def set_horizontal_scale_sec(self, seconds: float) -> None:
        self.command(f":TIM:SCAL {seconds}")

    def get_horizontal_range_sec(self) -> float:
        return float(self.ask(":TIM:RANG?"))

    def set_horizontal_range_sec(self, seconds: float) -> None:
        self.range_s = seconds
        command = f":TIM:RANG {seconds}"
        self.command(command)



    def get_horizontal_offset_sec(self) -> float:
        return float(self.ask(":TIM:POS?"))

    def set_horizontal_offset_sec(self, offset: float) -> None:
        self.offset_s = offset
        self.command(f":TIM:POS {offset}")

        actual_offset_s = self.get_horizontal_offset_sec()
        if not actual_offset_s == self.offset_s:
            self.log(level='error', message=f'Value out of range, '
                                            f'oscilloscope time offset set to: {actual_offset_s} seconds')
            return False

    # stretch: add automatic waveform finding
    def autoset_oscilloscope_timebase(self):
        self.max_time_of_flight = self.config['Autoset timebase']["Max time of flight (us)"]
        self.min_time_of_flight = self.config['Autoset timebase']["Min time of flight (us)"]
        range_s = self.config['Autoset timebase']["Horizontal scale (us)"] * 10 ** -6
        time_of_flight_window = (self.max_time_of_flight - self.min_time_of_flight) / 1000000
        offset_s = self.min_time_of_flight / 1000000 + time_of_flight_window / 2
        self.set_horizontal_range_sec(range_s)
        self.set_horizontal_offset_sec(offset_s)

    def get_frequency_Hz(self) -> float:
        return float(self.ask(":MEAS:FREQ?"))

    def get_amplitude_V(self) -> float:
        return float(self.ask(":MEAS:VAMP?"))

    def autoScale(self):
        self.command(":AUT")

    def capture(self, channel):
        # self.log(
        #     f"capture method called in keysight_oscilloscope.py, called by {inspect.getouterframes(inspect.currentframe(), 2)[1][3]}, channel is: {channel}")
        if self.connected:
            # self.command("WAV:POIN:MODE RAW")
            self.command(f"WAV:SOUR:CHAN{channel}")
            self.command(f"WAV:FORM ASC")

            preamble = None
            start_time = t.time()
            while t.time() - start_time < self.timeout_s:
                try:
                    preamble = self.ask("WAV:PRE?").split(",")
                except pyvisa.errors.VisaIOError as e:
                    if "Timeout" in str(e):
                        pass
                    else:
                        self.log(level="error",
                                 message=f"Unknown error when asking for waveform preamble, retrying: {e}")
                if preamble is not None:
                    break

            if preamble is None:
                return

            while preamble[0] != "+4":
                self.command(f"WAV:FORM ASC")

            # Interpret preamble
            if preamble[1] == "+0":
                mode = "normal"  # todo: mode is not being used, why is this here?
            elif preamble[1] == "+1":
                mode = "peak"
            elif preamble[1] == "+2":
                mode = "average"
            else:
                mode = "HRESolution"

            num_points = int(preamble[2])
            average_num = preamble[3]
            sample_interval_s = float(preamble[4])
            x_origin = float(preamble[5])
            x_reference = float(preamble[6])
            voltage_resolution_v = float(preamble[7])
            y_origin = float(preamble[8])
            y_reference = float(preamble[9])

            # Capture data
            voltages_v_strings = None
            start_time_2 = t.time()
            while t.time() - start_time_2 < self.timeout_s:
                try:
                    voltages_v_strings = self.ask("WAV:DATA?").split(",")
                except pyvisa.errors.VisaIOError as e:
                    if "Timeout" in str(e):
                        pass
                    else:
                        self.log(level="error", message="Unknown error when asking for waveform preamble")
                if voltages_v_strings is not None:
                    break

            # temp = voltages_v[0].split()[-1]
            # voltages_v[0] = temp
            # removes the metadata at the beginning
            if "#" in voltages_v_strings[0]:
                voltages_v_strings[0] = voltages_v_strings[0][10:]

            voltages_v = list()
            time_s = list()

            for i in range(len(voltages_v_strings)):
                try:
                    voltages_v.append(float(voltages_v_strings[i]))
                    time_s.append((i - x_reference) * sample_interval_s + x_origin)
                except ValueError:
                    self.log(level="Error", message="An oscilloscope sample was not sent in a float format")

            return time_s, voltages_v
        else:
            self.log(f"Could not capture, {self.device_key} is not connected")
            return [0], [0]

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
        """Generic method that takes a command parameter and writes it to the oscilloscope, does not read the response,
        handles device not being"""
        try:
            self.inst.write(command)
            t.sleep(.03)
        except AttributeError as e:
            if str(e) == "\'NoneType\' object has no attribute \'write\'":
                self.log(f"Could not send command {command}, {self.device_key} not connected")

    def read(self):
        """reads the current data that the oscilloscope has pending, handles device not being connected """
        try:
            return self.inst.read()
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'read'":
                self.log(f"Could not read reply, {self.device_key} Not connected")

    def ask(self, command:str) -> Union[str, None]:
        """generic method to send a command to the oscilloscope and return its response"""
        if not self.connected:
            return None

        reply = self.inst.query(command)
        t.sleep(.03)
        return reply

    def get_serial_number(self) -> Union[str,None]:
        if not self.connected:
            return None

        str = self.ask("*IDN?")
        return str.split(",")[2]

    def get_rms(self) -> float:

        """asks the oscilloscope what the voltage root mean squared of the current window is and returns it as a
        float"""
        rms = self.ask(":MEASure:VRMS?")
        return float(rms)


def error_acceptable(value1: float, value2: float) -> bool:
    print(colored(f'value1 = {value1}, value2 = {value2}','yellow'))
    if value1 == 0:
        print("value is 0")
        return False
    return abs((value1 - value2) / value1) * 100 < 6

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

# Script/example code for testing out hardware class
if __name__ == "__main__":
    import random
    from signal import signal, SIGINT
    signal(SIGINT, handler)

    osc = KeysightOscilloscope()
    osc.connect_hardware()

    osc.set_horizontal_scale_sec(5.704571933249891)


    assert osc.config is not None

    # test a random sequence of operations 10 times
    for i in range(10):
        step_sequence = list(range(11))
        random.shuffle(step_sequence)

        # todo: figure out true limits in certain variables
        for step_number in step_sequence:
            if step_number == 0:  # TEST: set to defaults
                print(colored("running set to default test", 'cyan'))
                osc.set_to_defaults()
                assert error_acceptable(osc.channel, osc.config[osc.device_key]['channel'])
                assert error_acceptable(osc.max_time_of_flight, osc.config['Autoset timebase']["Max time of flight (us)"])
                assert osc.min_time_of_flight == osc.config['Autoset timebase']["Min time of flight (us)"]
                assert error_acceptable(osc.range_s, osc.config['Autoset timebase']["Horizontal scale (us)"] * 10 ** -6)
                assert error_acceptable(osc.time_of_flight_window, (osc.max_time_of_flight - osc.min_time_of_flight) / 1000000)
                assert error_acceptable(osc.offset_s, osc.min_time_of_flight / 1000000 + osc.time_of_flight_window / 2)
                assert osc.autorange_v == bool(osc.config[osc.device_key]["autorange_v_startup"])
                assert error_acceptable(osc.range_mV, osc.config[osc.device_key]["range_mV"])
                assert error_acceptable(osc.average_count, osc.config[osc.device_key]["averages"])
                assert osc.external_trigger == osc.config[osc.device_key]["ext_trigger"]
                assert error_acceptable(osc.timeout_s, osc.config[osc.device_key]["timeout_s"])
            if step_number == 1:  # TEST: disconnect hardware
                print(colored("running disconnect hardware test", 'cyan'))
                osc.disconnect_hardware()
                assert not osc.connected
                osc.connect_hardware()
            if step_number == 2:  # TEST: set averaging
                print(colored("running set averaging test", 'cyan'))
                averages = random.randrange(1, 10)
                osc.set_averaging(averages=averages)
                assert error_acceptable(osc.averages, averages)
                if averages > 1:
                    type1 = osc.ask(":ACQ:TYPE?")
                    assert type1 == "AVER\n"
                    assert error_acceptable(int(osc.ask(":ACQ:COUN?")), int(averages))
                else:
                    type2 = osc.ask(":ACQ:TYPE?")
                    assert type2 == "HRES\n"
            if step_number == 3:  # TEST: set trigger
                print(colored("running set trigger test", 'cyan'))
                external = bool(random.getrandbits(1))
                osc.set_trigger(external=external)
                trig_mode = osc.ask(":TRIG:MODE?")
                mode = osc.ask(":TRIG:MODE?")
                assert mode == "EDGE\n"
                assert osc.ask(":TRIG:EDGE:SLOP?") == "POS\n"
                if external:
                    assert osc.ask(":TRIG:EDGE:SOUR?")=="EXT\n"
                else:
                    assert osc.ask(":TRIG:EDGE:SOUR?")=="CHAN1\n"
            # horizontal commands ----------------------------------------------------
            if step_number == 4:  # TEST: horizontal scale (s)
                print(colored("running horizontal scale test", 'cyan'))
                seconds = random.uniform(0, 10)
                osc.set_horizontal_scale_sec(seconds=seconds)
                assert error_acceptable(osc.get_horizontal_scale_sec(), seconds)
            if step_number == 5:  # TEST: horizontal range sec (s)
                print(colored("running horizontal range test", 'cyan'))
                seconds = random.randrange(1, 30)  # set range between 1 and 30 seconds
                osc.set_horizontal_range_sec(seconds=float(seconds))
                assert error_acceptable(osc.get_horizontal_range_sec(), float(seconds))
                assert error_acceptable(osc.range_s, float(seconds))
            if step_number == 6:  # TEST: horizontal offset (s)
                print(colored("running horizontal offset test", 'cyan'))
                offset_seconds = random.uniform(-500, 500)
                in_range = osc.set_horizontal_offset_sec(offset=offset_seconds)
                assert error_acceptable(osc.get_horizontal_offset_sec(), offset_seconds) or not in_range
                assert error_acceptable(osc.offset_s, offset_seconds)
            # vertical commands -----------------------------------------------------
            if step_number == 7:  # TEST: vertical scale (V)
                print(colored("running vertical scale test", 'cyan'))
                scale1 = random.uniform(0.1, 50)
                osc.set_vertical_scale_V(channel=1, volts_per_div=scale1)
                scale2 = osc.get_vertical_scale_V(channel=1)
                assert error_acceptable(scale1, scale2)
                assert error_acceptable(osc.range_mV/1000, 8 * scale1)
            if step_number == 8:  # TEST: vertical range (V)
                print(colored("running vertical range test", 'cyan'))
                range_V = random.uniform(.01, 50)
                osc.set_vertical_range_V(channel=1, volts=range_V)
                assert error_acceptable(osc.get_vertical_range_V(channel=1), range_V)
                assert error_acceptable(osc.range_mV, range_V * 1000)
            if step_number == 9:  # TEST: vertical offset (V)
                print(colored("running vertical offset test", 'cyan'))
                offset_V = random.uniform(-20, 20)
                osc.set_vertical_offset_V(channel=1, offset=offset_V)
                assert error_acceptable(osc.get_vertical_offset_V(channel=1), offset_V)
            # -------------------------------------------------------------
            if step_number == 10:  # TEST: autoset timebase
                print(colored("running autoset timebase test", 'cyan'))
                osc.autoset_oscilloscope_timebase()
                assert error_acceptable(osc.max_time_of_flight, osc.config['Autoset timebase']["Max time of flight (us)"])
                assert error_acceptable(osc.min_time_of_flight, osc.config['Autoset timebase']["Min time of flight (us)"])
                assert error_acceptable(osc.range_s, osc.config['Autoset timebase']["Horizontal scale (us)"] * 10 ** -6)
                assert error_acceptable(osc.time_of_flight_window, (osc.max_time_of_flight - osc.min_time_of_flight) / 1000000)
                assert error_acceptable(osc.offset_s, osc.min_time_of_flight / 1000000 + osc.time_of_flight_window / 2)
                osc.set_horizontal_range_sec(osc.range_s)
                osc.set_horizontal_offset_sec(osc.offset_s)
                assert error_acceptable(osc.get_horizontal_range_sec(), osc.range_s)
                assert error_acceptable(osc.get_horizontal_offset_sec(), osc.offset_s)

    osc.disconnect_hardware()
    print("Test passed :)")


