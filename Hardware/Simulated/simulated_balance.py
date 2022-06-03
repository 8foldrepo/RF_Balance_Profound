import random
import time as t

from PyQt5.QtCore import pyqtSignal

from Hardware.Abstract.abstract_balance import AbstractBalance
from Utilities.load_config import load_configuration


class SimulatedBalance(AbstractBalance):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)
    timeout_s: int
    port: str

    def __init__(self, config, device_key="MT_Balance", parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)

        self.latest_weight = -1
        self.connected = False

        self.fields_setup()

    def fields_setup(self):
        self.timeout_s = self.config[self.device_key]["timeout_s"]
        self.port = self.config[self.device_key]["port"]

    def zero_balance_stable(self):
        """Zeroes the scale with the next stale weight reading"""
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if not self.connected:
            self.log("Device is not connected")
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

    def zero_balance_instantly(self):
        """Zeroes the scale with the next stale weight reading"""
        self.log("Zeroing Balance")
        # Command: I2 Inquiry of balance data.
        # Response: I2 A Balance data as "text_item".
        if not self.connected:
            self.log("Device is not connected")
            return
        self.log("Zeroing Balance, Please wait")

        start_time = t.time()
        while t.time() - start_time < self.timeout_s:
            item = random.choice([b"Z S", b"Z D", b"Z I"])

            if item == b"Z S" or b"Z D":
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

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        if self.config["Debugging"]["simulate_balance_error"]:
            return None

        t.sleep(0.02)
        return random.random()

    def reset(self):
        self.log("Reset")

    def get_stable_reading(self):
        self.log("Getting stable weight, please wait")
        return random.random()

    def get_serial_number(self) -> str:
        return '"Simulated"'

    def wrap_up(self):
        self.disconnect_hardware()


if __name__ == "__main__":
    balance = SimulatedBalance(config=load_configuration())
    balance.connect_hardware()
    balance.reset()
    balance.zero_balance_instantly()
    input("press enter when weight is on scale")
    balance.get_reading()
    balance.get_stable_reading()
