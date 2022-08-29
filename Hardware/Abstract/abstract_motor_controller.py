from abc import abstractmethod
from typing import List

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QMutex

from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractMotorController(AbstractDevice):
    """Defines an interface with key functionality for a motor controller"""

    # These lists will all be the same length when populated from the config file
    coords_mm = list()
    home_coords = list()
    reverse_ray: List[bool]
    ax_letters: List[str]
    calibrate_ray_steps_per: List[float]
    rotational_ray: List[bool]
    speeds_ray: List[float]
    increment_ray: List[float]

    movement_mode: List[str]
    timeout_s: List[float]
    time_limit_s: float
    on_by_default: List[bool]
    port: str

    moving = False

    # Signals
    x_pos_mm_signal = pyqtSignal(float)
    y_pos_signal = pyqtSignal(float)
    r_pos_mm_signal = pyqtSignal(float)
    z_pos_signal = pyqtSignal(float)

    moving_signal = pyqtSignal(bool)
    connected_signal = pyqtSignal(bool)
    ready_signal = pyqtSignal()

    # The lock parameter is a provided as a way to prevent the motor class to have multiple conflicting commands at once
    def __init__(self, config: dict, lock: QMutex, device_key="VIX_Motors", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.gearing_ray = None
        self.fields_setup()

    def fields_setup(self) -> None:
        """
        Initializes all class variables, all of which come from the config file
        """
        self.ax_letters = self.config[self.device_key]["axes"]
        num_axes = len(self.ax_letters)
        for i in range(num_axes):
            self.coords_mm.append(0)
        self.reverse_ray = self.config[self.device_key]["reverse_ray"]
        self.movement_mode = self.config[self.device_key]["movement_mode"]
        self.ax_letters = self.config[self.device_key]["axes"]
        self.calibrate_ray_steps_per = self.config[self.device_key]["calibrate_ray"]
        self.rotational_ray = self.config[self.device_key]["rotational_ray"]
        self.gearing_ray = self.config[self.device_key]["gearing_ray"]
        self.speeds_ray = self.config[self.device_key]["speeds_ray"]
        self.increment_ray = self.config[self.device_key]["increment_ray"]
        self.timeout_s = self.config[self.device_key]["timeout_s"]
        self.time_limit_s = self.config[self.device_key]["time_limit_s"]
        self.on_by_default = self.config[self.device_key]["on_by_default"]

    @abstractmethod
    @pyqtSlot(list, list)
    def go_to_position(self, axes: List[str], coordinates_mm: List[float], mutex_locked: bool,
                       enable_ui: bool = True) -> bool:
        """
        Tells a list of axis letters ('X' , 'Y' , 'Z' , or 'R') to go to corresponding list of coordinates in deg or mm

        :param axes: list of axes to be moved
        :param coordinates_mm: where the motor for the specific axis should be moved to
        :param mutex_locked: unused variable; default to false, presumably to prevent race condition with moving
        :param enable_ui: Enable ui to control motors unless the manager is running a script
        :return: whether movement finished successfully
        """
        # Mutex locked informs this class if the class that called this method has already locked the mutex
        ...

    @abstractmethod
    @pyqtSlot()
    def set_origin_here(self) -> None:
        """Sets the current position to zero for all axes"""

        ...

    @abstractmethod
    @pyqtSlot()
    def set_origin(self, origin_mm: List[float]) -> None:
        """
        Abstract: Sets the origin to a specified list of coordinates. length must equal the length of self.ax_letters

        --------------------------

        Galil: Given a list of origin points in mm that matches the numbers of axis: tell the galil
        motor controller where the home position is for the respective axes
        """

        ...

    @abstractmethod
    def set_origin_1d(self, axis: str, coord_mm: float, get_position: bool = True):
        """
        Abstract: Sets the origin of a specified axis to a specified coordinate

        --------------------------

        Galil: Helper method for the 'set_origin' method, actually creates the command string given
        the passed values and issues the command to the hardware, will return position if flag
        set to true and handles various error cases

        :param axis: the axis to set the origin of
        :param coord_mm: where the origin should be set to
        :param get_position:
            true if you want the class to update it's internal coord_mm variable and emit it as a
            signal, false if otherwise (true by default)
        :return: whether setting origin operation was successful
        """

        ...

    @abstractmethod
    @pyqtSlot(dict)
    def setup(self, settings: dict):
        """
        Setup all axes according to a dictionary of settings. R is configured according to rotational settings.

        :param settings: dictionary of settings to apply to the class and motors
        """

        ...

    @abstractmethod
    @pyqtSlot()
    def stop_motion(self):
        """
        Sends the stop command to the motor control hardware to stop **all** motor movement.
        Also **emits a signal** of whether the motor is moving
        """
        ...

    @abstractmethod
    @pyqtSlot()
    def go_home(self, enable_ui: bool = True) -> bool:
        """
        Abstract: Commands all motors to begin motion in the negative direction until they hit the edge of a limit
        switch, then to reverse direction and continue moving until the positive edge of the switch is reached

        ___________________________________________________

        Galil: Moves the motors to the internally stored home position for all axis.
        Has an optional flag to have the user see a warning prompt before motor homing.

        :param enable_ui:
            whether to turn on various buttons in main window and its tabs after operation if script
            isn't running
        :returns: boolean representing successful homing.
        """
        ...

    @abstractmethod
    @pyqtSlot(str)
    def go_home_1d(self, axis: str, enable_ui: bool = True, theta_pre_home_move: bool = True) -> bool:
        """
        Commands one axis to begin motion in the negative direction until they hit the edge of a limit switch,
        then to reverse direction and continue moving until the positive edge of the switch is reached

        -------------------------------

        Galil: Does the same as the go_home method except is only pertained to the passed axis.

        :param axis: the axis the user wishes to home
        :param enable_ui: re-enables various inputs of the main window if a script isn't running
        :param theta_pre_home_move: Causes the rotational axis to move a fixed amount before homing
        :return: whether homing operation completed successfully
        """
        ...

    @abstractmethod
    @pyqtSlot(str)
    def stop_motion_1d(self, axis: str):
        """
        Tells the motion controller to **stop** a **specific** axis motor, `handles errors`

        :param axis: axis to stop the motion of
        """
        ...

    @pyqtSlot()
    @pyqtSlot(str, int)
    def begin_motion(self, axis: str, direction: int):
        """
        begin moving a specific axis in a specified direction

        :param axis: is a letter (X,Y,Z, or R)
        :param direction: the sign of the int specifies the positive or negative direction
        """

        ...

    @abstractmethod
    @pyqtSlot()
    def stop_motion(self):
        """Stops the motion of all axes, updates the moving variable and emits the moving signal"""

        ...

    @abstractmethod
    @pyqtSlot()
    def get_position(self, mutex_locked: bool = False):
        """
        Tell the motor controller to update its coordinates_mm variable and emit its current position as a signal

        :param mutex_locked: unused variable, presumably used to prevent race condition for the parker controller
        """

        ...

    def __get_ax_number(self, axis: str) -> int:
        """return the motor controller driver number of the axis with the specified letter"""

        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number
