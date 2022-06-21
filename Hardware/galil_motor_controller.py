import time as t
from typing import List, Union, Tuple
import gclib
from PyQt5.QtCore import pyqtSlot, QMutex
from PyQt5.QtWidgets import QApplication as QApp

from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
from Utilities.useful_methods import create_comma_string, is_number


class GalilMotorController(AbstractMotorController):
    """Provides an interface with key functionality for a galil motor controller"""

    def get_serial_number(self) -> str:
        ...
        # todo stretch: implement

    def wrap_up(self):
        self.disconnect_hardware()

    # Note: see the abstract_motor_controller class for all inherited signals and attributes
    galil_ax_letters = list()

    def __init__(self, config: Union[dict, None], lock: Union[QMutex, None], device_key="Galil_Motors", parent=None):
        super().__init__(parent=parent, config=config, lock=lock, device_key=device_key)
        self.app = QApp.instance()
        self.handle = gclib.py()
        self.fields_setup()
        self.generate_galil_axes()

    def generate_galil_axes(self) -> None:
        """
        assigns axis letters corresponding to the galil's letters starting with capital
        A to the user facing axis letters. for example if self.ax_letters is ['X', 'R']
        the corresponding self.galil_ax_letters will be ['A', 'B']
        """
        for i in range(len(self.ax_letters)):
            self.galil_ax_letters.append(chr(65 + i))

    def disconnect_hardware(self) -> None:
        """
        Sends disconnect commands to galil motors and sets flags to reflect disconnection
        """
        self.command("ST")
        self.command("MO")
        self.get_position()
        self.get_position()
        self.handle.GClose()
        self.log("Connection terminated")
        self.connected = False
        self.connected_signal.emit(False)

    def check_connected(self) -> bool:
        """
        Returns whether a galil motor controller is connected. Also updates self.connected
        :return: true if connected, false otherwise
        """
        try:
            info = self.handle.GInfo()
            self.connected = True
            return True
        except:
            self.connected = False
            return False

    def connect_hardware(self) -> Tuple[bool, str]:
        """
        attempts to connect the galil motor controller via IP and ports

        :return: feedback of connection attempt and whether controller was successfully connected
        """
        feedback = ""

        port_list = self.handle.GAddresses()
        self.connected = False

        for _ in port_list.keys():
            try:
                self.handle.GOpen(f"{self.config[self.device_key]['ip_address']} --direct -s ALL")
                feedback = feedback + self.handle.GInfo() + '\n'
                self.connected = True
            except gclib.GclibError as e:
                feedback = "Connection to motor controller timed out. Make sure it is connected and do a power " \
                           "cycle: {0}".format(e)

            if self.connected:
                break

        feedback = feedback + f"post connection handle status: {self.handle}" + '\n'

        if not self.connected:
            self.log(level="error", message=feedback)
        else:
            # todo: populate with settings

            self.setup(settings=None)

        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    @pyqtSlot(dict)
    def setup(self, settings: Union[dict, None]) -> None:
        """
        Setup all axes according to a dictionary of settings. R is configured according to rotational settings.

        :param settings: dictionary of settings to apply to the class and motors
        """
        # Update settings according to the dict
        if settings is not None:
            self.increment_ray[0] = settings["lin_incr"]
            self.increment_ray[1] = settings["ang_incr"]
            self.speeds_ray[0] = settings["lin_speed"]
            self.speeds_ray[1] = settings["rot_speed"]
            self.calibrate_ray_steps_per[0] = settings["steps_per_mm"]
            self.calibrate_ray_steps_per[1] = settings["steps_per_deg"]
            self.gearing_ray[0] = settings["x_gearing"]
            self.gearing_ray[1] = settings["r_gearing"]

        # Ensure motors are connected, if not return
        self.check_connected()
        if not self.connected:
            self.connect_hardware()
            if not self.connected:
                self.ready_signal.emit()
                return

        # Turn Motors on
        self.handle.GCommand("SH")

        try:
            # Turn off gear ratio and gear mode
            self.command("GR 0,0,0,0")
            self.command("GM 0,0,0,0")

            # Set the number of decimal places preceding the decimal
            self.command('PF 7')
            # Attempt to stop motor's motion
            self.command("ST")

            # Convert speeds to number of counts per second and update them
            steps_per_second = [speed * cal for speed, cal in zip(self.speeds_ray, self.calibrate_ray_steps_per)]
            sp_command_str = f"SP {create_comma_string(self.ax_letters, steps_per_second, self.ax_letters)}"
            self.command(sp_command_str)

            self.command("DC 1000000,1000000,1000000,1000000")
            # self.set_origin()
            self.get_position()
            self.connected = True
        except gclib.GclibError:
            self.log(level='error', message=f"Connection error: {self.check_user_fault()}")
            self.connected = False
        self.ready_signal.emit()

    # todo: test
    @pyqtSlot(list, list)
    def go_to_position(self, axes: List[str], coordinates_mm: List[float],
                       mutex_locked: bool = False, enable_ui: bool = True) -> bool:
        """
        Tells a list of axis letters ('X' , 'Y' , 'Z' , or 'R') to go to corresponding list of coordinates in deg or mm

        :param axes: list of axes to be moved
        :param coordinates_mm: where the motor for the specific axis should be moved to
        :param mutex_locked: unused variable; default to false, presumably to prevent race condition with moving
        :param enable_ui: Enable ui to control motors unless the manager is running a script
        :return: whether movement finished successfully
        """

        # check edge cases
        if not self.connected:
            self.log(level='error', message='Go to position failed, Galil not connected')
            if enable_ui:
                self.ready_signal.emit()
            return False

        if len(axes) != len(coordinates_mm):
            self.log(level='error', message="Go to position failed axes length does not match coordinates length")
            if enable_ui:
                self.ready_signal.emit()
            return False

        if sum(coordinates_mm) > 100000:
            self.log(level='error', message="Coordinates entered for the motors are too large."
                                            " Double check in the code that they are given in mm")
            if enable_ui:
                self.ready_signal.emit()
            return False

        galil_ax_letters_for_move = list()
        coordinates_steps = list()

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
            target_coordinate_mm = float(coordinates_mm[i])
            target_coord_steps = int(self.position_to_steps(ax_index, target_coordinate_mm))
            coordinates_steps.append(target_coord_steps)

        pa_command_str = f"PA {create_comma_string(axes, coordinates_steps, self.ax_letters)}"

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

    def wait_for_motion_to_complete(self) -> bool:
        # todo: this method seems to return true even if only one axis makes it to the origin
        """
        Hangs program in while loop until either move command finishes or move timeout from config file is reached

        :return: whether the method/movement completed successfully
        """
        start_time = t.time()
        success = False
        while t.time() - start_time < self.config[self.device_key]["move_timeout_s"]:
            self.app.processEvents()
            self.get_position()
            try:
                stop_code = self.command("SC AB")

                stop_code_ray = stop_code.split(', ')
                zero_in_ray = False
                for code in stop_code_ray:
                    if code == '0':
                        zero_in_ray = True

                if not zero_in_ray:
                    success = True
                    break
            except gclib.GclibError as e:
                code = self.check_user_fault()
                self.log(level='error', message=f"error in wait_for_motion_to_complete: {code}")
                return False

        if not success:
            self.log(level='error', message='movement timed out')
            self.stop_motion()

        return success

    @pyqtSlot()
    def set_origin_here(self) -> None:
        """
        Sets origin for all axes to 0
        """
        for axis in self.ax_letters:
            self.set_origin_here_1d(axis=axis)

    @pyqtSlot()
    def set_origin_here_1d(self, axis: str) -> None:
        """
        relay method from set_origin_here to set_origin_1d, passing the coord_mm as 0 to latter method

        :param axis: the axis to set the origin of
        """
        self.set_origin_1d(axis=axis, coord_mm=0)

    @pyqtSlot()
    def set_origin(self, origin_mm: list):
        """
        Given a list of origin points in mm that matches the numbers of axis: tell the galil
        motor controller where the home position is for the respective axes
        """
        if len(origin_mm) != len(self.ax_letters):
            self.log(level='error', message='Error in set_origin, not enough coordinates provided')
            return

        for i in range(len(origin_mm)):
            self.set_origin_1d(axis=self.ax_letters[i], coord_mm=origin_mm[i], get_position=False)

        self.get_position()

    def set_origin_1d(self, axis, coord_mm, get_position=True):
        """
        Helper method for the 'set_origin' method, actually creates the command string given
        the passed values and issues the command to the hardware, will return position if flag
        set to true and handles various error cases

        :param axis: the axis to set the origin of
        :param coord_mm: where the origin should be set to
        :param get_position:
            true if you want the class to update it's internal coord_mm variable and emit it as a
            signal, false if otherwise (true by default)
        :return: whether setting origin operation was successful
        """
        if coord_mm > 1000:
            self.log(level='error', message='Coordinate entered is too large, double check that it is given in mm')
            return False

        try:
            axis_index = self.ax_letters.index(axis.upper())
        except ValueError:
            self.log(level='error', message='Axis not found in set_origin_1d')
            return False

        coord_steps = self.position_to_steps(axis_index, coord_mm)
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
    def stop_motion(self) -> None:
        """
        Sends the stop command to the Galil control hardware to stop **all** motor movement.
        Also **emits a signal** of whether the motor is moving
        """
        try:
            self.command("ST")
            self.moving = False
        except gclib.GclibError:
            stop_code = self.check_user_fault()
            if stop_code is not None:
                self.log(level='error', message=f"error in stop_motion, stop code: {stop_code}")
            self.moving = True
        finally:
            self.get_position()
        self.moving_signal.emit(self.moving)

    def __get_galil_ax_letter(self, axis: str) -> str:
        """
        Helper method to convert a given axis name in string format to the index
        position in the program's internal list of axes

        :param axis: the axis in ax_letters that needs to be converted to an axis from the galil_ax_letters list
        :returns: the correct axis string from the galil_ax_letters list
        """
        galil_ax_letter = ''

        try:
            galil_ax_letter = self.galil_ax_letters[self.ax_letters.index(axis)]
        except ValueError:
            if axis.upper() != 'All'.upper():
                self.log(level='error', message='invalid axis letter in stop stop_motion_1d')
                raise Exception

        return galil_ax_letter

    @pyqtSlot(str)
    def stop_motion_1d(self, axis: str) -> None:
        """
        Tells the motion controller to **stop** a **specific** axis motor, `handles errors`

        :param axis: axis to stop the motion of
        """
        galil_ax_letter = self.__get_galil_ax_letter(axis)

        try:
            self.command(f"ST {galil_ax_letter}")
            self.moving = False
        except gclib.GclibError:
            stop_code = self.check_user_fault()
            if stop_code is not None:
                self.log(level='error', message=f"error in stop_motion, stop code: {stop_code}")
            self.moving = True
        finally:
            self.get_position()
        self.moving_signal.emit(self.moving)

    @pyqtSlot()
    def go_home(self, enable_ui: bool = True) -> bool:
        """
        Moves the motors to the internally stored home position for all axis.
        Has an optional flag to have the user see a warning prompt before motor homing.

        :param enable_ui:
            whether to turn on various buttons in main window and its tabs after operation if script
            isn't running
        :returns: boolean representing successful homing.
        """
        # enforce pre-move conditions
        self.command("ST")  # INFO: stops motor movement
        self.command("SH AB")

        # Theta pre-home move
        self.go_to_position(['R'], [self.config["WTF_PositionParameters"]["ThetaPreHomeMove"]], enable_ui=False)

        self.command("ST")
        self.command("SH AB")
        try:
            self.command("HM")  # set up for homing command
            self.command("BG")  # begin command
        except gclib.GclibError:
            self.log(level='error', message=self.check_user_fault())

        motion_complete_success = self.wait_for_motion_to_complete()
        self.set_origin_1d('R', self.coords_mm[1] - (self.config['WTF_PositionParameters']['ThetaHomeCoord']+
                                                self.config['WTF_PositionParameters']['ThetaHomeEdgeOffset']))
        self.get_position()

        go_to_position_success = self.go_to_position(['R'], [self.config["WTF_PositionParameters"]['ThetaHomeCoord']], enable_ui=False)

        self.get_position()
        if enable_ui:
            self.ready_signal.emit()

        return motion_complete_success and go_to_position_success

    @pyqtSlot(str)
    def go_home_1d(self, axis: str, enable_ui: bool = True) -> bool:
        """
        Does the same as the go_home method except is only pertained to the passed axis.

        :param axis: the axis the user wishes to home
        :param enable_ui: re-enables various inputs of the main window if a script isn't running
        :return: whether homing operation completed successfully
        """
        # QUESTION: should this also support the x axis?
        # ANSWER: No, only theta requires a prehome move
        # enforce pre-move conditions
        self.command("ST")  # stop command
        self.command("SH AB")

        if axis == 'R' or axis == 'Theta':
            # Theta pre-home move
            self.go_to_position(['R'], [self.config["WTF_PositionParameters"]["ThetaPreHomeMove"]], enable_ui=False)

            self.command("ST")
            self.command("SH AB")
        try:
            self.command(f"HM {self.__get_galil_ax_letter(axis)}")
            self.command(f"BG {self.__get_galil_ax_letter(axis)}")
        except gclib.GclibError:
            self.log(level='error', message=self.check_user_fault())

        success = self.wait_for_motion_to_complete()

        if axis == 'R' or axis == 'Theta':
            self.set_origin_1d('R', self.coords_mm[1] - (self.config['WTF_PositionParameters']['ThetaHomeCoord'] +
                                                         self.config['WTF_PositionParameters']['ThetaHomeEdgeOffset']))
            self.get_position()
            success = success and self.go_to_position(['R'], [self.config["WTF_PositionParameters"]["ThetaHomeCoord"]], enable_ui=False)

        t.sleep(.1)
        self.get_position()

        if enable_ui:
            self.ready_signal.emit()
        return success

    @pyqtSlot()
    @pyqtSlot(str, int)
    def begin_motion(self, axis: str, direction: int) -> None:
        """
        begin moving a specific axis in a specfied direction

        :param axis: is a letter (X,Y,Z, or R)
        :param direction: the sign of the int specifies the positive or negative direction
        """
        axis_index = self.ax_letters.index(axis)

        current_coordinate_mm = self.coords_mm[axis_index]

        if direction < 0:
            go_to_coord_mm = float((current_coordinate_mm - abs(self.increment_ray[axis_index])))
        else:
            go_to_coord_mm = float((current_coordinate_mm + abs(self.increment_ray[axis_index])))

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

        x_pos_str = self.command('RP A')
        if is_number(x_pos_str):
            x_pos = self.steps_to_position(0, float())
        else:
            self.ready_signal.emit()
            return

        if abs(x_pos - self.coords_mm[0]) > moving_margin_ray[0]:
            moving_ray[0] = True
        self.coords_mm[0] = x_pos
        self.x_pos_mm_signal.emit(round(x_pos, 2))

        r_pos = self.steps_to_position(1, float(self.command('RP B')))
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
        # QUESTION: this method is never used, is it meant to be?
        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number

    def position_to_steps(self, axis_index: int, position_deg_or_mm: float):
        """Converts the user-facing coordinate in mm or degrees to the coordinate in motor steps"""
        i = axis_index

        if self.ax_letters[i].upper() == "X":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_steps = position_deg_or_mm + self.config['WTF_PositionParameters']['XHomeCoord']
        elif self.ax_letters[i].upper() == "R":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_steps = position_deg_or_mm - self.config['WTF_PositionParameters']['ThetaHomeCoord']-\
                             self.config['WTF_PositionParameters']['ThetaHomeEdgeOffset']

        else:
            return

        position_steps = position_steps * self.calibrate_ray_steps_per[i] / self.gearing_ray[i]

        if self.reverse_ray[i]:
            position_steps *= -1

        return position_steps

    def steps_to_position(self, axis_index: int, position_steps: float) -> float:
        """
        Converts the coordinate in motor steps to the user-facing coordinate in mm or degrees

        :param axis_index: the axis for which the user wants to convert steps to mm/deg; 0=X, 1=R
        :param position_steps: the position in steps
        :returns: position in mm/deg
        """
        i = axis_index
        position_deg_or_mm = position_steps / self.calibrate_ray_steps_per[i] * self.gearing_ray[i]

        if self.reverse_ray[i]:
            position_deg_or_mm *= -1

        if self.ax_letters[i].upper() == "X":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_deg_or_mm = position_deg_or_mm - self.config['WTF_PositionParameters']['XHomeCoord']
            self.x_pos_mm_signal.emit(round(position_deg_or_mm, 2))
        elif self.ax_letters[i].upper() == "R":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_deg_or_mm = position_deg_or_mm + self.config['WTF_PositionParameters']['ThetaHomeCoord']+\
                                 self.config['WTF_PositionParameters']['ThetaHomeEdgeOffset']
            self.r_pos_mm_signal.emit(round(position_deg_or_mm, 2))

        return position_deg_or_mm

    def check_user_fault(self) -> str:
        """
        Motor controller will usually have an error number and code, if it doesn't,
        simply print out python's exception

        :returns: galil motor controller response to 'TC 1': check error code command
        """
        try:
            error = self.command("TC 1")
            return error
        except gclib.GclibError as e:
            return str(e)

    def command(self, command: str) -> str:
        """
        Helper method to send command to the galil motor controller

        :param command: the command in string form you wish to send to the motor controller
        :return: response of galil motor controller to issues command
        """
        print(command)
        try:
            output = self.handle.GCommand(command)
        except gclib.GclibError as e:
            if "device read error" in str(e) or 'device write error' in str(e):
                self.log(level='error', message=f'Error in command device is likely disconnected, {e}.')
            else:
                code = self.check_user_fault()
                self.log(level='error', message=f'Error in command device {code}.')
            return ""

        t.sleep(.01)
        return output.replace('\r\n','')
