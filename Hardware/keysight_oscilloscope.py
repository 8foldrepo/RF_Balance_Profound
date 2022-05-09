import time as t
import inspect
import pyvisa

from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope


class KeysightOscilloscope(AbstractOscilloscope):
    max_time_of_flight: float
    min_time_of_flight: float
    timeout_s: float
    range_mV: float
    channel: int
    averages: int
    range_s: int

    def __init__(self, device_key='Keysight_Oscilloscope', config=None, resource_manager=None, parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)
        self.connected = False
        if resource_manager is not None:
            self.rm = resource_manager
        else:
            self.rm = pyvisa.ResourceManager()
        self.inst = None

    def connect_hardware(self):
        self.log("Attempting to connect to oscilloscope...")
        feedback = ""
        resources = self.rm.list_resources()
        self.inst = None
        for resource in resources:
            if self.config[self.device_key]["identifier"] in resource:

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
        try:
            self.inst.close()
            self.rm.close()
        except pyvisa.errors.VisaIOError:
            pass
        self.connected = False
        self.connected_signal.emit(False)
        pass

    def set_to_defaults(self):
        self.reset()
        channel = self.config[self.device_key]['channel']
        self.max_time_of_flight = self.config["Autoset timebase"]["Max time of flight (us)"]
        self.min_time_of_flight = self.config["Autoset timebase"]["Min time of flight (us)"]
        range_s = self.config["Autoset timebase"]["Horizontal scale (us)"] * 10 ** -6
        time_of_flight_window = (self.max_time_of_flight - self.min_time_of_flight) / 1000000
        offset_s = self.min_time_of_flight / 1000000 + time_of_flight_window / 2
        autorange_V = self.config[self.device_key]["autorange_v_startup"]
        range_V = self.config[self.device_key]["range_mV"] / 1000
        average_count = self.config[self.device_key]["averages"]
        external_trigger = self.config[self.device_key]["ext_trigger"]
        self.timeout_s = self.config[self.device_key]["timeout_s"]

        self.setup(channel=channel, range_s=range_s, offset_s=offset_s, autorange_v=autorange_V, range_v=range_V,
                   ext_trigger=external_trigger, average_count=average_count)

    def setup(self, channel, range_s, offset_s, autorange_v, range_v, ext_trigger, average_count):
        self.setHorzRange_sec(range_s)
        self.setHorzOffset_sec(offset_s)
        if autorange_v:
            self.autoScale()
        else:
            self.setVertRange_V(channel=channel, volts=range_v)

        # Set averaging count
        self.SetAveraging(averages=average_count)

        # Set trigger
        self.SetTrigger(ext_trigger)

    def SetTrigger(self, external):
        """Sets whether or not to capture when triggered. If false the oscilloscope will capture continuously."""

        if external:
            self.command(":TRIG:MODE EDGE")
            self.command(":TRIG:EDGE:SOUR EXT")
            self.command(":TRIG:EDGE:SLOP POS")
        else:
            self.command(":TRIG:MODE EDGE")
            self.command(":TRIG:EDGE:SOUR CHAN1")
            self.command(":TRIG:EDGE:SLOP POS")

    def SetAveraging(self, averages=1):
        self.averages = averages
        if averages > 1:
            self.command(":ACQ:TYPE AVER")
            self.command(f":ACQ:COUN {averages}")
        else:
            self.command(":ACQ:TYPE HRES")

    """Shows text_item on the oscilloscope screen"""

    def DisplayText(self, text: str):
        self.command(f":DISP:TEXT {text}")

    def getVertScale_V(self, channel):
        return float(self.ask(f":CHAN{channel}:SCAL?"))

    def setVertScale_V(self, volts_per_div, channel):
        self.command(f":CHAN{channel}:SCAL {volts_per_div}")

    def getVertRange_V(self, channel):
        return float(self.ask(f":CHAN{channel}:RANG?"))

    def setVertRange_V(self, channel, volts):
        self.range_mV = volts * 1000
        self.command(f":CHAN{channel}:RANG {volts}")

    def getVertOffset(self, channel):
        return float(self.ask(f":CHAN{channel}:OFFS?"))

    def setVertOffset_V(self, channel, offset):
        self.command(f":CHAN{channel}:OFFS {offset}")

    def getHorzScale_V(self):
        return float(self.ask(f":TIM:SCAL?"))

    def setHorzScale_sec(self, seconds):
        self.command(f":TIM:SCAL {seconds}")

    def setHorzRange_sec(self, seconds):
        self.range_s = seconds
        command = f":TIM:RANG {seconds}"
        self.command(command)

    def getHorzOffset_sec(self):
        return float(self.ask(":TIM:POS?"))

    def setHorzOffset_sec(self, offset):
        self.offset_s = offset
        self.command(f":TIM:POS {offset}")

    # stretch: add automatic waveform finding
    def autoset_timebase(self):
        """Automatically sets the horizontal scale and range of the oscilloscope with a predetermined procedure"""

        self.max_time_of_flight = self.config["Autoset timebase"]["Max time of flight (us)"]
        self.min_time_of_flight = self.config["Autoset timebase"]["Min time of flight (us)"]
        range_s = self.config["Autoset timebase"]["Horizontal scale (us)"] * 10 ** -6
        time_of_flight_window = (self.max_time_of_flight - self.min_time_of_flight) / 1000000
        offset_s = self.min_time_of_flight / 1000000 + time_of_flight_window / 2
        self.setHorzRange_sec(range_s)
        self.setHorzOffset_sec(offset_s)

    def getFreq_Hz(self):
        return float(self.ask(":MEAS:FREQ?"))

    def getAmp_V(self):
        return float(self.ask(":MEAS:VAMP?"))

    def autoScale(self):
        self.command(":AUT")

    def capture(self, channel):
        # self.log(
        #     f"capture method called in keysight_oscilloscope.py, called by {inspect.getouterframes(inspect.currentframe(), 2)[1][3]}, channel is: {channel}")
        if self.connected:
            # self.command("WAV:POIN:MODE RAW")
            print(channel)
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

            while not preamble[0] == "+4":
                self.command(f"WAV:FORM ASC")

            # Interpret preamble
            if preamble[1] == "+0":
                mode = "normal"
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

    def command(self, command):
        # self.log(
        #     f"command method called in keysight_oscilloscope.py, called by {inspect.getouterframes(inspect.currentframe(), 2)[1][3]}, command is: {command}")
        try:
            self.inst.write(command)
            # t.sleep(.03)
        except AttributeError as e:
            if str(e) == "\'NoneType\' object has no attribute \'write\'":
                self.log(f"Could not send command {command}, {self.device_key} not connected")

    def read(self):
        # self.log(f"read method called in keysight_oscilloscope.py, called by {inspect.getouterframes(inspect.currentframe(), 2)[1][3]}")
        try:
            return self.inst.read()
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'read'":
                self.log(f"Could not read reply, {self.device_key} Not connected")

    def ask(self, command):
        return self.inst.query(command)

    # Todo: make sure this saves correctly in the systeminfo.ini
    def get_serial_number(self) -> str:
        if not self.connected:
            return None

        str = self.ask("*IDN?")
        return str.split(",")[2]


# Script/example code for testing out hardware class
if __name__ == "__main__":
    osc = KeysightOscilloscope()
    osc.connect_hardware()

    start_time = t.time()
    osc.setHorzScale_sec(.00001)
    for x in range(10):
        osc.capture(1)
        # print(f"capture method called, {x}th time")
    # print(f'elapsed time: {t.time() - start_time}')

    # may not be run if script is terminated early
    osc.disconnect_hardware()
