import time as t
from abc import abstractmethod

from PyQt5.QtCore import *

from Hardware.Abstract.abstract_motor_controller import AbstractMotorController

"""
    A class providing a crude imitation of the functionality of motor controller hardware classes.
"""


class SimulatedMotorController(AbstractMotorController):
    def __init__(self, config: dict, device_key="VIX_Motors", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.fields_setup()

    def go_home_1d(self, axis):
        if axis == "R":
            self.coords_mm[1] = -90
        elif axis == "X":
            self.coords_mm[0] = 273
        self.get_position()
        self.ready_signal.emit()

    def fields_setup(self):
        self.ax_letters = self.config[self.device_key]["axes"]
        num_axes = len(self.ax_letters)
        for i in range(num_axes):
            self.coords_mm.append(0)
        self.reverse_ray = self.config[self.device_key]["reverse_ray"]
        self.movement_mode = self.config[self.device_key]["movement_mode"]
        self.ax_letters = self.config[self.device_key]["axes"]
        self.calibrate_ray_steps_per = self.config[self.device_key]["calibrate_ray"]
        self.rotational_ray = self.config[self.device_key]["rotational_ray"]
        self.speeds_ray = self.config[self.device_key]["speeds_ray"]
        self.increment_ray = self.config[self.device_key]["increment_ray"]
        self.timeout_s = self.config[self.device_key]["timeout_s"]
        self.time_limit_s = self.config[self.device_key]["time_limit_s"]
        self.on_by_default = self.config[self.device_key]["on_by_default"]
        self.port = self.config[self.device_key]["port"]

    """Setup all axes according to a dictionary of settings. R is configured according to rotational settings."""

    @pyqtSlot(dict)
    def setup(self, settings):
        t.sleep(0.1)
        self.ready_signal.emit()

    """Setup an axis according to a dictionary of settings. R is configured according to rotational settings."""

    def setup_1d(self, axis, settings):
        pass

    def command(self, command):
        pass

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def check_connected(self):
        return self.connected, ""

    def begin_motion(self, axis=None, direction=None, feedback=True):
        axis_index = self.ax_letters.index(axis)
        current_coordinate_mm = self.coords_mm[axis_index]

        if direction < 0:
            go_to_coord_mm = int((current_coordinate_mm - abs(self.increment_ray[axis_index])))
        else:
            go_to_coord_mm = int((current_coordinate_mm + abs(self.increment_ray[axis_index])))

        self.go_to_position([axis], [go_to_coord_mm])

    @abstractmethod
    def stop_motion(self):
        self.moving_signal.emit(False)

    @abstractmethod
    def set_origin(self, origin_mm: list):
        origin_steps = list()

        for i in range(len(self.ax_letters)):
            origin_steps[i] = -1 * origin_mm[i] * self.calibrate_ray_steps_per + float(self.coords_mm[i])
            if self.reverse_ray[i]:
                origin_steps[i] = origin_steps * -1

        self.get_position()

    @abstractmethod
    def set_origin_here(self):
        self.coords_mm = [0, 0]
        self.get_position()

    @abstractmethod
    def set_origin_here_1d(self, axis):
        self.coords_mm[self.ax_letters.index(axis)] = 0
        self.get_position()

    @abstractmethod
    def go_home(self):
        self.coords_mm[1] = -90
        self.coords_mm[0] = 273
        self.get_position()

    @pyqtSlot(list, list)
    def go_to_position(self, axes: list, coords_mm: list) -> bool:
        for i in range(len(axes)):
            self.coords_mm[self.ax_letters.index(axes[i])] = coords_mm[i]

        # Used for simulating delay
        # t.sleep(.2)

        self.get_position()

        self.ready_signal.emit()
        return True

    @abstractmethod
    def is_moving(self):
        return self.moving

    @abstractmethod
    def get_position(self, mutex_locked=False):
        self.x_pos_mm_signal.emit(self.coords_mm[self.ax_letters.index("X")])
        self.r_pos_mm_signal.emit(self.coords_mm[self.ax_letters.index("R")])

    def wrap_up(self):
        self.disconnect_hardware()

    def get_serial_number(self) -> str:
        return '"Simulated"'

    def wrap_up(self):
        self.stop_motion()
        self.disconnect_hardware()
