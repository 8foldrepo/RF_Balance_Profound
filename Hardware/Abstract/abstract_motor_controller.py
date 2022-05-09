from abc import abstractmethod
from typing import List

from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractMotorController(AbstractDevice):
    """Defines an interface with key functionality for a motor controller"""

    # These lists will all be the same length when populated from the config file
    coords_mm = list()
    home_coords = list()
    reverse_ray = List[bool]
    ax_letters = List[str]
    calibrate_ray_steps_per = List[float]
    rotational_ray = List[bool]
    speeds_ray = List[float]
    increment_ray = List[float]

    movement_mode = List[str]
    timeout_s = List[float]
    time_limit_s = List[float]
    on_by_default = List[bool]
    port = List[str]

    moving = False

    # Signals
    x_pos_mm_signal = pyqtSignal(float)
    y_pos_signal = pyqtSignal(float)
    r_pos_mm_signal = pyqtSignal(float)
    z_pos_signal = pyqtSignal(float)

    moving_signal = pyqtSignal(bool)
    connected_signal = pyqtSignal(bool)
    ready_signal = pyqtSignal()

    def __init__(self, config: dict, device_key="VIX_Motors", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.fields_setup()

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

    @abstractmethod
    @pyqtSlot(list, list)
    def go_to_position(self, axes: List[str], coords_mm: List[float]) -> bool:
        """
        # Tells a list of axis letters ('X' , 'Y' , 'Z' , or 'R') to go to corresponding list of coordinates in deg or mm
        """
        ...

    @abstractmethod
    @pyqtSlot()
    def set_origin_here(self):
        """Sets the current position to zero for all axes"""

        ...

    @abstractmethod
    @pyqtSlot()
    def set_origin(self, origin_mm: List[float]):
        """Sets the origin to a specified list of coordinates. length must equal the length of self.ax_letters"""

        ...

    @abstractmethod
    def set_origin_1d(self, axis: str, coord_mm: float, get_position=True):
        """Sets the origin of a specified axis to a specified coordinate"""

        ...

    @abstractmethod
    @pyqtSlot(dict)
    def setup(self, settings):
        """Setup all axes according to a dictionary of settings. R is configured according to rotational settings."""

        ...

    @abstractmethod
    @pyqtSlot()
    def stop_motion(self):
        ...

    @abstractmethod
    @pyqtSlot()
    def go_home(self):
        ...

    @abstractmethod
    @pyqtSlot(str)
    def go_home_1d(self, axis: str):
        ...

    @abstractmethod
    @pyqtSlot(str)
    def stop_motion_1d(self, axis: str):
        ...

    @abstractmethod
    def is_moving(self) -> bool:
        ...

    @pyqtSlot()
    @pyqtSlot(str, int)
    def begin_motion(self, axis: str, direction: int):
        """Axis is a letter (X,Y,Z, or R). The sign of the int specifies the positive or negative direction"""

        ...

    @abstractmethod
    @pyqtSlot()
    def stop_motion(self):
        """Stops the motion of all axes, updates the moving variable and emits the moving signal"""

        ...

    @abstractmethod
    @pyqtSlot()
    def get_position(self):
        """Tell the motor controller to update its coords_mm variable and emit its current position as a signal"""

        ...

    def get_ax_number(self, axis):
        """return the motor controller driver number of the axis with the specified letter"""

        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number
