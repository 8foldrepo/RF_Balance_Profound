from abc import abstractmethod, ABCMeta
from typing import Union

from Hardware.Abstract.abstract_sensor import AbstractSensor


class AbstractBalance(AbstractSensor):
    __metaclass__ = ABCMeta

    timeout_s: int
    port: str

    def __init__(self, config, device_key="MT_Balance", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    @abstractmethod
    def fields_setup(self) -> None:
        """Sets the timeout in seconds and port from the config data structure (not passed as an argument to this method)"""
        self.timeout_s = self.config[self.device_key]["timeout_s"]
        self.port = self.config[self.device_key]["port"]

    @abstractmethod
    def zero_balance_stable(self) -> None:
        """Zeroes the scale with the next stale weight reading"""
        ...

    @abstractmethod
    def zero_balance_instantly(self) -> None:
        """Zeroes the scale with the next stale weight reading"""
        ...

    @abstractmethod
    def get_stable_reading(self) -> None:
        """Waits until the weight reading on the scale is stable, function mechanics are already built-in"""
        ...

    @abstractmethod
    def get_serial_number(self) -> Union[str, None]:
        """Attempts to retrieve the serial number of the balance as a string"""
        ...
