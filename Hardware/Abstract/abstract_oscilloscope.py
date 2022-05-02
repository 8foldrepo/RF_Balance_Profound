from abc import abstractmethod
from typing import Tuple, List

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractOscilloscope(AbstractDevice):
    """Defines key functionalities for oscilloscopes"""

    range_mv: float
    channel: int
    averages: int
    capture_period_ns: int
    signal_frequency_MHz: float
    signal_period_ns: float
    cycles: int
    delay_cycles: float
    captures: int

    def __init__(self, device_key="Keysight_Oscilloscope", config=None, parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)

    @abstractmethod
    def reset(self):
        ...

    @abstractmethod
    def set_to_defaults(self):
        ...

    @abstractmethod
    def setup(
        self,
        channel: int,
        range_s: float,
        offset_s: float,
        autorange_v: float,
        range_v: float,
        ext_trigger: bool,
        average_count: int,
    ):
        ...

    @abstractmethod
    def SetTrigger(self, external):
        """Sets whether or not to capture when triggered. If false the oscilloscope will capture continuously."""

        ...

    @abstractmethod
    def SetAveraging(self, averages: int):
        ...

    @abstractmethod
    def getVertRange_V(self, channel: int, volts: float):
        ...

    @abstractmethod
    def setVertRange_V(self, channel: int, volts: float):
        ...

    @abstractmethod
    def getHorzScale_V(self):
        ...

    @abstractmethod
    def setHorzScale_sec(self, seconds: float):
        ...

    @abstractmethod
    def getVertScale_V(self, channel: int):
        ...

    @abstractmethod
    def setVertScale_V(self, volts_per_div: float, channel: int):
        ...

    @abstractmethod
    def getVertOffset(self, channel: int):
        ...

    @abstractmethod
    def setVertOffset_V(self, channel: int, offset: float):
        ...

    @abstractmethod
    def setHorzRange_sec(self, seconds: float):
        ...

    @abstractmethod
    def getHorzOffset_sec(self):
        ...

    @abstractmethod
    def setHorzOffset_sec(self, offset: float):
        ...

    @abstractmethod
    def autoScale(self):
        """Autoscales the oscilloscope's voltage range to fit the waveform"""

        ...

    @abstractmethod
    def capture(self, channel: int) -> Tuple[List[float], List[float]]:
        """Captures from the specified channel and returns a list of times and a list of voltages of equal length"""

        ...
