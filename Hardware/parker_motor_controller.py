import time as t
from typing import Union, Tuple, Optional, List


import serial
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
from Utilities.useful_methods import create_coord_rays, is_number


class ParkerMotorController(AbstractMotorController):
    """Class providing functionality for one or more Parker VIX-250 IM drives"""

    command_history = list()
    echo_history = list()
    response_history = list()
    history_length = 5

    def __init__(self, config: Union[dict, None], device_key="VIX_Motors", parent=None, lock=None):
        self.lock = lock
        super().__init__(parent=parent, config=config, device_key=device_key, lock=lock)
        # For refreshing UI
        self.app = QApplication.instance()
        # Serial communication object for the motor controllers
        self.ser = None

    # Tells one axis what coordinate to travel to
    # Axis must be 'x' , 'y' , 'z' , or 'r'
    @pyqtSlot(list, list)
    def go_to_position(self, axes: list, coordinates_mm: list, enable_ui: bool = True) -> bool:
        """
        Sends a command to the controller telling it to move the
        given axes to the given coordinates, contains exception handling
        """
        # self.command("0SV")
        # self.command("0Z")
        # t.sleep(0.25)
        success = True

        if not self.connected:
            if enable_ui:
                self.ready_signal.emit()
            return False

        if len(axes) != len(coordinates_mm):
            self.log(level='error', message="Axes length does not match coordinates length")
            if enable_ui:
                self.ready_signal.emit()
            return False

        axis_numbers = list()
        coordinates = list()

        for current_axis_number in range(len(axes)):
            if axes[current_axis_number].upper() in self.ax_letters:
                num = self.ax_letters.index(axes[current_axis_number].upper()) + 1
            else:
                num = 0

            axis_numbers.append(num)

            target_coordinate_mm = float(coordinates_mm[current_axis_number])
            target_coord_steps = self.position_to_steps(num - 1, target_coordinate_mm)

            coordinates.append(target_coord_steps)

        if self.movement_mode != "Distance":
            self.set_movement_mode("Distance")

        for current_axis_number in range(len(axis_numbers)):
            self.command(f'{axis_numbers[current_axis_number]}D{int(coordinates[current_axis_number])}')
            self.command(f'{axis_numbers[current_axis_number]}G')
            if '*E' in self.get_response(retries=1):
                self.log(f"Movement of {axis_numbers[current_axis_number]} to coordinate {coordinates} failed, checking fault data")
                self.check_user_fault(axis_number=axis_numbers[current_axis_number])
                if enable_ui:
                    self.ready_signal.emit()
                return False
            else:
                self.moving = True
                self.moving_signal.emit(True)

        start_time = t.time()
        while self.moving and t.time() - start_time < self.config[self.device_key]['move_timeout_s']:
            self.get_position()
            t.sleep(.1)

        if self.moving:
            self.log(level='error', message='movement timed out')
            self.stop_motion()
            success = False

        # Wait for motion to be over
        # t.sleep(2)
        # Check position
        # self.get_position()
        # Send ready signal to enable UI
        if enable_ui:
            self.ready_signal.emit()
        return success

    @pyqtSlot()
    def set_origin_here(self) -> None:
        """Relay method to set origin in current position for all axes in the self-contained ax_letters list"""
        for axis in self.ax_letters:
            self.set_origin_here_1d(axis=axis)

    @pyqtSlot()
    def set_origin_here_1d(self, axis) -> None:
        """Relay method to set a particular axis to current position"""
        self.set_origin_1d(axis=axis, coord_mm=0)

    @pyqtSlot()
    def set_origin(self, origin_mm: list) -> Optional[None]:
        """
        Relay method that calls set_origin_1d to set the origin of all the axes in
        self.ax_letters to given list of coordinates in mm, lengths of lists must match
        """
        if len(origin_mm) != len(self.ax_letters):
            self.log(level='error', message='Error in set_origin, not enough coordinates provided')
            return

        for current_axis in range(len(origin_mm)):
            self.set_origin_1d(axis=self.ax_letters[current_axis], coord_mm=origin_mm[current_axis], get_position=False)

        self.get_position()

    def set_origin_1d(self, axis, coord_mm, get_position=True) -> None:
        """
        Sends the set origin command to the motor controller for the given axis and
        coordinate in mm, also has option to return the current position after command runs
        """
        axis_number = self.__get_ax_number(axis)
        axis_index = axis_number - 1

        coord_steps = self.position_to_steps(axis_index, coord_mm)

        home_coordinate = int(coord_steps)

        # add on the offset of the origin from the motor's zero

        self.command(f"{axis_number}W(PT,{home_coordinate})")

        if get_position:
            self.get_position()

    @pyqtSlot(dict)
    def setup_slot(self, settings=None) -> None:
        """Setup all axes according to a dictionary of settings. R is configured according to rotational settings."""
        self.setup(settings=settings)

    @pyqtSlot(int)
    def set_increment(self, increment: int) -> None:
        """Setter for increment variable, applies to all axes"""
        self.set_increment_1d(axis="All", increment=increment)

    @pyqtSlot()
    def stop_motion(self) -> None:
        """Sends the stop-motion command to the controller, applies to all axes"""
        self.log("Stopping motion")
        self.moving = not self.stop_motion_1d(axis="All")

    @pyqtSlot(float)
    def set_speeds(self, speed: float) -> None:
        """Setter for the movement speed of the motors, input must be a float value. Method relays to set_speeds_1d"""
        self.set_speeds_1d(axis="All", speed=speed)

    @pyqtSlot()
    def go_home(self, enable_ui: bool = True) -> bool:
        """
        Tells the controller to go to theta's pre-home position before moving to -90 degrees home
        position, has error/exception handling, and timeout. Returns boolean representing success
        """
        # Theta pre-home move
        self.go_to_position(['R'], [self.config["WTF_PositionParameters"]["ThetaPreHomeMove"]], enable_ui=False)
        self.command(f"0GH")

        success = True

        start_time = t.time()
        while self.moving and t.time() - start_time < self.config[self.device_key]['move_timeout_s']:
            self.get_position()
            t.sleep(.1)

        if self.moving:
            self.log(level='error', message='go home timed out')
            self.stop_motion()
            success = False

        t.sleep(3)

        self.go_to_position(['R'], [-90], enable_ui=False)

        if enable_ui:
            self.ready_signal.emit()
        return success

    @pyqtSlot(str)
    def go_home_1d(self, axis, enable_ui: bool = True) -> bool:
        """
        Method to move a particular axis to its home position. Has theta move to
        pre-home position if targeted. Returns whether command succeeded or failed
        """
        if axis == 'R' or axis == "Theta":
            self.go_to_position(['R'], [self.config["WTF_PositionParameters"]["ThetaPreHomeMove"]], enable_ui=False)

        axis_number = self.__get_ax_number(axis)
        self.command(f"{axis_number}GH")

        success = True

        start_time = t.time()
        while self.moving and t.time() - start_time < self.config[self.device_key]['move_timeout_s']:
            self.get_position()

        if self.moving:
            self.log(level='error', message='go home timed out')
            self.stop_motion()
            success = False

        t.sleep(3)

        if axis == 'R' or axis == "Theta":
            self.go_to_position(['R'], [-90], enable_ui=False)

        if enable_ui:
            self.ready_signal.emit()
        return success

    def setup_home(self) -> None:
        """Relay method calling setup_home_1d for both X and theta axes"""
        self.setup_home_1d(axis='X', enabled=self.config[self.device_key]['enable_homing_ray'][0],
                           reference_edge='+', normally_closed=True, speed=-5, mode=1)
        self.setup_home_1d(axis='R', enabled=self.config[self.device_key]['enable_homing_ray'][1],
                           reference_edge='+', normally_closed=True, speed=-3, mode=1)

    def setup_home_1d(self, axis: str, enabled: bool = True, reference_edge: str = '+', normally_closed: bool = False, speed: int = -5, mode: int = 1,
                      acceleration: int = 10) -> None:
        """Sends the home command to the controller passing various parameters required by the HOME command"""
        axis_number = self.__get_ax_number(axis)

        if enabled:
            on_string = "1"
        else:
            on_string = "0"

        if normally_closed:
            closed_string = "1"
        else:
            closed_string = "0"

        command_string = f"{axis_number}HOME{on_string}({reference_edge},{closed_string},{speed},{acceleration},{mode})"

        self.command(command_string, log=True)

    def connect_hardware(self) -> Tuple[bool, str]:
        """Attempts to make a serial connection to controller and sets internal variables to default values"""
        feedback = ""
        try:
            self.log("Connecting to motor controller...")
            self.ser = serial.Serial(
                port=self.port,  # May vary depending on computer
                baudrate=19200,
                timeout=self.timeout_s,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
            )
            self.setup()
            start_time = t.time()
            while t.time() - start_time < self.time_limit_s:
                self.ser.write(b"1R(BD)")
                t.sleep(0.1)
                reply = self.ser.read()
                if reply != '':
                    self.connected = True
                    self.log("Motor controller connected and set to default settings")
                    return self.connected, ''

            self.connected = False
            self.log(level='error', message=f"{self.device_key} COM port found but motor controller is not "
                                            f"responding. Make sure it is powered up and click setup.")

            self.connected = True
        except serial.serialutil.SerialException as e:
            self.connected = False
            if "PermissionError" in str(e):
                feedback = f"{self.device_key} not connected. Another program is likely using it"
            elif 'FileNotFoundError' in str(e):
                feedback = f"{self.device_key} not connected because the COM port was not found. Check that it is " \
                           f"plugged in and look at Device manager to determine which COM port to use. enter it" \
                           f" into Local.yaml: \n\n {e}"
            else:
                feedback = f"{self.device_key} not connected due to an unknown error. \n\n {e}"

        if not self.connected:
            self.log(level="error", message=feedback)
        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def disconnect_hardware(self) -> None:
        """Closes serial connection, turns off motors and sets connected flag to false and sends it via signal"""
        self.set_motors_on(False)
        self.ser.close()

        self.connected = False
        self.connected_signal.emit(self.connected)

    def check_connected(self) -> bool:
        """Getter for class' internal connected boolean flag"""
        return self.connected

    def command(self, command: str, retry: bool = True, time_limit=None, mutex_locked: bool = False, log: bool = True) -> Union[None, bool]:
        """Attempt to send command until it is faithfully echoed by the controller, or else return false"""
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        if self.lock is not None and not mutex_locked:
            self.lock.lock()

        # Log command if so desired
        if log:
            self.log(f'{command} command sent to parker motor controller')

        # Handle not connected case
        if not self.connected:
            self.log(level='error', message=f'motor not connected, could not send command: {command}')
            if self.lock is not None and not mutex_locked:
                self.lock.unlock()
            return

        start_time = t.time()
        if time_limit is None:
            time_limit: float = self.time_limit_s

        while t.time() - start_time < time_limit:
            # start_time = t.time()
            bites = command.encode("utf-8")
            output = bites + b"\r\n"

            # Keep track of the previous few commands for Debugging purposes
            self.command_history.append(output)
            if len(self.command_history) > self.history_length:
                self.command_history.pop(0)

            if log:
                self.log(f"output = {output}")

            self.ser.write(output)
            # t.sleep(0.1)
            # Listen for echo twice
            for _ in range(2):
                echo = self.ser.readline().strip(b"\r\n")
                # t.sleep(0.1)
                # Keep track of the previous few echos for Debugging purposes
                self.echo_history.append(output)
                if len(self.echo_history) > self.history_length:
                    self.echo_history.pop(0)

                if echo == bites:
                    if self.lock is not None and not mutex_locked:
                        self.lock.unlock()
                    return True

            if not retry:
                break
        self.log(level="error", message=f"command not sent successfully: {command}")

        if self.lock is not None and not mutex_locked:
            self.lock.unlock()
        return False

    def print_response(self, mutex_locked: bool = False) -> None:
        """Print every line of the controller's output until timeout is reached"""
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        if self.lock is not None and not mutex_locked:
            self.lock.lock()

        start_time = t.time()
        while t.time() - start_time < self.time_limit_s:
            start_time = t.time()
            response_line = self.ser.readline().strip(b"\r\n")
            self.log(f"Response:{response_line}")
        self.log(level="error", message=f"{self.device_key} timed out")

        if self.lock is not None and not mutex_locked:
            self.lock.unlock()

    # todo: (stretch) implement
    def get_serial_number(self) -> str:
        """Returns the serial number of the parker motor controller (not yet implemented)"""
        return "get serial number for parker motor controller has not been implemented yet"

    def get_response(self, retries: int = 2, need_reply: bool = False, mutex_locked: bool = False) -> Union[bytes, str]:
        """Return the next non-empty line of the controller's response over serial. Assumes echo has already been read"""
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        if self.lock is not None and not mutex_locked:
            self.lock.lock()
        reply = b""
        for _ in range(retries):
            try:
                reply = self.ser.readline().strip(b"\r\n")
            except KeyboardInterrupt:
                self.log("Program terminated unexpectedly, ensuring motors are stopped")
                self.stop_motion()
                self.wrap_up()
                break
            except AttributeError as e:
                if str(e) == "'VIX_Motor_Controller' object has no attribute 'ser'":
                    self.log(f"{self.device_key} is not connected, could not get reply")
                    reply = b""
                    break
                else:
                    self.log(level="error", message=f"Unknown error in get reply: {e}")
            if reply != b"":
                break

        try:
            reply = reply.decode("utf-8")
        except UnicodeDecodeError:
            reply = ""

        if reply == "" and need_reply:
            self.log(level="error", message=f"{self.device_key} gave no reply")

        # Keep track of the previous few commands for Debugging purposes
        self.response_history.append(reply)
        if len(self.response_history) > self.history_length:
            self.response_history.pop(0)

        if "*E" in reply:
            self.log(level="Error", message="Motor error occured")
            self.log(f"Recent commands: {self.command_history}")
            self.log(f"Recent echos (should match commands) {self.echo_history}")
            self.log(f"Recent responses: {self.command_history}")

        if self.lock is not None and not mutex_locked:
            self.lock.unlock()

        return reply

    def ask(self, command: str, retries: int = 5, mutex_locked: bool = False, log: bool = True) -> Union[bytes, str]:
        """Sends the controller a command and returns the response if one exists"""
        for _ in range(retries):
            self.command(command, mutex_locked=mutex_locked, log=log)
            response = self.get_response(mutex_locked=mutex_locked)
            if "*E" not in response:
                return response
        return ""

    def set_motors_on(self, on: bool) -> None:
        """Set all motors on/off depending on boolean on"""
        self.set_motor_on(axis="All", on=on)

    def set_motor_on(self, axis: str, on: bool) -> None:
        """Set motor with given axis letter on/off depending on boolean on"""
        axis_number = self.__get_ax_number(axis)

        if on:
            self.command(f"{axis_number}ON")
        else:
            self.command(f"{axis_number}OFF")

    def setup(self, settings=None) -> None:
        """
        Ensures controller is connected and responding, initializes
        all settings and emits connected signal if appropriate
        """
        if self.ser is None:
            self.connect_hardware()

        # confirm drive is responding
        start_time = t.time()
        self.connected = False
        while t.time() - start_time < self.time_limit_s:
            self.ser.write(b"1R(BD)")
            t.sleep(0.1)
            reply = self.ser.read()
            if reply != "":
                self.connected = True
                self.log("Motor controller connected and set to default settings")
                break

        self.connected_signal.emit(self.connected)

        if not self.connected:
            self.log(level='error', message=f"{self.device_key} COM port found but motor controller is not "
                                            f"responding. Make sure it is powered up and click setup.")
            self.ready_signal.emit()
            return

        # This accounts for the lower idle current of the rotational motor.
        # Sets the rotational motor to 10% idle current
        sent_1_successfully = self.command("2W(MS,10)")
        # Sets the translational motor to 50% idle current
        sent_2_successfully = self.command("1W(MS,50)")

        if not (sent_1_successfully and sent_2_successfully):
            self.log(level='error', message='failed to setup, check that drivers are powered on and try again')
            return

        if settings is not None:
            self.increment_ray[0] = settings["lin_incr"]
            self.increment_ray[1] = settings["ang_incr"]
            self.speeds_ray[0] = settings["lin_speed"]
            self.speeds_ray[1] = settings["rot_speed"]
            self.calibrate_ray_steps_per[0] = settings["steps_per_mm"]
            self.calibrate_ray_steps_per[1] = settings["steps_per_deg"]
            self.movement_mode = settings["movement_mode"]
            self.gearing_ray[0] = settings["x_gearing"]
            self.gearing_ray[1] = settings["r_gearing"]

        self.set_limits_enabled(True)
        self.setup_position_maintenance()
        self.set_movement_mode(self.movement_mode)
        self.set_motors_on(True)
        self.setup_home()
        self.command("2W(IC,7136)")  # configure inputs of r axis

        for current_axis_letter in range(len(self.ax_letters)):
            self.update_distance_and_velocity(axis=self.ax_letters[current_axis_letter])

        self.log("Done setting up")
        self.ready_signal.emit()

    def set_movement_mode(self, movement_mode: Union[str, list]) -> None:
        """Setter for movement mode variable and relay for set_mode_1d method, affects all axes"""
        self.movement_mode = movement_mode
        self.set_mode_1d(axis="All", movement_mode=self.movement_mode)

    def set_mode_1d(self, axis: str, movement_mode: Union[str, list, None] = None) -> None:
        """
        Sets mode (string) for given axis (string) to either
        'Incremental,' 'Continuous,' or 'Distance' via command method
        """
        axis_number: int = self.__get_ax_number(axis)

        if movement_mode is None:
            movement_mode = self.movement_mode

        if movement_mode == "Incremental":
            self.command(f"{axis_number}MI", log=True)
        elif movement_mode == "Continuous":
            self.command(f"{axis_number}MC", log=True)
        elif movement_mode == "Distance":
            self.command(f"{axis_number}MA", log=True)

    def update_distance_and_velocity(self, axis: str) -> None:
        """Set up an axis according to a dictionary of settings. R is configured according to rotational settings."""
        axis_index: int = self.ax_letters.index(axis)
        axis_number: int = axis_index + 1
        steps_per_s: float = self.speeds_ray[axis_index]
        # self.calibrate_ray_steps_per[axis_index] *
        self.command(f"{axis_number}V{steps_per_s}")
        self.command(f"{axis_number}D{self.increment_ray[axis_index]}")

    def set_limits_enabled(self, enabled: bool = True) -> None:
        """Toggle on whether to enable pre-defined limits for element positions"""
        if enabled:
            self.command("0LIMITS(0,1,0,200)")
        else:
            self.command("0LIMITS(1,1,0,200)")

    def setup_position_maintenance(self) -> None:
        """Turns on position maintenance for axes depending on config value"""
        for j in range(2):
            if self.config[self.device_key]['encoder_installed_ray'][j]:
                self.command(
                    f"{j + 1}POSMAIN1(10)")  # turn on position maintenance for theta with a margin of error of 2/2000 revolutions
            else:
                self.command(f"{j + 1}POSMAIN0(10)")

    def set_speeds_1d(self, axis: str, speed: Union[float, int]) -> None:
        """Sets the speed (float or int) variable for given axis (string)"""
        axis_number = self.__get_ax_number(axis)
        self.command(f"{axis_number}V{speed}")

    def set_increment_1d(self, axis: str, increment: int) -> None:
        """Setter for the increment (int) value for the given axis (string)"""
        axis_number = self.__get_ax_number(axis)
        self.command(f"{axis_number}D{increment}")

    def stop_motion_1d(self, axis: str) -> bool:
        """Stops motion for given axis (string), returns whether stop command succeeded or failed"""
        axis_number: int = self.__get_ax_number(axis)

        stopped: bool = False
        for _ in range(20):
            if stopped:
                return True
            else:
                stopped = self.command(f"{axis_number}S", retry=False)
        return stopped

    def getBaud(self) -> Union[None, int]:
        """Query and return the baud rate"""
        if self.ser is None:
            self.log(level="error", message=f"{self.device_key} not connected")
            return
        self.command("1R(BR)")
        response = self.get_response()
        if str(b"19200") in str(response):
            return 19200
        elif str(b"9600") in str(response):
            return 9600
        else:
            return -1

    @pyqtSlot(str, int)
    def begin_motion(self, axis: str = None, direction: int = None):
        """Moves given axis (string) in given direction (int) via class' increment array """
        axis_index = self.ax_letters.index(axis)

        current_coordinate_mm = self.coords_mm[axis_index]

        if direction < 0:
            go_to_coord_mm: int = int((current_coordinate_mm - abs(self.increment_ray[axis_index])))
        else:
            go_to_coord_mm: int = int((current_coordinate_mm + abs(self.increment_ray[axis_index])))

        self.go_to_position([axis], [go_to_coord_mm], enable_ui=True)

    @pyqtSlot()
    def stop_motion(self) -> None:
        """Stops motion for all axes with pyqtSlot and logs it. Also updates moving variable"""
        self.log("Stopping motion")
        self.moving: bool = not self.stop_motion_1d(axis="All")

    def get_position(self, mutex_locked: bool = False) -> None:
        """Asks motor controller the position of the motors and sends signal conveying whether motor is moving in either axis"""
        # Assume motors are not moving unless their position is changing
        moving_ray: List[bool] = [False, False]
        moving_margin_ray: List[float] = [0.001, 0.001]

        for current_axis in range(len(self.ax_letters)):
            position_string = self.ask(f"{current_axis + 1}R(PT)", mutex_locked=mutex_locked, log=False)
            position_string = position_string.replace('*', '')

            if not is_number(position_string):
                self.log(level='Error', message=f'Failed to get {self.ax_letters[current_axis]} position')
                continue

            position_steps = float(position_string)

            position_deg_or_mm = self.steps_to_position(current_axis, position_steps)

            # Check if position has not changed. If all axes have not changed moving will be false
            if abs(position_deg_or_mm - self.coords_mm[current_axis]) > moving_margin_ray[current_axis]:
                moving_ray[current_axis] = True

            self.coords_mm[current_axis] = position_deg_or_mm

        # Update the moving variable and emit it as a signal
        if True in moving_ray:
            self.moving = True
        else:
            self.moving = False
        self.moving_signal.emit(self.moving)

        if self.app is not None:
            self.app.processEvents()

    def check_user_fault(self, axis_number: int) -> None:
        """
        Controller has 27 error flags for a malformed command, this method
        will provide user feedback as to if and how their command is malformed
        """
        response = self.ask(f"{axis_number}R(UF)", retries=1)
        response = response.replace("_", "")
        if "1" not in response:
            return
        if response[1] == "1":
            self.log("Value is out of range")
        if response[2] == '1':
            self.log("Incorrect command syntax (this is a known issue due to unreliable serial communication)")
        if response[3] == '1':
            self.log("Last label already in use")
        if response[4] == "1":
            self.log("Label of this name not defined")
        if response[5] == "1":
            self.log("Missing Z pulse when homing")
        if response[6] == "1":
            self.log("Homing failed - no signal detected")
        if response[7] == "1":
            self.log("Home signal too narrow")
        if response[8] == "1":
            self.log("Drive de-energised")
        if response[9] == "1":
            self.log("Cannot relate END statement to a label")
        if response[10] == "1":
            self.log("Program memory buffer full*")
        if response[11] == "1":
            self.log("No more motion profiles available")
        if response[12] == "1":
            self.log("No more sequence labels available")
        if response[13] == "1":
            self.log("End of travel limit hit")
        if response[14] == "1":
            self.log("Still moving")
        if response[15] == "1":
            self.log("Deceleration error")
        if response[16] == "1":
            self.log("Transmit buffer overflow")
        if response[17] == "1":
            self.log("User program nesting overflow")
        if response[18] == "1":
            self.log("Cannot use an undefined profile")
        if response[19] == "1":
            self.log("Drive not ready")
        if response[20] == "1":
            self.log("Save error")
        if response[21] == "1":
            self.log("Command not supported by this product")
        if response[22] == "1":
            self.log("Fieldbus error")
        if response[23] == "1":
            self.log("Input buffer overflow")
        if response[24] == "1":
            self.log("")
        if response[25] == "1":
            self.log("Command not actioned")
        if response[26] == "1":
            self.log("Scale distance is non-integer")
        if response[27] == "1":
            self.log("")

    def position_to_steps(self, axis_index: int, position_deg_or_mm: float) -> Union[None, float]:
        """Converts the user-facing coordinate in mm or degrees to the coordinate in motor steps"""

        if self.ax_letters[axis_index].upper() == "X":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_steps = position_deg_or_mm + self.config['WTF_PositionParameters']['XHomeCoord']
        elif self.ax_letters[axis_index].upper() == "R":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_steps = position_deg_or_mm - self.config['WTF_PositionParameters']['ThetaHomeCoord']
        else:
            self.log(level='error', message=f'axis index [{axis_index}] does not point to a valid axis in ax_letters '
                                            f'[{self.ax_letters}] in position_to_steps method in parker motor controller')
            return

        position_steps = position_steps * self.calibrate_ray_steps_per[axis_index] * self.gearing_ray[axis_index]

        if self.reverse_ray[axis_index]:
            position_steps = position_steps * -1

        return position_steps

    def steps_to_position(self, axis_index: int, position_steps: float) -> float:
        """Converts the coordinate in motor steps to the user-facing coordinate in mm or degrees"""
        position_deg_or_mm = position_steps / self.calibrate_ray_steps_per[axis_index] / self.gearing_ray[axis_index]

        if self.reverse_ray[axis_index]:
            position_deg_or_mm = position_deg_or_mm * -1

        if self.ax_letters[axis_index].upper() == "X":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_deg_or_mm = position_deg_or_mm - self.config['WTF_PositionParameters']['XHomeCoord']
            self.x_pos_mm_signal.emit(round(position_deg_or_mm, 2))
        elif self.ax_letters[axis_index].upper() == "R":
            # Add on the coordinate of the home position (from the motor's perspective it is zero)
            position_deg_or_mm = position_deg_or_mm + self.config['WTF_PositionParameters']['ThetaHomeCoord']
            self.r_pos_mm_signal.emit(round(position_deg_or_mm, 2))

        return position_deg_or_mm

    def exec_command(self, command: str) -> None:
        """Converts string command to method calls"""
        command = command.upper()
        cmd_ray = command.split(" ")

        if cmd_ray[0] == "MOTOR":
            cmd_ray.pop(0)
            command = command[6:]

        if command == "Stop Motion".upper():
            self.stop_motion()
        elif command == "Get Position".upper():
            self.get_position()
        elif cmd_ray[0] == "GO":
            axes, coordinates_mm = create_coord_rays(cmd_ray[1], self.ax_letters)
            self.go_to_position(axes=axes, coordinates_mm=coordinates_mm)
        elif cmd_ray[0] == "Origin".upper() and cmd_ray[1] == "Here".upper():
            self.set_origin_here()

    def __get_ax_number(self, axis: str) -> int:
        """return the motor controller driver number of the axis with the specified letter"""
        # Added flexibility for synonymous axis identifiers
        if axis.upper() == "Theta".upper() or axis.upper() == "Th".upper():
            axis = "R"
        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number

    def setup_motors(self) -> None:
        """
        This method takes a while to execute, do not call it in the main application. Call it in the script at the
        bottom of this class when setting up a new system. Use caution because when used with 0SV it overwrites settings
        """
        self.set_motors_on(False)
        self.command("1MOTOR(718,1,1000,500,5,0.63,2)")
        self.command("2MOTOR(718,0.1,2000,100,5,3.2,2)")
        self.log("Motors set, use a serial terminal to confirm smooth operation, then command 0SV and 0Z")

    # def setup_motor(self):
    #     self.command("0Z")
    #     self.set_position_maintanance(False)
    #     motor_type = 716  # Read from the profound driver
    #     stall_current_amps = 2.1
    #     encoder_resolution = 2000  # steps_rev
    #     max_rpm = 1000
    #     thermal_time_constant = 1000
    #     # Thermal time constant – is the time in seconds for the motor to reach
    #     # two-thirds of its rated temperature while operating at its continuous current
    #     # rating.
    #     r_ohms = 2
    #     l_mhenry = 2
    #     # command = f"1MOTOR({motor_type},{stall_current_amps},{10000},{max_rpm},{thermal_time_constant}," \
    #     #            f"{r_ohms},{l_mhenry},{50})"
    #     command = "1MOTOR(716,1.0,50000,1000,5,2,2)"
    #     # print(command)
    #     self.command(command)
    #     print(self.get_response())
    #
    # def setup_motor_1(self):
    #     self.command('1K')  # Kill any program that is running
    #     self.command('1CLEAR(ALL)')  # Erase all routines, etc
    #     self.command('1W(BR,19200)')  # BAUD rate
    #
    #     self.command('1W(CL,50)')  # Current clamp
    #
    #     self.command('1W(CQ,1)')  # Command queueing
    #
    #     self.command('1W(IC,8160)')  # I/O configuration
    #     self.command('1W(EI,2)')  # Following encoder inputs
    #     self.command('1W(EO,2)')  # Simulated encoder outputs
    #     self.command('1LIMITS(0,1,0,200.0)')  # ;Travel limits
    #
    #     # Homing setup
    #     self.command('1HOME1(+,1,-10.00,10.0,0,0)')  # Home setup 1
    #     self.command('1W(EW,50)')  # Error window
    #     self.command('1W(IT,10)')  # Settling time
    #     self.command('1GAINS(5.00,0.00,7.00,5.00,0)')  # Set gains
    #
    #     self.command('1W(IM,1)')  # Integral action in window
    #     self.command('1W(IW,50)')  # Integral window
    #
    #     self.command('1W(ES,1)')  # Drive enable sense (can over-ride input)'
    #     self.command('1W(PC,100)')  # Peak current
    #     self.command('1W(TL,4000)')  # Tracking limit
    #     # Motor configuration
    #     self.command('1MOTOR(457,1.2,4000,100,100,3.2,5,312.5)')  # Setup

    def wrap_up(self) -> None:
        """Sets motors on flag to false, calls both stop_motion() and disconnect_hardware() methods"""
        self.set_motors_on(False)
        self.stop_motion()
        self.disconnect_hardware()


if __name__ == "__main__":
    motors = ParkerMotorController(config=None)
    motors.connect_hardware()

    for i in range(2):
        for item in [0, -263, -90]:
            y = motors.position_to_steps(i, item)
            x = motors.steps_to_position(i, y)
            print(item)
            print(x)
            print(y)
            assert float(x) == float(item)

    # motors.setup_motor_1()
    # t.sleep(15)
    # motors.command("1W(PA,0)")
    # motors.command("1D10000")
    # motors.command("1ON")
    # motors.command("1G")
    #
    # t.sleep(1)
    #
    # target_position_string = motors.ask(f"1R(PT)")
    # actual_position_string = motors.ask(f"1R(PA)")
    # position_error_string = motors.ask(f"1R(PE)")
    #
    # print(f'Tar: {target_position_string}')
    # print(f'Act: {actual_position_string}')
    # print(f'Err: {position_error_string}')
