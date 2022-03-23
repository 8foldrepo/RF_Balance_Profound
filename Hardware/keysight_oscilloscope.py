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
                    self.inst.write("*OPC?")
                    self.inst.read()
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
            self.inst.write('OUTP ON')
        else:
            self.inst.write('OUTP OFF')
        t.sleep(0.03)

    """Shows text_item on the oscilloscope screen"""
    def DisplayText(self, text):
        self.inst.write(f"DISP:TEXT {text}")
        t.sleep(0.03)

    def getVertScale_V(self, channel):
        self.inst.write(f"CHAN{channel}:SCAL?")
        return (float(self.inst.read()))
        t.sleep(0.03)

    def setVertScale_V(self, volts_per_div, channel):
        self.inst.write(f"CHAN{channel}:SCAL {volts_per_div}")
        t.sleep(0.03)

    def getVertRange_V(self, channel, volts):
        self.inst.write(f"CHAN{channel}:RANG?")
        return (float(self.inst.read()))
        t.sleep(0.03)

    def setVertRange_V(self, channel, volts):
        self.inst.write(f"CHAN{channel}:RANG {volts}")
        t.sleep(0.03)

    def getVertOffset(self, channel):
        self.inst.write(f"CHAN{channel}:OFFS?")
        return (float(self.inst.read()))
        t.sleep(0.03)

    def setVertOffset_V(self, channel, offset):
        self.inst.write(f"CHAN{channel}:OFFS {offset}")
        t.sleep(0.03)

    def getHorzScale_V(self):
        self.inst.write(f"TIM:SCAL?")
        return (float(self.inst.read()))

    def setHorzScale_sec(self, seconds):
        self.inst.write(f"TIM:SCAL {seconds}")
        t.sleep(0.03)

    def getHorzOffset_sec(self):
        self.inst.write("TIM:POS?")
        return (float(self.inst.read()))
        t.sleep(0.03)

    def setHorzOffset_sec(self, offset):
        self.inst.write(f"TIM:POS {offset}")
        t.sleep(0.03)

    def getFreq_Hz(self):
        self.inst.write("MEAS:FREQ?")
        return (float(self.inst.read()))
        t.sleep(0.03)

    def getAmp_V(self):
        self.inst.write("MEAS:VAMP?")
        return (float(self.inst.read()))
        t.sleep(0.03)

    def autoScale(self):
        self.inst.write(":AUT")
        t.sleep(0.03)

    def capture(self, channel):
        self.inst.write("WAV:POIN:MODE RAW")
        self.inst.write(f"WAV:SOUR:CHAN{channel}")
        self.inst.write("WAV:FORM ASCII")
        self.inst.write("WAV:PRE?")
        preamble = self.inst.read().split(",")

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
        self.inst.write("WAV:DATA?")
        voltages_v = self.inst.read().split(",")
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

    """Sets whether or not to capture when triggered. If false the oscilloscope will capture continuously."""
    def SetTrigger(self, trigger_on):
        if trigger_on:
            self.inst.write(f"TRIG:EDGE:SOUR EXT")
            self.inst.write(f"TRIG:MODE EDGE")
            self.inst.write(f"TRIG:EDGE:LEV 1")
            self.inst.write(f"TRIG:EDGE:SLOP POS")
        else:
            self.inst.write(f"TRIG:EDGE:SOUR LINE")

    """Sets the burst period of the waveform in seconds"""
    def SetPeriod_s(self, channel, period):
        self.Period = period
        Peri = "C" + channel + ":BTWV PRD,{}".format(self.Period)
        self.inst.write(Peri)
        t.sleep(0.03)


    def SetCycles(self, channel, cycle):
        self.Cycle = cycle
        Cycl = "C" + channel + ":BTWV TIME," + self.Cycle
        self.inst.write(Cycl)
        t.sleep(0.03)

    def AutosetTimebase(self):
        self.max_time_of_flight = self.config["Autoset timebase"]["Max time of flight (us)"]
        self.min_time_of_flight = self.config["Autoset timebase"]["Min time of flight (us)"]

        self.time_of_flight = (self.max_time_of_flight - self.min_time_of_flight)/10000000
        self.setHorzScale_sec(self.time_of_flight/1000000)
        self.setHorzOffset_sec(self.min_time_of_flight/1000000)


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
    osc.autoScale()
    osc.capture(1)
    osc.getHorzScale_V()
    osc.disconnect_hardware()