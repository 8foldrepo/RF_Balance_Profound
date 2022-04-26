from abc import abstractmethod, ABC
from typing import Tuple, List
from Hardware.Abstract.abstract_device import AbstractDevice

'''Defines key functionalities for oscilloscopes'''


class AbstractOscilloscope(AbstractDevice):
    range_mv: float
    channel: int
    averages: int
    capture_period_ns: int
    signal_frequency_MHz: float
    signal_period_ns: float
    cycles: int
    delay_cycles: float
    captures: int

    def __init__(self, device_key='Keysight_Oscilloscope', config=None, parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)

    @abstractmethod
    def reset(self):
        ...

    @abstractmethod
    def set_to_defaults(self):
        ...

    @abstractmethod
    def setup(self, channel, range_s, offset_s, autorange_v, range_v, ext_trigger, average_count):
        ...

    """Sets whether or not to capture when triggered. If false the oscilloscope will capture continuously."""

    @abstractmethod
    def SetTrigger(self, external):
        ...

    @abstractmethod
    def SetAveraging(self, averages:int):
        ...

    @abstractmethod
    def getVertRange_V(self, channel, volts):
        ...

    @abstractmethod
    def setVertRange_V(self, channel, volts):
        ...

    @abstractmethod
    def getVertOffset(self, channel):
        ...

    @abstractmethod
    def setVertOffset_V(self, channel, offset):
        ...

    @abstractmethod
    def setHorzRange_sec(self, seconds):
        ...

    @abstractmethod
    def getHorzOffset_sec(self):
        ...

    @abstractmethod
    def setHorzOffset_sec(self, offset):
        ...

    '''Autoscales the oscilloscope's voltage range to fit the waveform'''

    @abstractmethod
    def autoScale(self):
        ...

    '''Captures from the specified channel and returns a list of times and a list of voltages of equal length'''

    @abstractmethod
    def capture(self, channel: int) -> Tuple[List[float], List[float]]:
        ...
