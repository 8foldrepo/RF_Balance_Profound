from typing import Tuple

import nidaqmx
from PyQt5 import QtCore

from Hardware.Abstract.abstract_sensor import AbstractSensor


class NIThermocouple(AbstractSensor):
    reading_signal = QtCore.pyqtSignal(float)
    connected_signal = QtCore.pyqtSignal(bool)

    def __init__(self, config, parent=None, device_key="TempMon"):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.name = None
        self.connected = False
        self.fields_setup()

    def fields_setup(self):
        """
        Takes the name value from the default or local.yaml
        config file and set's the local name variable to that
        """
        self.name = self.config[self.device_key]["DeviceName"]

    def connect_hardware(self) -> Tuple[bool, str]:
        """This method uses the nidaqmx library to tell the thermocouple to connect to the computer
        via a digital channel. The method then sets the connected flag to true and emits the signal
        for the main window and manager. Handles error with log message."""
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_thrmcpl_chan(f"{self.name}/ai0")
            self.connected = True
        except Exception as e:
            self.log(level="error", message=f"Error connecting to thermocouple: {e}")
            self.connected = False

        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self) -> None:
        """
        Sets the connected flag to false and relays the boolean status to MainWindow
        which connects it to the manager's hardware thermocouple variable
        """
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self) -> None:
        """
        Ensures device is connected, then adds a channel from the thermocouple, takes a reading from
        the device's channel, and emits the signal to the main window which connects it to the manager's
        device variable.
        """
        if not self.connected:
            return

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_thrmcpl_chan(f"{self.name}/ai0")
            reading = task.read()

        self.reading_signal.emit(reading)
        return reading

    # todo: implement
    def get_serial_number(self) -> str:
        """Method retrieves serial number from device and returns it as a string value"""
        pass

    def wrap_up(self) -> None:
        """Calls the disconnect hardware method"""
        self.disconnect_hardware()

if __name__ == "__main__":
    therm = NIThermocouple(config=None)
    therm.connect_hardware()

    while True:
        print(therm.get_reading())
