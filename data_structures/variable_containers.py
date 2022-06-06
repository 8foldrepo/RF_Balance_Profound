from enum import Enum


class FrequencyRange(Enum):
    high_frequency = 1
    low_frequency = 2


class WaterLevel(Enum):
    below_level = 1
    level = 2
    above_level = 3

class FileMetadata:
    element_number: int
    X: float
    Theta: float
    frequency_MHz: float
    amplitude_mVpp: float
    source_signal_type: str
    num_cycles: int
    axis: str
    waveform_number: int
    nominal_low_frequency_MHz: float
    nominal_high_frequency_MHz: float
    y_units_str: str
    x_units_str: str

class SerialNumbers:
    rf_balance_sn: str
    oscilloscope_sn: str
    wtf_sn: str
    awg_sn: str
    forward_power_sn: str
    reflected_power_sn: str
    thermocouple_sn: str


class OscilloscopePreamble:
    preamble_list: list
    format_str: str
    num_points: int
    average_num: int
    sample_interval_s: float
    x_origin: float
    x_reference: float
    voltage_resolution_v: float
    y_origin: float
    y_reference: float

    def __init__(self, preamble: list):
        # Interpret preamble
        self.format_str = preamble[0]  # "+4" means ascii format
        if preamble[1] == "+0":
            self.mode = "normal"
        elif preamble[1] == "+1":
            self.mode = "peak"
        elif preamble[1] == "+2":
            self.mode = "average"
        else:
            self.mode = "HRESolution"

        self.num_points = int(preamble[2])
        self.average_num = int(preamble[3])
        self.sample_interval_s = float(preamble[4])
        self.x_origin = float(preamble[5])
        self.x_reference = float(preamble[6])
        self.voltage_resolution_v = float(preamble[7])
        self.y_origin = float(preamble[8])
        self.y_reference = float(preamble[9])
