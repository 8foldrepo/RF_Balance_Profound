from PyQt5.QtCore import *
import logging

from typing import Optional

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import is_number
log_formatter = logging.Formatter(LOGGER_FORMAT)

motor_logger = logging.getLogger('motor_log')

file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
motor_logger.addHandler(file_handler)

motor_logger.setLevel(logging.INFO)

root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class DummyMotors(QThread):
    num_axes = 0
    ax_letters= None

    #not all signals will be used for every application of this class
    x_pos_signal = pyqtSignal(float)
    y_pos_signal = pyqtSignal(float)
    r_pos_signal = pyqtSignal(float)
    z_pos_signal = pyqtSignal(float)

    coords = list()
    speeds = list()
    motors_on = list()
    pos_limits = list()
    neg_limits = list()
    targets = list()

    scanning_signal = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent=parent, objectName="manager_thread")
        self.device_key = 'Dummy_Motors'
        self.stay_alive = True

        self.cmd = 'NONE'

        self.connected = False
        self.scanning = False

        self.jog_speed = 1
        self.scan_speed = 1

        self.mutex = QMutex()
        self.condition = QWaitCondition()

    def set_config(self, config):
        self.config = config
        self.ax_letters = self.config[self.device_key]['axes']

        self.num_axes = len(self.ax_letters)

        for i in range(self.num_axes):
            self.coords.append(0)
            self.speeds.append(0)
            self.motors_on.append(True)
            self.pos_limits.append(50)
            self.neg_limits.append(-50)
            self.targets.append(0)

    def run(self) -> None:
        """
        Overloaded function from QThread, this is the main scope control thread
        function.
        """
        self.mutex.lock()
        self.stay_alive = True

        while self.stay_alive is True:

            # root_logger.info('Waiting in motor thread.')
            # wait_bool = self.condition.wait(self.mutex)
            wait_bool = self.condition.wait(self.mutex, 50)
            # root_logger.info(f"Finished waiting in motor thread. {wait_bool}")

            if self.stay_alive is False:
                break

            self.cmd = self.cmd.upper()
            cmd_ray = self.cmd.split(' ')

            if self.connected:
                if self.cmd == 'Disconnect'.upper():
                    self.connected = False
                elif cmd_ray[0] == 'JOG' and cmd_ray[1] == 'SPEED':
                    self.jog_speed = float(cmd_ray[2])
                    self.log_msg(level = 'info', message=f"Jog Speed Set: {cmd_ray[2]}")
                elif cmd_ray[0] == 'SCAN' and cmd_ray[1] == 'SPEED':
                    self.scan_speed = float(cmd_ray[2])
                    self.log_msg(level = 'info', message=f"Scan Speed Set: {cmd_ray[2]}")

                #Usage: Begin Motion X+ means jog the x axis in the positive direction
                elif cmd_ray[0] == 'BEGIN' and cmd_ray[1] == 'MOTION':
                    ax = cmd_ray[2][0]
                    dir = cmd_ray[2][1]

                    ax_index = self.ax_letters.index(ax)

                    if dir == '-':
                        self.speeds[ax_index] = -1 * self.jog_speed
                    elif dir == '+':
                        self.speeds[ax_index] = 1 * self.jog_speed
                elif self.cmd == 'Stop Motion'.upper():
                    for i in range(self.num_axes):
                        self.speeds[i] = 0
                elif cmd_ray[0] == 'GO':
                    targ_coords = cmd_ray[1].split(',')
                    for i in range(len(targ_coords)):
                        try:
                            if is_number(targ_coords[i]):
                                self.targets[i] = float(targ_coords[i])

                                if self.targets[i] > self.coords[i]:
                                    self.scanning = True
                                    self.speeds[i] = abs(self.scan_speed)
                                elif self.targets[i] < self.coords[i]:
                                    self.scanning = True
                                    self.speeds[i] = -1 * abs(self.scan_speed)

                        except IndexError:
                            self.log_msg(level='Error', message='More coordinates were entered than Axes')

                elif self.cmd == 'Get Position'.upper():
                    if 'X' in self.ax_letters:
                        self.x_pos_signal.emit(self.coords(self.ax_letters.index('X')))
                    if 'Y' in self.ax_letters:
                        self.y_pos_signal.emit(self.coords(self.ax_letters.index('Y')))
                    if 'Z' in self.ax_letters:
                        self.z_pos_signal.emit(self.coords(self.ax_letters.index('Z')))
                    if 'R' in self.ax_letters:
                        self.r_pos_signal.emit(self.coords(self.ax_letters.index('R')))

                elif cmd_ray[0] == 'SET':
                    ax_letter = cmd_ray[1]
                    ax_index = self.ax_letters.index(ax_letter)
                    self.coords[ax_index] = float(cmd_ray[2])
                    self.cmd = 'Get Position'

            else:
                if self.cmd == 'Connect'.upper():
                    self.connected = True

            self.cmd = ""

            if self.scanning:
                for i in range(self.num_axes):
                    if (self.targets[i] - self.coords[i]) * self.speeds[i] <= 0:
                        self.speeds[i] = 0

                if self.not_moving():
                    self.scanning = False
                    self.scanning_signal.emit(False)

            for i in range(self.num_axes):
                if self.motors_on[i]:
                    self.coords[i] = self.coords[i] + self.speeds[i]


        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    @pyqtSlot(str)
    def command_received(self, command):
        self.cmd = command
        #self.condition.wakeAll()
        self.log_msg(level='Info', message=command)

    def not_moving(self):
        for speed in self.speeds:
            if not speed == 0:
                return False

        return True

    def log_msg(self, level: str, message: str) -> None:
        """
        Convenience function to log messages in a compact way with useful info.

            Parameters:
                level (str): A string indicating the logger level, can be either
                'info', 'debug' or 'error'
                message (str): A string that contains the message to be logged

            Returns:
                None
        """
        thread_name = QThread.currentThread().objectName()
        log_entry = f"[{type(self).__name__}] [{thread_name}] : {message}"
        if level == 'debug':
            root_logger.debug(log_entry)
            motor_logger.debug(log_entry)
        elif level == 'error':
            root_logger.error(log_entry)
            motor_logger.error(log_entry)
        elif level == 'warning':
            root_logger.warning(log_entry)
            motor_logger.warning(log_entry)
        else:
            root_logger.info(log_entry)
            motor_logger.info(log_entry)