from PyQt5.QtCore import QMutex, QObject, QThread, QWaitCondition, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QMessageBox
from typing import Optional
from Hardware.hardware_galil import GalilDMC41x3

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging

log_formatter = logging.Formatter(LOGGER_FORMAT)

motor_logger = logging.getLogger('motor_log')

file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
motor_logger.addHandler(file_handler)

motor_logger.setLevel(logging.INFO)

root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class Manager(QThread):
    """
    this class acts as the chief executive for the application. It is in charge of recieving commands from the UI,
    dictating actions to other classes, and emitting feedback back to the UI

    Signals:
        logger_signal: convey info to the user via a feedback widget
        finished_signal: emitted when the thread is ready to be deleted.
    Slots:
        execute_command: execute a command given to the application

    Methods:

    """

    logger_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    sMotorConnection = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject], config: dict):
        super().__init__(parent=parent, objectName=u"manager_thread")
        self.script = None
        self.stay_alive = True

        self.cmd = 'POS'

        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # -> check if we are simulating hardware
        self.SIMULATE_HARDWARE = config['WTF']['Motor']['simulate_hw']

        self.motor = GalilDMC41x3(parent=None, config=config)

    def run(self) -> None:
        """
        Overloaded function from QThread, this is the main scope control thread
        function.
        """
        self.mutex.lock()

        # -> try to connect to the motor
        msg = f"SIMULATE HARDWARE is: {self.SIMULATE_HARDWARE}"
        self.log_msg(level='info', message=msg)

        motor_status = self.motor.connect_motor()
        self.stay_alive = motor_status

        # -> signal the main app whether the motor connection was successful
        self.sMotorConnection.emit(motor_status)

        while self.stay_alive is True:

            # root_logger.info('Waiting in motor thread.')
            # wait_bool = self.condition.wait(self.mutex)
            wait_bool = self.condition.wait(self.mutex)
            # root_logger.info(f"Finished waiting in motor thread. {wait_bool}")

            if self.stay_alive is False:
                break

            self.cmd = self.cmd.upper()
            cmd_ray = self.cmd.split(' ')

            if cmd_ray[0] == 'LOAD':
                self.log_msg('info', message="Loading script")
                try:
                    cmd_ray.pop(0)
                    path = ' '.join(cmd_ray)
                    self.script = open(path, "r")
                except Exception as e:
                    self.log_msg("info", f"Error in load script: {e}")
                self.cmd = ''
            elif cmd_ray[0] == 'RUN':
                self.log_msg('info', message="Running script")
                try:
                    for command in self.script:
                        self.log_msg('info', message=command)
                except Exception as e:
                    self.log_msg("info", f"Error in run script: {e}")

                self.cmd == ''
            else:
                pass

        self.wrap_up()
        self.mutex.unlock()

        return super().run()

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

    @pyqtSlot(str)
    def exec_command(self,command):
        self.cmd = command
        self.condition.wakeAll()

    def wrap_up(self):
        pass

