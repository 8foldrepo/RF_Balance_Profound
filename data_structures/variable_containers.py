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


class SystemInfo:
    rf_balance_sn: str
    oscilloscope_sn: str
    wtf_sn: str
    awg_sn: str
    forward_power_sn: str
    reflected_power_sn: str
    thermocouple_sn: str