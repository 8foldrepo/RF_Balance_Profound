from abc import abstractmethod
from typing import Tuple, List

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractOscilloscope(AbstractDevice):
    """Defines key functionalities for oscilloscopes"""
    range_s: float
    offset_s: float
    range_mV: float
    channel: int
    averages: int

    def __init__(self, device_key="Keysight_Oscilloscope", config=None, parent=None):
        super().__init__(device_key=device_key, config=config, parent=parent)
        self.min_time_of_flight: float = float('nan')
        self.max_time_of_flight: float = float('nan')

    @abstractmethod
    def reset(self) -> None:
        """sends the reset signal to the oscilloscope via calling the oscilloscope's "command" method"""
        ...

    @abstractmethod
    def set_to_defaults(self) -> None:
        """Sets the oscilloscope's window values to default values specified in the inherited class. Other values
        such as the average counts, time of flight, external trigger, and timeout are also set"""
        ...

    @abstractmethod
    def setup(self, channel: int, range_s: float, offset_s: float, autorange_v: float, range_v: float,
              ext_trigger: bool, average_count: int) -> None:
        """Method to initialize various aspects of the oscilloscope window, such as the horizontal/vertical scales,
        averaging value and trigger policy"""
        ...

    @abstractmethod
    def set_trigger(self, external: bool) -> None:
        """Sets whether to capture when triggered. If false the oscilloscope will capture continuously."""

        ...

    @abstractmethod
    def set_averaging(self, averages: int):
        """Takes multiple captures triggered by something (e.g. a function generator), and averages them together
        the "averages" parameter is the number of waveforms to average together, functionality is built into the
        oscilloscope"""
        ...

    @abstractmethod
    def get_vertical_range_V(self, channel: int) -> float:
        """Method to get the vertical range of the oscilloscope window in volts (float) when given channel (int)
        as a parameter"""
        ...

    @abstractmethod
    def set_vertical_range_V(self, channel: int, volts: float) -> None:
        """Method to set the vertical offset of the oscilloscope window in float volts"""
        ...

    @abstractmethod
    def get_horizontal_scale_sec(self) -> float:
        """method that returns the horizontal scale of the oscilloscope, return value is voltage as a float"""
        ...

    @abstractmethod
    def set_horizontal_scale_sec(self, seconds: float) -> None:
        """Method to set the horizontal scale of the oscilloscope window when given the seconds as a float parameter"""
        ...

    @abstractmethod
    def autoset_oscilloscope_timebase(self):
        """Automatically sets the horizontal scale and range of the oscilloscope with a predetermined procedure"""
        ...

    @abstractmethod
    def get_vertical_scale_V(self, channel: int) -> float:
        """
        Method to get the vertical scale of the oscilloscope window when given the channel number (int) as a parameter
        """
        ...

    @abstractmethod
    def set_vertical_scale_V(self, volts_per_div: float, channel: int):
        ...

    @abstractmethod
    def get_vertical_offset_V(self, channel: int) -> float:
        """Method to get the voltage float vertical offset of the oscilloscope window"""
        ...

    @abstractmethod
    def set_vertical_offset_V(self, channel: int, offset: float) -> None:
        """Method to set the vertical offset of the oscilloscope window in voltage units as a parameter for given
        channel parameter"""
        ...

    @abstractmethod
    def set_horizontal_range_sec(self, seconds: float) -> None:
        """Method that sets the horizontal range of the oscilloscope window when given seconds (float) as a parameter"""
        ...

    @abstractmethod
    def get_horizontal_offset_sec(self) -> float:
        """Method to get the horizontal offset of the oscilloscope window in seconds"""
        ...

    @abstractmethod
    def set_horizontal_offset_sec(self, offset: float) -> bool:
        """Method to set the horizontal offset of the oscilloscope window in seconds as a float parameter"""
        ...

    @abstractmethod
    def autoScale(self):
        """Auto-scales the oscilloscope's voltage range to fit the waveform"""

        ...

    @abstractmethod
    def capture(self, channel: int) -> Tuple[List[float], List[float]]:
        """Captures from the specified channel and returns a list of times and a list of voltages of equal length"""

        ...

    @abstractmethod
    def get_rms(self) -> float:
        """Retrieves the root mean squared value of what's current in the oscilloscope's window as a float"""
        ...

    @abstractmethod
    def get_horizontal_range_sec(self):
        ...
