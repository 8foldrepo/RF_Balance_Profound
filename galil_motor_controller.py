from typing import List
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
import time as t
import gclib
from Utilities.useful_methods import create_comma_string

class GalilMotorController(AbstractMotorController):
    """Provides an interface with key functionality for a galil motor controller"""

    galil_ax_letters = list()

    def __init__(self, config: dict, device_key="Galil_Motors", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.lock = lock
        self.handle = gclib.py()
        self.fields_setup()
        self.generate_galil_axes()

    def generate_galil_axes(self):
        """
        assigns axis letters corresponding to the galil's letters starting with capital A to the user facing axis letters.
        for example if self.ax_letters is ['X', 'R'] the corresponding self.galil_ax_letters will be ['A', 'B']
        """
        for i in range(len(self.ax_letters)):
            self.galil_ax_letters.append(chr(65 + i))

    def disconnect_hardware(self):
        self.handle.GCommand("ST")
        self.handle.GCommand("MO")
        self.handle.GClose()
        self.log("Connection terminated")
        self.connected = False
        self.connected_signal.emit(False)

    def check_connected(self):
        return self.connected

    def connect_hardware(self):
        feedback = ""

        port_list = self.handle.GAddresses()
        feedback = feedback + ("pre-connection handle status: {0}".format(self.handle)) +'\n'
        self.connected = False

        for port in port_list.keys():
            feedback = feedback + ("port: {0} , handle status: {1}".format(port, self.handle))  +'\n'
            try:
                self.handle.GOpen("192.168.42.100 --direct -s ALL")
                feedback = feedback + self.handle.GInfo() +'\n'
                self.connected = True
            except gclib.GclibError as e:
                feedback = feedback + ("Something went wrong: {0}".format(e)) +'\n'

            if self.connected:
                break

        feedback = feedback + f"post connection handle status: {self.handle}" + '\n'

        if not self.connected:
            self.log(level="error", message=feedback)
        else:
            self.setup_axes()
            #todo: call self.setup

        self.connected_signal.emit(self.connected)
        return self.connected, feedback


    @pyqtSlot(dict)
    def setup(self, settings):
        """Setup all axes according to a dictionary of settings. R is configured according to rotational settings."""

        ...

    #todo: merge into setup
    def setup_axes(self):
        # Setup
        try:
            self.handle.GCommand("GR 0,0,0,0")
            self.handle.GCommand("GM 0,0,0,0")

            # self.handle.GCommand('PF 7')
            self.handle.GCommand("ST")
            self.handle.GCommand(
                f"SP {self._x_calibrate}, {self._y_calibrate}, {self._z_calibrate}, {self._r_calibrate}"
            )  # yaml file value

            self.handle.GCommand("AC 1000000,1000000,1000000,1000000")
            self.handle.GCommand("DC 1000000,1000000,1000000,1000000")
            # self.set_origin()
            self.get_position()
            self.connected = True
        except gclib.GclibError as e:
            print(f"Connection error: {self.check_user_fault()}")
            self.connected = False



    #todo: test
    @pyqtSlot(list, list)
    def go_to_position(self, axes: List[str], coords_mm: List[float]) -> bool:
        """
        # Tells a list of axis letters ('X' , 'Y' , 'Z' , or 'R') to go to corresponding list of coordinates in deg or mm
        """

        #check edge cases
        if not self.connected:
            self.log(level='error',message='Go to position failed, Galil not connected')
            self.ready_signal.emit()
            return False

        if not len(axes) == len(coords_mm):
            self.log(level='error', message="Go to position failed axes length does not match coordinates length")
            self.ready_signal.emit()
            return False

        if coords_mm > 1000:
            self.log(level='error', message=
                "Coordinates entered for the motors are too large. Double check in the code that they are given in mm"
            )
            return

        galil_ax_letters = list()
        coords_steps = list()

        # Enforce pre-move conditions
        self.handle.GCommand("ST")
        self.handle.GCommand("SH ABCD")

        for i in range(len(axes)):
            if axes[i].upper() in self.ax_letters:
                ax_index = self.ax_letters.index(axes[i].upper())
                galil_ax_letter = galil_ax_letters[ax_index]
            else:
                continue

            galil_ax_letters.append(galil_ax_letter)
            target_coordinate_mm = float(coords_mm[i])
            target_coord_steps = self.position_to_steps(ax_index, target_coordinate_mm)
            coords_steps.append(target_coord_steps)

        #Issue position absolute command
        pa_command_str = f"PA {create_comma_string(axes, coords_steps, self.ax_letters)}"
        print(pa_command_str)
        #self.handle.GCommand(pa_command_str)

        #Issue begin motion command
        bg_command_str = f"BG {''.join(galil_ax_letters)}"
        print(bg_command_str)
        #self.handle.GCommand(bg_command_str)

        while self.moving:
            self.get_position()
            t.sleep(.1)

        # Wait for motion to be over
        # t.sleep(2)
        # Check position
        # self.get_position()
        # Send ready signal to enable UI
        self.ready_signal.emit()
        return True

    @pyqtSlot()
    def set_origin_here(self):
        for axis in self.ax_letters:
            self.set_origin_here_1d(axis=axis)

    @pyqtSlot()
    def set_origin_here_1d(self, axis):
        self.set_origin_1d(axis=axis, coord_mm=0)

    @pyqtSlot()
    def set_origin(self, origin_mm: list):
        if not len(origin_mm) == len(self.ax_letters):
            self.log(level='error', message='Error in set_origin, not enough coordinates provided')
            return

        for i in range(len(origin_mm)):
            self.set_origin_1d(axis=self.ax_letters[i], coord_mm=origin_mm[i], get_position=False)

        self.get_position()

    #todo: test
    def set_origin_1d(self, axis, coord_mm, get_position=True):
        try:
            axis_index = self.ax_letters.index(axis.upper())
        except ValueError:
            self.log(level='error', message='Axis not found in set_origin_1d')
            return False

        coord_steps = self.position_to_steps(axis_index, coord_mm)
        home_coordinate = int(coord_steps)

        self.command(f"{axis_number}W(PT,{home_coordinate})")

        #issue set origin command
        dp_command_str = f'DP {create_comma_string(axis, home_coordinate, self.ax_letters)}'
        try:
            self.handle.GCommand(dp_command_str)
            successful = True
        except gclib.GclibError as e:
            stop_code = self.check_user_fault()
            if stop_code is not None:
                self.log(level='error', message=f"error in set_origin: {stop_code}")
            else:
                self.log(level='error', message=f"error in set_origin: {e}")
            successful = False
        finally:
            if get_position:
                self.get_position()
        return successful

    @pyqtSlot()
    def stop_motion(self):
        ...

    @pyqtSlot()
    def go_home(self) -> bool:
        ...

    @pyqtSlot(str)
    def go_home_1d(self, axis: str) -> bool:
        ...

    @pyqtSlot(str)
    def stop_motion_1d(self, axis: str):
        ...

    def is_moving(self) -> bool:
        ...

    @pyqtSlot()
    @pyqtSlot(str, int)
    def begin_motion(self, axis: str, direction: int):
        """Axis is a letter (X,Y,Z, or R). The sign of the int specifies the positive or negative direction"""

        ...

    @pyqtSlot()
    def stop_motion(self):
        """Stops the motion of all axes, updates the moving variable and emits the moving signal"""

        ...

    @pyqtSlot()
    def get_position(self):
        """Tell the motor controller to update its coords_mm variable and emit its current position as a signal"""

        ...

    def __get_ax_number(self, axis):
        """return the motor controller driver number of the axis with the specified letter"""

        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number

    def position_to_steps(self, axis_index, position_deg_or_mm):
        """Converts the user-facing coordinate in mm or degrees to the coordinate in motor steps"""
        i = axis_index

        if self.ax_letters[i].upper() == "X":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_steps = position_deg_or_mm + self.config['WTF_PositionParameters']['XHomeCoord']
        elif self.ax_letters[i].upper() == "R":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_steps = position_deg_or_mm - self.config['WTF_PositionParameters']['ThetaHomeCoord']
        else:
            return

        position_steps = position_steps * self.calibrate_ray_steps_per[i] / self.gearing_ray[i]

        if self.reverse_ray[i]:
            position_steps = position_steps * -1

        return position_steps

    def steps_to_position(self, axis_index, position_steps):
        """Converts the coordinate in motor steps to the user-facing coordinate in mm or degrees"""
        i = axis_index
        position_deg_or_mm = position_steps / self.calibrate_ray_steps_per[i] * self.gearing_ray[i]

        if self.reverse_ray[i]:
            position_deg_or_mm = position_deg_or_mm * -1

        if self.ax_letters[i].upper() == "X":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_deg_or_mm = position_deg_or_mm - self.config['WTF_PositionParameters']['XHomeCoord']
            self.x_pos_mm_signal.emit(round(position_deg_or_mm, 2))
        elif self.ax_letters[i].upper() == "R":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_deg_or_mm = position_deg_or_mm + self.config['WTF_PositionParameters']['ThetaHomeCoord']
            self.r_pos_mm_signal.emit(round(position_deg_or_mm, 2))

        return position_deg_or_mm

    def check_user_fault(self):
        try:
            error = self.handle.GCommand("TC 1")
            return(error)
        except:
            return None


if __name__ == '__main__':
    galil = GalilMotorController(config=None)
    print(galil.galil_ax_letters)
    galil.go_to_position(['X','R'],[-263, 0])