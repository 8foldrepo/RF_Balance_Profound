import time as t

import serial
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication

from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
from Utilities.useful_methods import create_coord_rays, is_number


class ParkerMotorController(AbstractMotorController):
    """Class providing functionality for one or more Parker VIX-250 IM drives"""

    command_history = list()
    echo_history = list()
    response_history = list()
    history_length = 5

    def __init__(self, config: dict, device_key="VIX_Motors", parent=None, lock=None):
        self.lock = lock
        super().__init__(parent=parent, config=config, device_key=device_key)
        # For refreshing UI
        self.app = QApplication.instance()
        # Serial communication object for the motor controllers
        self.ser = None

    # Tells one axis what coordinate to travel to
    # Axis must be 'x' , 'y' , 'z' , or 'r'
    @pyqtSlot(list, list)
    def go_to_position(self, axes: list, coords_mm: list, enable_ui: bool = True) -> bool:
        # self.command("0SV")
        # self.command("0Z")
        # t.sleep(0.25)
        success = True

        if not self.connected:
            if enable_ui:
                self.ready_signal.emit()
            return False

        if not len(axes) == len(coords_mm):
            self.log(level='error', message="Axes length does not match coordinates length")
            if enable_ui:
                self.ready_signal.emit()
            return False

        axis_numbers = list()
        coords = list()

        for i in range(len(axes)):
            if axes[i].upper() in self.ax_letters:
                num = self.ax_letters.index(axes[i].upper()) + 1
            else:
                num = 0

            axis_numbers.append(num)

            target_coordinate_mm = float(coords_mm[i])
            target_coord_steps = self.__position_to_steps(num - 1, target_coordinate_mm)

            coords.append(target_coord_steps)

        if not self.movement_mode == "Distance":
            self.set_movement_mode("Distance")

        for i in range(len(axis_numbers)):
            self.command(f'{axis_numbers[i]}D{int(coords[i])}')
            self.command(f'{axis_numbers[i]}G')
            if '*E' in self.get_response(retries=1):
                self.log(f"Movement of {axis_numbers[i]} to coordinate {coords} failed, checking fault data")
                self.check_user_fault(axis_number=axis_numbers[i])
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

    def set_origin_1d(self, axis, coord_mm, get_position=True):
        axis_number = self.__get_ax_number(axis)
        axis_index = axis_number - 1

        coord_steps = self.__position_to_steps(axis_index, coord_mm)

        home_coordinate = int(coord_steps)

        # add on the offset of the origin from the motor's zero

        self.command(f"{axis_number}W(PT,{home_coordinate})")

        if get_position:
            self.get_position()

    @pyqtSlot(dict)
    def setup_slot(self, settings=None):
        """Setup all axes according to a dictionary of settings. R is configured according to rotational settings."""
        self.setup(settings=settings)

    @pyqtSlot(int)
    def set_increment(self, increment):
        self.set_increment_1d(axis="All", increment=increment)

    @pyqtSlot()
    def stop_motion(self):
        self.log("Stopping motion")
        self.moving = not self.stop_motion_1d(axis="All")

    @pyqtSlot(float)
    def set_speeds(self, speed):
        self.set_speeds_1d(axis="All", speed=speed)

    @pyqtSlot()
    def go_home(self, enable_ui: bool = True):
        # Theta prehome move
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
    def go_home_1d(self, axis, enable_ui: bool = True):
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

    def setup_home(self):
        self.setup_home_1d(axis='X', enabled=self.config[self.device_key]['enable_homing_ray'][0],
                           reference_edge='+', normally_closed=True, speed=-5, mode=1)
        self.setup_home_1d(axis='R', enabled=self.config[self.device_key]['enable_homing_ray'][1],
                           reference_edge='+', normally_closed=True, speed=-3, mode=1)

    def setup_home_1d(self, axis, enabled=True, reference_edge='+', normally_closed=False, speed=-5, mode=1,
                      acceleration=10):
        axis_number = self.get_ax_number(axis)

        if enabled:
            onString = "1"
        else:
            onString = "0"

        if normally_closed:
            closedString = "1"
        else:
            closedString = "0"

        command_string = f"{axis_number}HOME{onString}({reference_edge},{closedString},{speed},{acceleration},{mode})"

        self.command(command_string, log=True)

    def connect_hardware(self):
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
            startTime = t.time()
            while t.time() - startTime < self.time_limit_s:
                self.ser.write(b"1R(BD)")
                t.sleep(0.1)
                reply = self.ser.read()
                if not reply == '':
                    self.connected = True
                    self.log("Motor controller connected and set to default settings")
                    return self.connected, ''

            self.connected = False
            self.log(level='error', message=
            f"{self.device_key} COM port found but motor controller is not responding. "
            f"Make sure it is powered up and click setup.")

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
                feedback = f"{self.device_key} not connected due to an unkown error. \n\n {e}"

        if not self.connected:
            self.log(level="error", message=feedback)
        self.connected_signal.emit(self.connected)
        return self.connected, feedback

    def disconnect_hardware(self):
        self.set_motors_on(False)
        self.ser.close()

        self.connected = False
        self.connected_signal.emit(self.connected)

    def check_connected(self):
        return self.connected

    def command(self, command, retry=True, time_limit=None, mutex_locked=False, log=True):
        """Attempt to send command until it is faithfully echoed by the controller, or else return false"""
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        import inspect
        print(f"method command in parker_motor_controller called by {inspect.stack()[1].function}")
        if self.lock is not None and not mutex_locked:
            self.lock.lock()

        # Log command if so desired
        if log:
            self.log(command)

        # Handle not connected case
        if not self.connected:
            self.log(level='error', message=f'motor not connected, could not send command: {command}')
            if self.lock is not None and not mutex_locked:
                self.lock.unlock()
            return

        start_time = t.time()
        if time_limit is None:
            time_limit = self.time_limit_s

        while t.time() - start_time < time_limit:
            print(
                f"t.time = {t.time()}, start_time = {start_time}, time_limit = {time_limit} ; t.time() - start_time = {t.time() - start_time}")  # debug line
            # start_time = t.time()
            bites = command.encode("utf-8")
            output = bites + b"\r\n"

            # Keep track of the previous few commands for debugging purposes
            self.command_history.append(output)
            if len(self.command_history) > self.history_length:
                self.command_history.pop(0)

            if log:
                self.log(f"output = {output}")

            self.ser.write(output)
            # t.sleep(0.1)
            # Listen for echo twice
            for i in range(2):
                echo = self.ser.readline().strip(b"\r\n")
                # t.sleep(0.1)
                # Keep track of the previous few echos for debugging purposes
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

    def print_response(self, mutex_locked=False):
        """Print every line of the controller's output until timeout is reached"""
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        if self.lock is not None and not mutex_locked:
            self.lock.lock()

        start_time = t.time()
        while t.time() - start_time < self.time_limit_s:
            start_time = t.time()
            y = self.ser.readline().strip(b"\r\n")
            self.log(f"Response:{y}")
        self.log(level="error", message=f"{self.device_key} timed out")

        if self.lock is not None and not mutex_locked:
            self.lock.unlock()

    # todo: (stretch) implement
    def get_serial_number(self) -> str:
        pass

    def get_response(self, retries=2, need_reply=False, mutex_locked=False):
        """Return the next non-empty line of the controller's response over serial. Assumes echo has already been read"""
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        if self.lock is not None and not mutex_locked:
            self.lock.lock()
        reply = b""
        for i in range(retries):
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

        # Keep track of the previous few commands for debugging purposes
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

    def ask(self, command, retries=5, mutex_locked=False, log=True):
        for i in range(retries):
            self.command(command, mutex_locked=mutex_locked, log=log)
            response = self.get_response(mutex_locked=mutex_locked)
            if "*E" not in response:
                return response
        return ""

    def set_motors_on(self, on):
        """Set all motors on/off depending on boolean on"""
        self.set_motor_on(axis="All", on=on)

    def set_motor_on(self, axis, on):
        """Set motor with given axis letter on/off depending on boolean on"""
        axis_number = self.__get_ax_number(axis)

        if on:
            self.command(f"{axis_number}ON")
        else:
            self.command(f"{axis_number}OFF")

    def setup(self, settings=None):
        if self.ser is None:
            self.connect_hardware()

        # confirm drive is responding
        startTime = t.time()
        self.connected = False
        while t.time() - startTime < self.time_limit_s:
            self.ser.write(b"1R(BD)")
            t.sleep(0.1)
            reply = self.ser.read()
            if not reply == "":
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
        self.setup_position_maintanance()
        self.set_movement_mode(self.movement_mode)
        self.set_motors_on(True)
        self.setup_home()
        self.command("2W(IC,7136)")  # configure inputs of r axis

        for i in range(len(self.ax_letters)):
            self.update_distance_and_velocity(axis=self.ax_letters[i])

        self.log("Done setting up")
        self.ready_signal.emit()

    def set_movement_mode(self, movement_mode):
        self.movement_mode = movement_mode
        self.set_mode_1d(axis="All", movement_mode=self.movement_mode)

    def set_mode_1d(self, axis, movement_mode=None):
        axis_number = self.__get_ax_number(axis)

        if movement_mode is None:
            movement_mode = self.movement_mode

        if movement_mode == "Incremental":
            self.command(f"{axis_number}MI", log=True)
        elif movement_mode == "Continuous":
            self.command(f"{axis_number}MC", log=True)
        elif movement_mode == "Distance":
            self.command(f"{axis_number}MA", log=True)

    def update_distance_and_velocity(self, axis):
        """Setup an axis according to a dictionary of settings. R is configured according to rotational settings."""
        axis_index = self.ax_letters.index(axis)
        axis_number = axis_index + 1
        steps_per_s = self.speeds_ray[axis_index]
        # self.calibrate_ray_steps_per[axis_index] *
        self.command(f"{axis_number}V{steps_per_s}")
        self.command(f"{axis_number}D{self.increment_ray[axis_index]}")

    def set_limits_enabled(self, enabled=True):
        if enabled:
            self.command("0LIMITS(0,1,0,200)")
        else:
            self.command("0LIMITS(1,1,0,200)")

    def setup_position_maintanance(self):
        for i in range(2):
            if self.config[self.device_key]['encoder_installed_ray'][i]:
                self.command(
                    f"{i + 1}POSMAIN1(10)")  # turn on position maintainence for theta with a margin of error of 2/2000 revolutions
            else:
                self.command(f"{i + 1}POSMAIN0(10)")

    def set_speeds_1d(self, axis, speed):
        axis_number = self.__get_ax_number(axis)
        self.command(f"{axis_number}V{speed}")

    def set_increment_1d(self, axis, increment):
        axis_number = self.__get_ax_number(axis)
        self.command(f"{axis_number}D{increment}")

    def stop_motion_1d(self, axis):
        axis_number = self.__get_ax_number(axis)

        stopped = False
        for i in range(20):
            if stopped:
                return True
            else:
                stopped = self.command(f"{axis_number}S", retry=False)
        return stopped

    def getBaud(self):
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
    def begin_motion(self, axis=None, direction=None):
        axis_index = self.ax_letters.index(axis)

        current_coordinate_mm = self.coords_mm[axis_index]

        if direction < 0:
            go_to_coord_mm = int((current_coordinate_mm - abs(self.increment_ray[axis_index])))
        else:
            go_to_coord_mm = int((current_coordinate_mm + abs(self.increment_ray[axis_index])))

        self.go_to_position([axis], [go_to_coord_mm], enable_ui=True)

    @pyqtSlot()
    def stop_motion(self):
        self.log("Stopping motion")
        self.moving = not self.stop_motion_1d(axis="All")

    def get_position(self, mutex_locked=False):
        # Assume motors are not moving unless their position is changing
        moving_ray = [False, False]
        moving_margin_ray = [0.001, 0.001]

        for i in range(len(self.ax_letters)):
            position_string = self.ask(f"{i + 1}R(PT)", mutex_locked=mutex_locked, log=False)
            position_string = position_string.replace('*', '')

            if not is_number(position_string):
                self.log(level='Error', message=f'Failed to get {self.ax_letters[i]} position')
                continue

            position_steps = float(position_string)

            position_deg_or_mm = self.__steps_to_position(i, position_steps)

            # Check if position has not changed. If all axes have not changed moving will be false
            if abs(position_deg_or_mm - self.coords_mm[i]) > moving_margin_ray[i]:
                moving_ray[i] = True

            self.coords_mm[i] = position_deg_or_mm

        # Update the moving variable and emit it as a signal
        if True in moving_ray:
            self.moving = True
        else:
            self.moving = False
        self.moving_signal.emit(self.moving)

        if self.app is not None:
            self.app.processEvents()

    def check_user_fault(self, axis_number):
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

    def exec_command(self, command):
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
            axes, coords = create_coord_rays(cmd_ray[1], self.ax_letters)
            self.go_to_position(axes=axes, coords_mm=coords)
        elif cmd_ray[0] == "Origin".upper():
            if cmd_ray[1] == "Here".upper():
                self.set_origin_here()

    def __get_ax_number(self, axis):
        """return the motor controller driver number of the axis with the specified letter"""
        # Added flexibility for synonomous axis identifiers
        if axis.upper() == "Theta".upper() or axis.upper() == "Th".upper():
            axis = "R"
        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number

    def setup_motors(self):
        """
        This method takes a while to execute, do not call it in the main application. Call it in the script at the
        bottom of this class when setting up a new system. Use caution because when used with 0SV it overwrites settings
        """
        self.set_motors_on(False)
        self.command("1MOTOR(718,1,1000,500,5,0.63,2)")
        self.command("2MOTOR(718,0.1,2000,100,5,3.2,2)")
        self.print("Motors set, use a serial terminal to confirm smooth operation, then command 0SV and 0Z")

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

    def wrap_up(self):
        self.set_motors_on(False)
        self.stop_motion()
        self.disconnect_hardware()


if __name__ == "__main__":
    motors = ParkerMotorController(config=None)
    motors.connect_hardware()

    for i in range(2):
        for item in [0, -263, -90]:
            y = motors.__position_to_steps(i, item)
            x = motors.__steps_to_position(i, y)
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
