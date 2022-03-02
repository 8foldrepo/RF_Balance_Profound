import pyvisa
import time as t
from PyQt5 import QtCore

rm = pyvisa.ResourceManager()


class KeysightAWG:
    def __init__(
        self, frequency, amplitude, period, cycles, C1output, C2output, device=None
    ):
        if device is not None:
            print("setting device")
            self.inst = device
        else:
            self.resources = rm.list_resources()
            print(self.resources)
            self.inst = None
            for resource in self.resources:
                print(resource)
                if "SDG" in resource:
                    try:
                        self.inst = rm.open_resource(resource)
                    except:
                        pass
            if self.inst == None:
                self.logger_signal.emit("Siglent function generator not found")

        self.setup("1", frequency, amplitude, period, cycles, C1output)
        self.setup("2", frequency, amplitude, period, cycles, C2output)

    def setup(self, channel, frequency, amplitude, period, cycles, output):
        self.SetOutput(channel, output)

        self.inst.write("C" + channel + ":BTWV STATE,ON")
        t.sleep(0.01)
        self.inst.write("C" + channel + ":BSWV STPS,0")
        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV INT")
        t.sleep(0.005)

        self.inst.write("C1:BTWV TRMD,OFF")
        t.sleep(0.005)
        self.inst.write("C2:BTWV TRMD,OFF")
        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV TRMD,RISE")

        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV DLAY, 2.4e-07S")
        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV GATE_NCYC,NCYC")
        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV CARR,OFST,0")
        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV CARR,WVTP,SINE")
        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV CARR,PHSE,0")
        t.sleep(0.005)
        self.SetFrequency(channel, frequency)
        self.SetAmplitude(channel, amplitude)
        self.SetPeriod(channel, period)
        self.SetCycles(channel, cycles)

    def SetFrequency(self, channel, frequency):
        self.Frequency = frequency
        Frq = "C" + channel + ":BSWV FRQ,{}".format(self.Frequency)
        self.inst.write(Frq)
        t.sleep(0.03)

    def SetAmplitude(self, channel, amplitude):
        self.Amplitude = amplitude
        Amp = "C" + channel + ":BSWV AMP,{}".format(self.Amplitude)
        self.inst.write(Amp)
        t.sleep(0.03)

    def SetPeriod(self, channel, period):
        self.Period = period
        Peri = "C" + channel + ":BTWV PRD,{}".format(self.Period)
        self.inst.write(Peri)
        t.sleep(0.03)

    def SetCycles(self, channel, cycle):
        self.Cycle = cycle
        Cycl = "C" + channel + ":BTWV TIME," + self.Cycle
        self.inst.write(Cycl)
        t.sleep(0.03)

    def SetOutput(self, channel, output):
        self.Output = output
        OutPut = "C" + channel + ":OUTP {},LOAD,50".format(self.Output)
        self.inst.write("C1:BTWV TRMD,OFF")
        t.sleep(0.005)
        self.inst.write("C2:BTWV TRMD,OFF")
        t.sleep(0.005)
        self.inst.write("C" + channel + ":BTWV TRMD,RISE")
        self.inst.write(OutPut)
        t.sleep(0.03)


my_FunctionGenerator = KeysightAWG(frequency = '1000000',amplitude = '10', period = '.0001', cycles = '2', C1output = 'ON', C2output= 'ON')