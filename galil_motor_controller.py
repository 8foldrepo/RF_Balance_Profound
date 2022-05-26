import random
from typing import List

import numpy as np
from PyQt5.QtCore import pyqtSlot, QMutex
from PyQt5.QtWidgets import QApplication as QApp
from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
import time as t
import gclib
from Utilities.useful_methods import create_comma_string


class GalilMotorController(AbstractMotorController):
    """Provides an interface with key functionality for a galil motor controller"""

    # Note: see the abstract_motor_controller class for all inherited signals and attributes
    galil_ax_letters = list()

    def __init__(self, config: dict, lock: QMutex, device_key="Galil_Motors", parent=None):
        super().__init__(parent=parent, config=config, lock=lock, device_key=device_key)
        self.app = QApp.instance()
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
        self.command("ST")
        self.command("MO")
        self.handle.GClose()
        self.log("Connection terminated")
        self.connected = False
        self.connected_signal.emit(False)

    def check_connected(self):
        return self.connected

    def connect_hardware(self):
        feedback = ""

        port_list = self.handle.GAddresses()
        feedback = feedback + ("pre-connection handle status: {0}".format(self.handle)) + '\n'
        self.connected = False

        for port in port_list.keys():
            feedback = feedback + ("port: {0} , handle status: {1}".format(port, self.handle)) + '\n'
            try:
                self.handle.GOpen(f"{self.config[self.device_key]['ip_address']} --direct -s ALL")
                feedback = feedback + self.handle.GInfo() + '\n'
                self.connected = True
            except gclib.GclibError as e:
                feedback = feedback + ("Something went wrong: {0}".format(e)) + '\n'

            if self.connected:
                break

        feedback = feedback + f"post connection handle status: {self.handle}" + '\n'

        if not self.connected:
            self.log(level="error", message=feedback)
        else:
            self.setup_axes()
            # todo: call self.setup

        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    @pyqtSlot(dict)
    def setup(self, settings):
        """Setup all axes according to a dictionary of settings. R is configured according to rotational settings."""

        ...

    # todo: merge into setup
    def setup_axes(self):
        # Setup
        try:
            self.command("GR 0,0,0,0")
            self.command("GM 0,0,0,0")

            # self.command('PF 7')
            self.command("ST")
            self.command(
                f"SP {create_comma_string(self.ax_letters, self.speeds_ray, self.ax_letters)}"
            )  # yaml file value

            self.command("AC 1000000,1000000,1000000,1000000")
            self.command("DC 1000000,1000000,1000000,1000000")
            # self.set_origin()
            self.get_position()
            self.connected = True
        except gclib.GclibError as e:
            self.log(level='error', message=f"Connection error: {self.check_user_fault()}")
            self.connected = False

    # todo: test
    @pyqtSlot(list, list)
    def go_to_position(self, axes: List[str], coords_mm: List[float],
                       mutex_locked: bool = False, enable_ui: bool = True) -> bool:
        """
        # Tells a list of axis letters ('X' , 'Y' , 'Z' , or 'R') to go to corresponding list of coordinates in deg or mm
        """

        # check edge cases
        if not self.connected:
            self.log(level='error', message='Go to position failed, Galil not connected')
            if enable_ui:
                self.ready_signal.emit()
            return False

        if not len(axes) == len(coords_mm):
            self.log(level='error', message="Go to position failed axes length does not match coordinates length")
            if enable_ui:
                self.ready_signal.emit()
            return False

        if sum(coords_mm) > 1000:
            self.log(level='error', message=
            "Coordinates entered for the motors are too large. Double check in the code that they are given in mm"
                     )
            if enable_ui:
                self.ready_signal.emit()
            return False

        success = True

        galil_ax_letters_for_move = list()
        coords_steps = list()

        # Enforce pre-move conditions
        self.command("ST")
        self.command("SH")

        for i in range(len(axes)):
            if axes[i].upper() in self.ax_letters:
                ax_index = self.ax_letters.index(axes[i].upper())
                galil_ax_letter = self.galil_ax_letters[ax_index]
            else:
                continue

            galil_ax_letters_for_move.append(galil_ax_letter)
            target_coordinate_mm = float(coords_mm[i])
            target_coord_steps = self.__position_to_steps(ax_index, target_coordinate_mm)
            coords_steps.append(target_coord_steps)

        pa_command_str = f"PA {create_comma_string(axes, coords_steps, self.ax_letters)}"

        try:
            # Issue position absolute command
            self.command(pa_command_str)

            # Issue begin motion command
            bg_command_str = f"BG {''.join(galil_ax_letters_for_move)}"
            self.command(bg_command_str)
            success = self.wait_for_motion_to_complete()

        except gclib.GclibError as e:
            success = False
            stop_code = self.check_user_fault()
            if stop_code is not None:
                self.log(level='error', message=f"error in go_to_position: {stop_code}")
            else:
                self.log(level='error', message=f"error in go_to_position: {e}")
        finally:
            self.get_position()

        # Send ready signal to enable UI
        if enable_ui:
            self.ready_signal.emit()
        return success

    def wait_for_motion_to_complete(self):

        start_time = t.time()

        success = False

        while t.time() - start_time < self.config[self.device_key]["move_timeout_s"]:
            try:
                self.get_position()

                current_pos_str = self.command('RP')
                # this command is intended to have no effect, by telling the motors to go to the current position.
                # It will raise an exception if the motors are moving. If there is no exception the motion is complete
                self.command(f"PA {current_pos_str}")
                self.command(f"BG {''.join(self.galil_ax_letters)}")
                success = True
                break

            except gclib.GclibError as e:
                code = self.check_user_fault()
                # This exception is expected to occur repeatedly until the motion is complete. This is not a bug.
                if not code == '7 Command not valid while running':
                    # If the error code is different, log it as an error and return False
                    self.log(level='error', message=f"error in go to position: {code}")
                    return False

        if not success:
            self.log(level='error', message='movement timed out')
            self.stop_motion()

        return success

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

    # todo: test
    def set_origin_1d(self, axis, coord_mm, get_position=True):
        if coord_mm > 1000:
            self.log(level='error', message='Coordinate entered is too large, double check that it is given in mm')
            return False

        try:
            axis_index = self.ax_letters.index(axis.upper())
        except ValueError:
            self.log(level='error', message='Axis not found in set_origin_1d')
            return False

        coord_steps = self.__position_to_steps(axis_index, coord_mm)
        home_coordinate = int(coord_steps)

        # issue set home command
        dp_command_str = f'DP {create_comma_string([axis], [home_coordinate], self.ax_letters)}'
        try:
            self.command(dp_command_str)
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
        try:
            self.command("ST")
            self.moving = False
        except gclib.GclibError as e:
            stop_code = self.check_user_fault()
            if stop_code is not None:
                print(f"error in stop_motion: {stop_code}")
            self.moving = True
        finally:
            self.get_position()
        self.moving_signal.emit(self.moving)

    def __get_galil_ax_letter(self, axis: str) -> str:
        galil_ax_letter = ''

        try:
            galil_ax_letter = self.galil_ax_letters[self.ax_letters.index(axis)]
        except ValueError:
            if axis.upper() != 'All'.upper():
                self.log(level='error', message='invalid axis letter in stop stop_motion_1d')
                raise Exception

        return galil_ax_letter

    @pyqtSlot(str)
    def stop_motion_1d(self, axis: str):
        galil_ax_letter = self.__get_galil_ax_letter(axis)

        try:
            self.command(f"ST {galil_ax_letter}")
            self.moving = False
        except gclib.GclibError as e:
            stop_code = self.check_user_fault()
            if stop_code is not None:
                print(f"error in stop_motion: {stop_code}")
            self.moving = True
        finally:
            self.get_position()
        self.moving_signal.emit(self.moving)

    @pyqtSlot()
    def go_home(self, enable_ui:bool = True) -> bool:
        # enforce premove conditions
        self.command("ST")
        self.command("SH ABCD")

        # Theta prehome move
        self.go_to_position(['R'], [self.config["WTF_PositionParameters"]["ThetaPreHomeMove"]], enable_ui=False)

        self.command("ST")
        self.command("SH ABCD")
        try:
            self.command("HM")
            self.command("BG")
        except gclib.GclibError as e:
            self.log(level='error', message=self.check_user_fault())

        success = self.wait_for_motion_to_complete()

        success_2 = self.go_to_position(['R'], [-90], enable_ui=False)

        if enable_ui:
            self.ready_signal.emit()

        return success and success_2

    @pyqtSlot(str)
    def go_home_1d(self, axis: str, enable_ui:bool = True) -> bool:
        # enforce premove conditions
        self.command("ST")
        self.command("SH ABCD")

        if axis == 'R' or axis == 'Theta':
            # Theta prehome move
            self.go_to_position(['R'], [self.config["WTF_PositionParameters"]["ThetaPreHomeMove"]], enable_ui=False)

            self.command("ST")
            self.command("SH ABCD")
        try:
            self.command(f"HM {self.__get_galil_ax_letter(axis)}")
            self.command(f"BG {self.__get_galil_ax_letter(axis)}")
        except gclib.GclibError as e:
            self.log(level='error', message=self.check_user_fault())

        success = self.wait_for_motion_to_complete()

        if axis == 'R' or axis == 'Theta':
            success = success and self.go_to_position(['R'], [-90], enable_ui=False)

        if enable_ui:
            self.ready_signal.emit()
        return success

    @pyqtSlot()
    @pyqtSlot(str, int)
    def begin_motion(self, axis: str, direction: int):
        """Axis is a letter (X,Y,Z, or R). The sign of the int specifies the positive or negative direction"""
        axis_index = self.ax_letters.index(axis)

        current_coordinate_mm = self.coords_mm[axis_index]

        if direction < 0:
            go_to_coord_mm = int((current_coordinate_mm - abs(self.increment_ray[axis_index])))
        else:
            go_to_coord_mm = int((current_coordinate_mm + abs(self.increment_ray[axis_index])))

        self.go_to_position([axis], [go_to_coord_mm], enable_ui=True)

    @pyqtSlot()
    def stop_motion(self):
        """Stops the motion of all axes, updates the moving variable and emits the moving signal"""
        self.log("Stopping motion")
        try:
            self.moving = not self.stop_motion_1d(axis="All")
        except gclib.GclibError as e:
            if "connection to hardware not established" in str(e):
                self.log("Could not stop motion, connection to hardware not established. If the system is moving, "
                         "press the emergency stop or turn off power manually")

    @pyqtSlot()
    def get_position(self, mutex_locked: bool = False):
        """Tell the motor controller to update its coords_mm variable and emit its current position as a signal"""
        moving_ray = [False, False]
        moving_margin_ray = [0.001, 0.001]

        x_pos = self.__steps_to_position(0, float(self.command('RP A')))
        if abs(x_pos - self.coords_mm[0]) > moving_margin_ray[0]:
            moving_ray[0] = True
        self.coords_mm[0] = x_pos
        self.x_pos_mm_signal.emit(round(x_pos, 2))

        r_pos = self.__steps_to_position(1, float(self.command('RP B')))
        if abs(r_pos - self.coords_mm[1]) > moving_margin_ray[1]:
            moving_ray[1] = True
        self.coords_mm[1] = r_pos
        self.r_pos_mm_signal.emit(round(r_pos, 2))

        if True in moving_ray:
            self.moving = True
        else:
            self.moving = False
        self.moving_signal.emit(self.moving)
        if self.app is not None:
            self.app.processEvents()

    def __get_ax_number(self, axis):
        """return the motor controller driver number of the axis with the specified letter"""

        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number

    def __position_to_steps(self, axis_index: int, position_deg_or_mm: float):
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

    def __steps_to_position(self, axis_index, position_steps):
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

    def check_user_fault(self) -> str:
        try:
            error = self.command("TC 1")
            return error
        except gclib.GclibError as e:
            return str(e)

    def command(self, command):
        output = self.handle.GCommand(command)
        t.sleep(.01)
        return output


if __name__ == '__main__':
    galil = GalilMotorController(config=None, lock=None)
    galil.connect_hardware()

    galil.handle.GCommand("DP 0,0,0,0")

    i = 1
    while True:
        i = i + 1

        distance_target = random.choice([-5000, 5000])
        galil.handle.GCommand("ST")

        t.sleep(.01)

        try:
            galil.handle.GCommand(f"PA {distance_target}")
        except:
            print(galil.check_user_fault())

        galil.handle.GCommand("BG A")

        t.sleep(.01)

        #wait_for_motion_to_complete()

        t.sleep(.01)

        print(galil.handle.GCommand("RP"))
        t.sleep(.01)
