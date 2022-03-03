import pyvisa
import time as t
from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope

class KeysightOscilloscope(AbstractOscilloscope):
    def __init__(self, device_key = 'Keysight_Oscilloscope', config = None, resource_manager = None, parent = None):
        super().__init__(device_key = device_key, config = config, parent = parent)
        if resource_manager is not None:
            self.rm = resource_manager
        else:
            self.rm = pyvisa.ResourceManager()
        self.inst = None

    def connect_hardware(self):
        resources = self.rm.list_resources()
        self.inst = None
        for resource in resources:
            if "0x179B" in resource:
                try:
                    self.inst = self.rm.open_resource(resource)
                    self.inst.write("*OPC?")
                    self.inst.read()
                except:
                    pass
        if self.inst == None:
            self.log("Keysight oscilloscope not found", level='error')
        self.connected_signal.emit(True)




    def disconnect_hardware(self):
        try:
            self.inst.close()
            self.rm.close()
        except:
            pass
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

    """Shows text on the oscilloscope screen"""
    def DisplayText(self, text):
        self.inst.write(f"DISP:TEXT {text}")
        t.sleep(0.03)

    def getVertScale_V(self, channel):
        self.inst.write(f"CHAN{channel}:SCAL?")
        print(float(self.inst.read()))
        t.sleep(0.03)

    def setVertScale_V(self, volts_per_div, channel):
        self.inst.write(f"CHAN{channel}:SCAL {volts_per_div}")
        t.sleep(0.03)

    def getVertOffset(self, channel):
        self.inst.write(f"CHAN{channel}:OFFS?")
        print(float(self.inst.read()))
        t.sleep(0.03)

    def setVertOffset_V(self, channel, offset):
        self.inst.write(f"CHAN{channel}:OFFS {offset}")
        t.sleep(0.03)

    def getHorzScale_V(self):
        self.inst.write(f"TIM:SCAL?")
        print(float(self.inst.read()))

    def setHorzScale_sec(self, seconds):
        self.inst.write(f"TIM:SCAL {seconds}")
        t.sleep(0.03)

    def getHorzOffset_sec(self):
        self.inst.write("TIM:POS?")
        print(float(self.inst.read()))
        t.sleep(0.03)

    def setHorzOffset_sec(self, offset):
        self.inst.write(f"TIM:POS {offset}")
        t.sleep(0.03)

    def getFreq_Hz(self):
        self.inst.write("MEAS:FREQ?")
        print(float(self.inst.read()))
        t.sleep(0.03)

    def getAmp_V(self):
        self.inst.write("MEAS:VAMP?")
        print(float(self.inst.read()))
        t.sleep(0.03)

    def capture(self, channel):
        self.inst.write("WAV:POIN:MODE RAW")
        self.inst.write(f"WAV:SOUR:CHAN{channel}")
        self.inst.write("WAV:FORM ASCII")
        self.inst.write("WAV:PRE?")
        a = self.inst.read().split(",")

        # print(a)

        #if(a[1] == "+0"):
            #print("normal")
        #elif(a[1] == "+1"):
            #print("peak")
        #elif(a[1] == "+2"):
            #print("average")
        #else:
            #print("HRESolution")

        self.inst.write("WAV:DATA?")

        y_axis = self.inst.read().split(",")
        temp = y_axis[0].split()[-1]

        y_axis[0] = temp

        x_axis = (list(range(0, len(y_axis)-1)))

        #removes the metadata at the beginning
        y_axis.pop(0)

        for i in range(len(y_axis)):
            y_axis[i] = float(y_axis[i])

        return x_axis, y_axis


    """Sets up the condition that triggers a burst. If external is false, burst will occur at a constant period."""
    def SetTrigger(self, external:bool, period_s = .010, delay_s = 0, level_v = 3.3):
        self.inst.write(f"TRIG:DELAY {delay_s}")
        self.inst.write(f"TRIG:LEVEL {level_v}")
        if external:
            self.inst.write(f"TRIG:SOUR EXT")
        else:
            self.inst.write(f"TRIG SOUR TIM")
            self.inst.write(f"TRIG TIM {period_s}")
        t.sleep(0.03)

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
    osc.capture(1)
    osc.disconnect_hardware()
