from abc import abstractmethod

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from Utilities.useful_methods import bound
from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
from Utilities.useful_methods import create_coord_rays, create_comma_string
import serial
import time as t
from Hardware.Abstract.abstract_device import AbstractDevice


class VIX_Motor_Controller(AbstractMotorController):
    """
        An abstract class that serves as a base for classes that interface with motor controllers.
        Used on its own, this class will create a DummyMotors object, which runs in a separate thread and simulates a
        generic motor controller. Remove the DummyMotors object and all uses of the dummy_command_signal when inheriting.

        Signals:
            logger_signal(str)   : communicates feedback (errors, messages) to the feedback widget

            x_pos_signal(str)    : communicates x position with scan area
            y_pos_signal(str)    : communicates y position with scan area
            z_pos_signal(str)    : communicates z position with scan area

        Slots:
            none

        Attributes:
            none

        Properties:
            _jog_speed : used in the jog method, controls how fast the gantry jogs
            _scan_speed : used in scanning, or any PA command

            each property's setter method raises an error if the type is not an int

        Methods:
            toggle_connection()
                attempts to connect to the controller if not connected
                disconnects from the controller if connected

            connected()
                checks connection to controller, return true if yes, false if no

            jog(axis, direction)
                sends jog command to controller given an axis and direction (+/-)
                uses jog speed property getter

            begin_motion(axis)
                sends begin motion command to controller given an axis
                for multiple axes, use 'AB', 'ABC' etc

            stop_motion()
                sends stop command to controller
                motors remain on after command is sent

            set_origin()
                sets coordinate system of controller to 0,0,0
                good for defining the center of a scan

            go_home()
                tells gantry to go to position 0,0,0

            mm_to_steps()
                uses calibrate property to convert a number of mm to a number of steps

            is_moving()
                poll controller, if the controller is moving return true
                else return false

            get_position()
                emits x,y,z position signals with current controller position

            clean_up()
                stop motors, and disconnect form the controller if connected
        """

    # Signals
    x_pos_mm_signal = pyqtSignal(float)
    y_pos_signal = pyqtSignal(float)
    r_pos_mm_signal = pyqtSignal(float)
    z_pos_signal = pyqtSignal(float)

    moving_signal = pyqtSignal(bool)
    ready_signal = pyqtSignal()
    connected_signal = pyqtSignal(bool)

    coords_mm = list()
    home_coords = list()

    command_history = list()
    echo_history = list()
    response_history = list()
    history_length = 5

    # Dummy code, replace when developing a hardware interface
    dummy_command_signal = pyqtSignal(str)

    def __init__(self, config: dict, device_key='VIX_Motors', parent=None, lock=None):
        self.lock = lock
        super().__init__(parent=parent, config=config, device_key=device_key)
        # For tracking latest known coordinates in steps
        self.app = QApplication.instance()
        self.coords_mm = list()
        for i in range(self.num_axes):
            self.coords_mm.append(0)
        # Tracks whther or not the gantry is going to a position
        self.scanning = False
        self.jogging = False
        self.moving = None

        # Serial communication object for the motor controllers
        self.ser = None

        self.fields_setup()

    def fields_setup(self):
        self.ax_letters = self.config[self.device_key]['axes']
        num_axes = len(self.ax_letters)
        for i in range(num_axes):
            self.coords_mm.append(0)
        self.reverse_ray = self.config[self.device_key]['reverse_ray']
        self.movement_mode = self.config[self.device_key]['movement_mode']
        self.ax_letters = self.config[self.device_key]['axes']
        self.calibrate_ray_steps_per = self.config[self.device_key]['calibrate_ray']
        self.speeds_ray = self.config[self.device_key]['speeds_ray']
        self.increment_ray = self.config[self.device_key]['increment_ray']
        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.time_limit_s = self.config[self.device_key]['time_limit_s']
        self.on_by_default = self.config[self.device_key]['on_by_default']
        self.port = self.config[self.device_key]['port']

    # Tells one axis what coordinate to travel to
    # Axis must be 'x' , 'y' , 'z' , or 'r'
    @pyqtSlot(list, list)
    def go_to_position(self, axes: list, coords_mm: list) -> bool:
        if not self.connected:
            self.ready_signal.emit()
            return False

        if not len(axes) == len(coords_mm):
            self.log(level='error', message="Axes length does not match coordinates length")
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

            if axes[i] == 'X':
                # Remove the coordinate of the home position (the motor doesn't recognize it)
                origin_offset = self.config['WTF_PositionParameters']['XHomeCoord']
            if axes[i] == 'R':
                # Remove the coordinate of the home position (the motor doesn't recognize it)
                origin_offset = self.config['WTF_PositionParameters']['ThetaHomeCoord']

            motor_steps = (target_coordinate_mm - origin_offset) * float(self.calibrate_ray_steps_per[num - 1])
            coords.append(motor_steps)

        if not self.movement_mode == "Distance":
            self.set_movement_mode("Distance")

        for i in range(len(axis_numbers)):
            self.command(f'{axis_numbers[i]}D{int(coords[i])}')
            self.command(f'{axis_numbers[i]}G')
            if '*E' in self.get_response(retries=1):
                if not self.jogging and not self.scanning:
                    self.log(f"Movement of {axis_numbers[i]} to coordinate {coords} failed, checking fault data")
                    self.check_user_fault(axis_number=axis_numbers[i])
                    self.ready_signal.emit()
                    return False
            else:
                self.moving = True
                self.moving_signal.emit(True)

        while self.moving:
            self.get_position()
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

    def set_origin_1d(self, axis, coord_mm, get_position=True):
        axis_number = self.get_ax_number(axis)
        axis_index = axis_number - 1

        if axis == 'R':
            coord_mm = coord_mm + self.config['WTF_PositionParameters']['ThetaHomeCoord']
        elif axis == 'X':
            coord_mm = coord_mm + self.config['WTF_PositionParameters']['XHomeCoord']

        coord_steps = coord_mm * self.calibrate_ray_steps_per[axis_index]

        home_coordinate = -1 * int(coord_steps)

        # add on the offset of the origin from the motor's zero

        self.command(f'{axis_number}W(PT,{home_coordinate})')

        if get_position:
            self.get_position()

    '''Setup all axes according to a dictionary of settings. R is configured according to rotational settings.'''

    @pyqtSlot(dict)
    def setup_slot(self, settings=None):
        self.setup(settings=settings)

    @pyqtSlot(int)
    def set_increment(self, increment):
        self.set_increment_1d(axis='All', increment=increment)

    @pyqtSlot()
    def stop_motion(self):
        self.log("Stopping motion")
        self.moving = not self.stop_motion_1d(axis='All')
        if self.moving == False:
            self.jogging = False
            self.scanning = False

    @pyqtSlot(float)
    def set_speeds(self, speed):
        self.set_speeds_1d(axis='All', speed=speed)

    @pyqtSlot()
    def go_home(self):
        self.command(f'0GH')

    @pyqtSlot(str)
    def go_home_1d(self, axis):
        axis_number = self.get_ax_number(axis)
        self.command(f'{axis_number}GH')

    def setup_home(self):
        #todo: test and uncomment
        self.setup_home_1d(axis='X', enabled=self.config[self.device_key]['enable_homing_ray'][0],
                           reference_edge='+', normally_closed=False, speed=10, mode=1)
        self.setup_home_1d(axis='R', enabled=self.config[self.device_key]['enable_homing_ray'][1],
                           reference_edge='-', normally_closed=False, speed=1, mode=1)

    def setup_home_1d(self, axis, enabled=True, reference_edge='+', normally_closed=False, speed=-5, mode=1,
                      accelleration = 10):
        axis_number = self.get_ax_number(axis)

        if enabled:
            onString = '1'
        else:
            onString = '0'

        if normally_closed:
            closedString = '1'
        else:
            closedString = '0'

        command_string = f"{axis_number}HOME{onString}({reference_edge},{closedString},{speed},{accelleration},{mode})"

        self.command(command_string, log=True)

    # Hardware interfacing functions
    def toggle_connection(self):
        if self.connected():
            return self.connect_hardware()
        else:
            return self.disconnect_hardware()

    def connect_hardware(self):
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

            #self.setup()

            # startTime = t.time()
            # while t.time()-startTime < self.time_limit_s:
            #     self.ser.write(b"1R(BD)")
            #     reply = self.ser.read()
            #     if not reply == '':
            #         self.connected = True
            #
            #         self.log("Motor controller connected and set to default settings")
            #         return
            #
            # self.connected = False
            # self.log(level='error', message=
            # f"{self.device_key} COM port found but motor controller is not responding. "
            # f"Make sure it is powered up and click setup.")
            self.connected = True
        except serial.serialutil.SerialException as e:
            self.connected = False
            if "PermissionError" in str(e):
                self.log(level='error', message=
                f"{self.device_key} not connected. Another program is likely using it")
            else:
                self.log(level='error', message=
                f"{self.device_key} not connected. Check that it is plugged in and look at Device manager "
                f"to determine which COM port to use. enter it into Local.yaml {e}")

        # TODO: remove this when limits are added
        self.connected_signal.emit(self.connected)

    def disconnect_hardware(self):
        try:
            self.set_motors_on(False)
            self.ser.close()
        except:
            pass
        self.connected = False
        self.connected_signal.emit(self.connected)

    def is_connected(self):
        return self.connected

    '''Attempt to send command until it is faithfully echoed by the controller, or else return false'''

    def command(self, command, retry=True, time_limit=None, mutex_locked=False, log=True):
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
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

        starttime = t.time()
        if time_limit is None:
            time_limit = self.time_limit_s

        while t.time() - starttime < time_limit:
            starttime = t.time()
            bites = command.encode('utf-8')
            output = bites + b'\r\n'

            # Keep track of the previous few commands for debugging purposes
            self.command_history.append(output)
            if len(self.command_history) > self.history_length:
                self.command_history.pop(0)

            if log:
                self.log(f"output = {output}")

            self.ser.write(output)
            t.sleep(.05) #todo: test this for time and reliability
            # Listen for echo twice
            for i in range(2):
                echo = self.ser.readline().strip(b'\r\n')

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
        self.log(level='error', message=f'command not sent successfully: {command}')

        if self.lock is not None and not mutex_locked:
            self.lock.unlock()
        return False

    '''Print every line of the controller's output until timeout is reached'''

    def print_response(self, mutex_locked=False):
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        if self.lock is not None and not mutex_locked:
            self.lock.lock()

        starttime = t.time()
        while t.time() - starttime < self.time_limit_s:
            starttime = t.time()
            y = self.ser.readline().strip(b'\r\n')
            self.log(f'Response:{y}')
        self.log(level='error', message=f'{self.device_key} timed out')

        if self.lock is not None and not mutex_locked:
            self.lock.unlock()

    '''Return the next non-empty line of the controller's response over serial. Assumes echo has already been read'''

    def get_response(self, retries=2, need_reply=False, mutex_locked=False):
        # Argument mutex_locked tells this method not to lock the mutex if it was already locked at a higher level
        if self.lock is not None and not mutex_locked:
            self.lock.lock()

        for i in range(retries):
            reply = b''
            try:
                reply = self.ser.readline().strip(b'\r\n')
            except KeyboardInterrupt:
                self.log("Program terminated unexpectedly, ensuring motors are stopped")
                self.stop_motion()
                self.wrap_up()
                break
            except AttributeError as e:
                if str(e) == "\'VIX_Motor_Controller\' object has no attribute \'ser\'":
                    self.log(f"{self.device_key} is not connected, could not get reply")
                    reply = b''
                    break
                else:
                    self.log(level="error", message=f"Unknown error in get reply: {e}")
            if reply != b'':
                break

        try:
            reply = reply.decode('utf-8')
        except UnicodeDecodeError:
            reply = ''

        if reply == '' and need_reply:
            self.log(level='error', message=f'{self.device_key} gave no reply')

        # Keep track of the previous few commands for debugging purposes
        self.response_history.append(reply)
        if len(self.response_history) > self.history_length:
            self.response_history.pop(0)

        if '*E' in reply:
            self.log(level='Error', message="Motor error occured")
            self.log(f"Recent commands: {self.command_history}")
            self.log(f"Recent echos (should match commands) {self.echo_history}")
            self.log(f"Recent responses: {self.command_history}")

        if self.lock is not None and not mutex_locked:
            self.lock.unlock()

        return reply

    def ask(self, command, retries=5, mutex_locked=False, log=False):
        for i in range(retries):
            self.command(command, mutex_locked=mutex_locked, log=log)
            response = self.get_response(mutex_locked=mutex_locked)
            if not '*E' in response:
                return response
        return ''

    '''Set all motors on/off depending on boolean on'''

    def set_motors_on(self, on):
        self.set_motor_on(axis='All', on=on)

    '''Set motor with given axis letter on/off depending on boolean on'''

    def set_motor_on(self, axis, on):
        axis_number = self.get_ax_number(axis)

        if on:
            self.command(f'{axis_number}ON')
        else:
            self.command(f'{axis_number}OFF')

    def setup(self, settings=None):
        if self.ser is None:
            self.connect_hardware()

        #confirm drive is responding
        startTime = t.time()
        self.connected = False
        while t.time() - startTime < self.time_limit_s:
            self.ser.write(b"1R(BD)")
            t.sleep(.1)
            reply = self.ser.read()
            if not reply == '':
                self.connected = True
                self.log("Motor controller connected and set to default settings")
                break

        self.connected_signal.emit(self.connected)

        if self.connected == False:
            self.log(level='error', message=
            f"{self.device_key} COM port found but motor controller is not responding. "
            f"Make sure it is powered up and click setup.")
            self.ready_signal.emit()
            return

        # This accounts for the lower idle current of the rotational motor.
        # TODO: check currents of motors in final application
        #Sets the rotational motor to 10% idle current
        sent_1_successfully = self.command("2W(MS,10)")
        #Sets the translational motor to 50% idle current
        sent_2_successfully = self.command("1W(MS,50)")

        if not (sent_1_successfully and sent_2_successfully):
            self.log(level='error', message='failed to setup, check that drivers are powered on and try again')
            return

        if settings is not None:
            self.increment_ray[0] = settings['lin_incr']
            self.increment_ray[1] = settings['ang_incr']
            self.speeds_ray[0] = settings['lin_speed']
            self.speeds_ray[1] = settings['rot_speed']
            self.calibrate_ray_steps_per[0] = settings['steps_per_mm']
            self.calibrate_ray_steps_per[1] = settings['steps_per_deg']
            self.movement_mode = settings['movement_mode']

        self.set_limits_enabled(True)
        self.set_position_maintanance(on=False)
        self.set_movement_mode(self.movement_mode)
        self.set_motors_on(True)
        self.setup_home()

        for i in range(len(self.ax_letters)):
            self.update_distance_and_velocity(axis=self.ax_letters[i])

        self.log("Done setting up")
        self.ready_signal.emit()

    def set_movement_mode(self, movement_mode):
        self.movement_mode = movement_mode
        self.set_mode_1d(axis='All', movement_mode=self.movement_mode)

    def set_mode_1d(self, axis, movement_mode=None):
        axis_number = self.get_ax_number(axis)

        if movement_mode is None:
            movement_mode = self.movement_mode

        if movement_mode == 'Incremental':
            self.command(f'{axis_number}MI', log=True)
        elif movement_mode == 'Continuous':
            self.command(f'{axis_number}MC', log=True)
        elif movement_mode == 'Distance':
            self.command(f'{axis_number}MA', log=True)

    '''Setup an axis according to a dictionary of settings. R is configured according to rotational settings.'''

    def update_distance_and_velocity(self, axis):
        axis_index = self.ax_letters.index(axis)
        axis_number = axis_index + 1
        steps_per_s = self.calibrate_ray_steps_per[axis_index] * self.speeds_ray[axis_index]
             #self.calibrate_ray_steps_per[axis_index] *
        self.command(f'{axis_number}V{steps_per_s}')
        self.command(f'{axis_number}D{self.increment_ray[axis_index]}')

    def set_limits_enabled(self, enabled = True):
        if enabled:
            self.command('0LIMITS(0,1,0,200)')
        else:
            self.command("0LIMITS(1,1,0,200)")

    def set_position_maintanance(self, on):
        if on:
            self.command(f'0POSMAIN1(10)')
        else:
            self.command(f'0POSMAIN0(10)')

    def set_speeds_1d(self, axis, speed):
        axis_number = self.get_ax_number(axis)
        self.command(f'{axis_number}V{speed}')

    def set_increment_1d(self, axis, increment):
        axis_number = self.get_ax_number(axis)
        self.command(f'{axis_number}D{increment}')

    def stop_motion_1d(self, axis):
        axis_number = self.get_ax_number(axis)

        stopped = False
        for i in range(20):
            if stopped:
                return True
            else:
                stopped = self.command(f"{axis_number}S", retry=False)
        return stopped

    def is_moving(self):
        for i in range(len(self.ax_letters)):
            self.command(f"{i + 1}R(MV)", log=True)
            response = self.get_response()
            if '1' in response:
                return True
        return False

    @property
    def scan_speed(self):
        return self._scan_speed

    @property
    def calibrate(self):
        return (
            self._x_calibrate,
            self._y_calibrate,
            self._z_calibrate,
            self._r_calibrate,
        )

    '''Query and return the baud rate'''

    def getBaud(self):
        if self.ser is None:
            self.log(level='error', message=f'{self.device_key} not connected')
            return
        self.command("1R(BR)")
        response = self.get_response()
        if str(b'19200') in str(response):
            return 19200
        elif str(b'9600') in str(response):
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

        self.go_to_position([axis], [go_to_coord_mm])

    @pyqtSlot()
    def stop_motion(self):
        self.log("Stopping motion")
        self.moving = not self.stop_motion_1d(axis='All')
        if self.moving == False:
            self.jogging = False
            self.scanning = False

    def get_position(self, mutex_locked=False):
        # Assume motors are not moving unless their position is changing
        moving_ray = [False, False]
        moving_margin_ray = [0.001, .001]

        for i in range(len(self.ax_letters)):
            position_string = self.ask(f"{i + 1}R(PT)", mutex_locked=mutex_locked, log = False)
            position_string = position_string.replace('*', '')
            try:
                position_steps = float(position_string)
            except:
                return
            position_deg_or_mm = position_steps / self.calibrate_ray_steps_per[i]

            if self.reverse_ray[i]:
                position_deg_or_mm = position_deg_or_mm * -1

            if self.ax_letters[i].upper() == 'X':
                # Add on the coordinate of the home position (from the motor's perspective it is zero)
                position_deg_or_mm = position_deg_or_mm + self.config['WTF_PositionParameters']['XHomeCoord']
                self.x_pos_mm_signal.emit(round(position_deg_or_mm, 2))
            elif self.ax_letters[i].upper() == 'R':
                # Add on the coordinate of the home position (from the motor's perspective it is zero)
                position_deg_or_mm = position_deg_or_mm + self.config['WTF_PositionParameters']['ThetaHomeCoord']
                self.r_pos_mm_signal.emit(round(position_deg_or_mm, 2))

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
        # May cause crashing, replace this with a signal if crashes occur
        self.app.processEvents()

    def check_user_fault(self, axis_number):
        response = self.ask(f'{axis_number}R(UF)', retries=1)
        response = response.replace('_', '')
        if not '1' in response:
            return
        if response[1] == '1':
            self.log("Value is out of range")
        if response[2] == '1':
            self.log("Incorrect command syntax (this is a known issue due to unreliable serial communication)")
        if response[3] == '1':
            self.log("Last label already in use")
        if response[4] == '1':
            self.log("Label of this name not defined")
        if response[5] == '1':
            self.log("Missing Z pulse when homing")
        if response[6] == '1':
            self.log("Homing failed - no signal detected")
        if response[7] == '1':
            self.log("Home signal too narrow")
        if response[8] == '1':
            self.log("Drive de-energised")
        if response[9] == '1':
            self.log("Cannot relate END statement to a label")
        if response[10] == '1':
            self.log("Program memory buffer full*")
        if response[11] == '1':
            self.log("No more motion profiles available")
        if response[12] == '1':
            self.log("No more sequence labels available")
        if response[13] == '1':
            self.log("End of travel limit hit")
        if response[14] == '1':
            self.log("Still moving")
        if response[15] == '1':
            self.log("Deceleration error")
        if response[16] == '1':
            self.log("Transmit buffer overflow")
        if response[17] == '1':
            self.log("User program nesting overflow")
        if response[18] == '1':
            self.log("Cannot use an undefined profile")
        if response[19] == '1':
            self.log("Drive not ready")
        if response[20] == '1':
            self.log("Save error")
        if response[21] == '1':
            self.log("Command not supported by this product")
        if response[22] == '1':
            self.log("Fieldbus error")
        if response[23] == '1':
            self.log("Input buffer overflow")
        if response[24] == '1':
            self.log("")
        if response[25] == '1':
            self.log("Command not actioned")
        if response[26] == '1':
            self.log("Scale distance is non-integer")
        if response[27] == '1':
            self.log("")

    def exec_command(self, command):
        command = command.upper()
        cmd_ray = command.split(' ')

        if cmd_ray[0] == 'MOTOR':
            cmd_ray.pop(0)
            command = command[6:]

        if command == 'Disconnect'.upper():
            self.disconnect()
        elif command == 'Connect'.upper():
            self.connect()
        elif cmd_ray[0] == 'JOG' and cmd_ray[1] == 'SPEED':
            self.set_jog_speed(cmd_ray[2], float(cmd_ray[3]))
        elif cmd_ray[0] == 'SCAN' and cmd_ray[1] == 'SPEED':
            self.set_scan_speed(axis=cmd_ray[2], value=float(cmd_ray[3]))
        elif command == 'Stop Motion'.upper():
            self.stop_motion()
        elif command == 'Get Position'.upper():
            self.get_position()
        elif cmd_ray[0] == 'GO':
            axes, coords = create_coord_rays(cmd_ray[1], self.ax_letters)
            self.go_to_position(axes=axes, coords_mm=coords)
        elif cmd_ray[0] == 'Origin'.upper():
            if cmd_ray[1] == 'Here'.upper():
                self.set_origin_here()

    def wrap_up(self):
        self.disconnect_hardware()

    # return the motor controller driver number of the axis with the specified letter
    def get_ax_number(self, axis):
        if axis.upper() in self.ax_letters:
            axis_number = self.ax_letters.index(axis.upper()) + 1
        else:
            axis_number = 0
        return axis_number

    def setup_motor(self):
        self.command("0Z")
        self.set_position_maintanance(False)
        motor_type = 716  # Read from the profound driver
        stall_current_amps = 2.1
        encoder_resolution = 2000  # steps_rev
        max_rpm = 1000
        thermal_time_constant = 1000
        # todo:set a real value, this one is a guess
        # Thermal time constant – is the time in seconds for the motor to reach
        # two-thirds of its rated temperature while operating at its continuous current
        # rating.
        r_ohms = 2
        l_mhenry = 2
        # command = f"1MOTOR({motor_type},{stall_current_amps},{10000},{max_rpm},{thermal_time_constant}," \
        #            f"{r_ohms},{l_mhenry},{50})"
        command = "1MOTOR(716,1.0,50000,1000,5,2,2)"
        # print(command)
        self.command(command)
        print(self.get_response())

    def setup_motor_1(self):
        self.command('1K')			#Kill any program that is running
        self.command('1CLEAR(ALL)')		#Erase all routines, etc
        self.command('1W(BR,19200)')		#BAUD rate

        self.command('1W(CL,50)')		#Current clamp

        self.command('1W(CQ,1)')		#Command queueing

        self.command('1W(IC,8160)')		#I/O configuration
        self.command('1W(EI,2)')		#Following encoder inputs
        self.command('1W(EO,2)')		#Simulated encoder outputs
        self.command('1LIMITS(0,1,0,200.0)')	#;Travel limits

        #Homing setup
        self.command('1HOME1(+,1,-10.00,10.0,0,0)') #Home setup 1
        self.command('1W(EW,50)') #Error window
        self.command('1W(IT,10)')		#Settling time
        self.command('1GAINS(5.00,0.00,7.00,5.00,0)') #Set gains

        self.command('1W(IM,1)')		#Integral action in window
        self.command('1W(IW,50)')		#Integral window

        self.command('1W(ES,1)')		#Drive enable sense (can over-ride input)'
        self.command('1W(PC,100)')  # Peak current
        self.command('1W(TL,4000)')  # Tracking limit
        #Motor configuration
        self.command('1MOTOR(457,1.2,4000,100,100,3.2,5,312.5)') #Setup







if __name__ == '__main__':
    motors = VIX_Motor_Controller(config=None)
    motors.connect_hardware()
    motors.setup_motor_1()
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
