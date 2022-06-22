"""
This class aims to emulate the functionality of the real MT Balance, both real and
simulated are based off the abstract_balance template from the /Hardware/Abstract folder
"""
import random
import time as t
from typing import Tuple, Optional

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from Hardware.Abstract.abstract_balance import AbstractBalance
from Utilities.load_config import load_configuration


class SimulatedBalance(AbstractBalance):
    """
    Simulated balance has limited functionality and should only be used if the real hardware is not available
    """
    reading_signal = QtCore.pyqtSignal(float)
    connected_signal = QtCore.pyqtSignal(bool)
    timeout_s: int
    port: str

    def __init__(self, config: dict, device_key: str = "MT_Balance", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

        self.ser = None
        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    def fields_setup(self) -> None:
        """
        sets timeout_s and port attributes to whatever is defined for the balance in config file
        """
        self.timeout_s = self.config[self.device_key]["timeout_s"]
        self.port = self.config[self.device_key]["port"]

    def zero_balance_stable(self) -> None:
        """Zeroes the scale with the next stale weight reading"""
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if not self.connected:
            self.log(message="Device is not connected, cannot run zero_balance_stable method", level='warning')
            return
        self.log("Zeroing Balance, Please wait")

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            item = random.choice([b"ZA", b"I"])

            if item == b"Z A":
                self.log(level="info", message="Balance Zeroed")
                return
            else:
                if item == b"I":
                    self.log(level="error", message="Weight unstable or balance busy")
                    return
                elif item == b"+":
                    self.log(level="error", message="Balance overloaded")
                    return
                elif item == b"-":
                    self.log(level="error", message="Balance underloaded")
                    return
        self.log(level="error", message=f"{self.device_key} timed out")

    def zero_balance_instantly(self) -> None:
        """Zeroes the scale with the next stale weight reading"""
        self.log("Zeroing Balance")
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if not self.connected:
            self.log(message="Device is not connected, cannot run zero_balance_instantly()", level='warning')
            return
        self.log("Zeroing Balance, Please wait")

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            item = random.choice([b"Z S", b"Z D", b"Z I"])

            if item == b"Z S" or item == b"Z D":
                self.log(level="info", message="Balance Zeroed")
                return
            else:
                if item == b"I":
                    self.log(level="error", message="Weight unstable or balance busy")
                    return
                elif item == b"+":
                    self.log(level="error", message="Balance overloaded")
                    return
                elif item == b"-":
                    self.log(level="error", message="Balance underloaded")
                    return
        self.log(level="error", message=f"{self.device_key} timed out")

    def connect_hardware(self) -> Tuple[bool, str]:
        """
        sets connected flag to true and emits 'True' via connected_signal

        :return: new state of self.connected (True) and empty string (feedback in real hardware class)
        """
        self.connected = True
        self.ser = object
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self) -> None:
        """
        Sets connected flag to false and emits 'False' via connected_signal
        """
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self) -> Optional[float]:
        """
        returns immediate reading of weight (randomly generated for simulated class)

        :return: random float value
        """
        if self.config["Debugging"]["simulate_balance_error"]:
            return None

        t.sleep(0.02)
        return random.random()

    def reset(self) -> None:
        """logs a reset command, does nothing to class"""
        self.log(message="Reset", level='info')

    def get_stable_reading(self) -> float:
        """
        Get stable reading from balance (returns random value in simulated class)

        :return: random float value
        """
        self.log("Getting stable weight, please wait")
        return random.random()

    def get_serial_number(self) -> str:
        """
        Returns serial number as a string

        :return: Will return 'Simulated' always, should return real serial in actual hardware class
        """
        return '"Simulated"'

    def wrap_up(self) -> None:
        """
        Relay caller for self.disconnect_hardware()
        """
        self.disconnect_hardware()


if __name__ == "__main__":
    balance = SimulatedBalance(config=load_configuration())
    balance.connect_hardware()
    balance.reset()
    balance.zero_balance_instantly()
    input("press enter when weight is on scale")
    balance.get_reading()
    balance.get_stable_reading()
