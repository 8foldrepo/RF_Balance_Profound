import pyvisa
import time as t
from PyQt5 import QtCore
from PyQt5.QtCore import QThread

rm = pyvisa.ResourceManager()

import logging
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import create_coord_rays
log_formatter = logging.Formatter(LOGGER_FORMAT)
file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class KeysightAWG:
    def __init__(self):
        self.inst = None

    def connect(self):
        resources = rm.list_resources()
        self.inst = None
        for resource in self.resources:
            if "0x2507" in resource:
                try:
                    self.inst = rm.open_resource(resource)
                except:
                    pass
        if self.inst == None:
            log_msg(self, root_logger,"Keysight 33509B Series function generator not found")

    def setup(self, channel, frequency, amplitude, period, cycles, output):
        self.SetOutput(channel, output)

    """Turns the output on or off"""
    def SetOutput(self, on: bool):
        if on:
            self.inst.write('OUTP ON')
        else:
            self.inst.write('OUTP OFF')
        t.sleep(0.03)

    """Sets the frequency of the signal"""
    def SetFrequency_Hz(self, frequency):
        self.inst.write(f"FREQ {frequency}")
        t.sleep(0.03)

    """Sets the peak to peak amplitude of the waveform in volts"""
    def SetAmplitude_V(self, amplitude):
        self.inst.write(f"VOLT {amplitude}")
        t.sleep(0.03)

    """Sets the dc offset of the waveform in volts"""
    def SetOffset_V(self, offset):
        self.inst.write(f"VOLT:OFF {offset}")
        t.sleep(0.03)


    """Shows text on the AWG screen"""
    def DisplayText(self, text):
        self.inst.write(f"DISP:TEXT {text}")
        t.sleep(0.03)

    def SetFunction(self, func = "SIN"):
        self.inst.write(f"FUNC {func}:")

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

    def SetBurst(self, on = True):
        if self.phase_degrees is not None:
            self.inst.write(f"BURS:PHAS {self.phase_degrees}")
        if on:
            self.inst.write("BURS ON")
        else:
            self.inst.write("BURS OFF")

    def SetOutputImpedence(self, impedence_ohms = 50, HiZ = False):
        if HiZ:
            self.inst.write("LOAD INF")
        else:
            self.inst.write(f"LOAD {impedence_ohms}")
        t.sleep(0.03)

    def SetPhase(self, phase_degrees=0):
        self.phase_degrees = phase_degrees
        self.inst.write(f"UNIT:ANGL DEG")
        self.inst.write(f"SOUR:PHASE{self.phase_degrees}")
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
    awg = KeysightAWG()
    awg.connect()
    awg.SetAmplitude_V(1)
    awg.SetBurst(True)
