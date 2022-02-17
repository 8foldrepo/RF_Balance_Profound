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
    num_axes = 2
    #Must be capital
    ax_letters= ['X','R']
    coords = list()
    speeds = list()
    motors_on = list()
    pos_limits = list()
    neg_limits = list()
    targets = list()
    pos_signals = list()

    for i in range(num_axes):
        coords.append(0)
        speeds.append(0)
        motors_on.append(True)
        pos_limits.append(50)
        neg_limits.append(-50)
        targets.append(0)
        pos_signals.append(pyqtSignal)

    scanning_signal = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent=parent, objectName="manager_thread")

        self.stay_alive = True

        self.cmd = 'NONE'

        self.connected = False

        self.scanning = False

        self.jog_speed = 1
        self.scan_speed = 1

        self.mutex = QMutex()
        self.condition = QWaitCondition()

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
                    coords = cmd_ray[1].split(',')
                    for i in range(len(coords)):
                        try:
                            if is_number(coords[i]):
                                self.targets[i] = float(coords[i])
                        except IndexError:
                            self.log_msg(level='Error', message='More coordinates were entered than Axes')

                elif cmd_ray[0] == 'BG':
                    axes = cmd_ray[1]
                    self.scanning = True
                    self.scanning_signal.emit(True)
                    for axis in axes:
                        try:
                            ax_index = self.ax_letters.index(axis)
                        except ValueError:
                            self.log_msg(level='Error', message='Invalid axis identifier in Begin Motion')
                        if self.targets[ax_index] > self.coords[ax_index]:
                            self.speeds[ax_index] = abs(self.scan_speed)
                        elif self.targets[ax_index] < self.coords[ax_index]:
                            self.speeds[ax_index] = -1 * abs(self.scan_speed)

                elif self.cmd == 'Get Position'.upper():
                    for i in range(self.num_axes):
                        self.pos_signals[i].emit(coords[i])

                elif cmd_ray[0] == 'SET':
                    ax_letter = cmd_ray[1]
                    ax_index = self.ax_letters.index(ax_letter)
                    self.coords[ax_index] = float(self.cmd_ray(2))

            else:
                if self.cmd == 'Connect'.upper():
                    self.connected = True

            self.cmd = ""

            if self.scanning:
                for i in range(self.num_axes):
                    print((self.targets[i] - self.coords[i]) * self.speeds[i])

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
        self.condition.wakeAll()
        self.log_msg(level='Info', message=command)

    def not_moving(self):
        for speed in self.speeds:
            if not speed == 0:
                return True

        return False

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