import pyvisa
import time as t
import cProfile
import pstats
from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope

class KeysightOscilloscope(AbstractOscilloscope):
    def __init__(self, device_key = 'Keysight_Oscilloscope', config = None, resource_manager = None, parent = None):
        super().__init__(device_key = device_key, config = config, parent = parent)
        self.connected = False
        if resource_manager is not None:
            self.rm = resource_manager
        else:
            self.rm = pyvisa.ResourceManager()
        self.inst = None

    def connect_hardware(self):
        resources = self.rm.list_resources()
        self.inst = None
        for resource in resources:
            if self.config[self.device_key]["identifier"] in resource:
                try:
                    self.inst = self.rm.open_resource(resource)
                    self.command("*OPC?")
                    self.read()
                    self.AutosetTimebase()
                    self.connected = True
                    self.connected_signal.emit(True)
                except pyvisa.errors.VisaIOError as e:
                    self.connected = False
                    self.connected_signal.emit(False)
                    self.log(level='error', message=f"Could not connect to oscilloscope, try restarting it: {e}")
                    #self.autoScale()
                    #self.SetTrigger(True)
        if self.inst == None:
            self.log("Keysight oscilloscope not found", level='error')

    def disconnect_hardware(self):
        try:
            self.inst.close()
            self.rm.close()
        except:
            pass
        self.connected = False
        self.connected_signal.emit(False)
        pass

    def setup(self, channel, frequency, amplitude, period, cycles, output):
        self.SetOutput(channel, output)

    """Turns the output on or off"""
    def SetOutput(self, on: bool):
        if on:
            self.command('OUTP ON')
        else:
            self.command('OUTP OFF')
        t.sleep(0.03)

    """Shows text_item on the oscilloscope screen"""
    def DisplayText(self, text):
        self.command(f"DISP:TEXT {text}")
        t.sleep(0.03)

    def getVertScale_V(self, channel):
        self.command(f"CHAN{channel}:SCAL?")
        return (float(self.read()))
        t.sleep(0.03)

    def setVertScale_V(self, volts_per_div, channel):
        self.command(f"CHAN{channel}:SCAL {volts_per_div}")
        t.sleep(0.03)

    def getVertRange_V(self, channel, volts):
        self.command(f"CHAN{channel}:RANG?")
        return (float(self.read()))
        t.sleep(0.03)

    def setVertRange_V(self, channel, volts):
        self.command(f"CHAN{channel}:RANG {volts}")
        t.sleep(0.03)

    def getVertOffset(self, channel):
        self.command(f"CHAN{channel}:OFFS?")
        return (float(self.read()))
        t.sleep(0.03)

    def setVertOffset_V(self, channel, offset):
        self.command(f"CHAN{channel}:OFFS {offset}")
        t.sleep(0.03)

    def getHorzScale_V(self):
        self.command(f"TIM:SCAL?")
        return (float(self.read()))

    def setHorzScale_sec(self, seconds):
        self.command(f"TIM:SCAL {seconds}")
        t.sleep(0.03)

    def getHorzOffset_sec(self):
        self.command("TIM:POS?")
        return (float(self.read()))
        t.sleep(0.03)

    def setHorzOffset_sec(self, offset):
        self.command(f"TIM:POS {offset}")
        t.sleep(0.03)

    def getFreq_Hz(self):
        self.command("MEAS:FREQ?")
        return (float(self.read()))
        t.sleep(0.03)

    def getAmp_V(self):
        self.command("MEAS:VAMP?")
        return (float(self.read()))
        t.sleep(0.03)

    def autoScale(self):
        self.command(":AUT")
        t.sleep(0.03)

    def capture(self, channel):
        if self.connected:
            self.command("WAV:POIN:MODE RAW")
            self.command(f"WAV:SOUR:CHAN{channel}")
            self.command("WAV:FORM ASCII")
            self.command("WAV:PRE?")
            preamble = self.read().split(",")

            #check that data is in ascii format
            if not preamble[0] == '+4':
                self.log(level='error', message='Oscilloscope data in unrecognized format, try restarting it.')

            #Interpret preamble
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

            #Capture data
            self.command("WAV:DATA?")
            voltages_v = self.read().split(",")
            #temp = voltages_v[0].split()[-1]
            #voltages_v[0] = temp
            # removes the metadata at the beginning
            if '#' in voltages_v[0]:
                voltages_v[0] = voltages_v[0][10:]

            for i in range(len(voltages_v)):
                voltages_v[i] = float(voltages_v[i])

            #Create time array
            times_s = [0] * num_points
            for i in range(0, num_points):
                times_s[i] = (i-x_reference)*sample_interval_s + x_origin

            return times_s, voltages_v
        else:
            self.log(f"Could not capture, {self.device_key} is not connected")
            return [0],[0]

    """Sets whether or not to capture when triggered. If false the oscilloscope will capture continuously."""
    def SetTrigger(self, trigger_on):
        if trigger_on:
            self.command(f"TRIG:EDGE:SOUR EXT")
            self.command(f"TRIG:MODE EDGE")
            self.command(f"TRIG:EDGE:LEV 1")
            self.command(f"TRIG:EDGE:SLOP POS")
        else:
            self.command(f"TRIG:EDGE:SOUR LINE")

    """Sets the burst period of the waveform in seconds"""
    def SetPeriod_s(self, channel, period):
        self.Period = period
        Peri = "C" + channel + ":BTWV PRD,{}".format(self.Period)
        self.command(Peri)
        t.sleep(0.03)


    def SetCycles(self, channel, cycle):
        self.Cycle = cycle
        Cycl = "C" + channel + ":BTWV TIME," + self.Cycle
        self.command(Cycl)
        t.sleep(0.03)

    def AutosetTimebase(self):
        self.max_time_of_flight = self.config["Autoset timebase"]["Max time of flight (us)"]
        self.min_time_of_flight = self.config["Autoset timebase"]["Min time of flight (us)"]

        self.horizontal_div_s = (self.max_time_of_flight - self.min_time_of_flight)/10000000
        self.setHorzScale_sec(self.horizontal_div_s)
        self.setHorzOffset_sec(self.min_time_of_flight/1000000+4*self.horizontal_div_s)

    def command(self, command):
        try:
            self.self.inst.write(command)
        except AttributeError as e:
            if str(e) == "\'NoneType\' object has no attribute \'write\'":
                self.log(f"Could not send command {command}, {self.device_key} not connected")

    def read(self):
        try:
            return self.inst.read()
        except AttributeError as e:
            if str(e) == "\'NoneType\' object has no attribute \'read\'":
                self.log(f"Could not read reply, {self.device_key} Not connected")

if __name__ == "__main__":
    osc = KeysightOscilloscope()
    osc.connect_hardware()
    # osc.setVertScale_V(0.05, 1)
    # osc.getVertScale_V(1)
    # osc.setHorzScale_Sec(.000000013)
    # osc.getHorzScale_V()
    # osc.setHorzOffset_sec(0.0)
    # osc.getHorzOffset_sec()
    # osc.getFreq_Hz()
    # osc.getAmp_V()
    #osc.autoScale()
    osc.SetTrigger(True)
    #osc.setVertRange_V(1,