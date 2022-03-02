from PyQt5.QtCore import QMutex, QObject, QThread, QWaitCondition, Qt, pyqtSignal, pyqtSlot
from typing import Optional
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Hardware.abstract_oscilloscope import AbstractOscilloscope
import logging

log_formatter = logging.Formatter(LOGGER_FORMAT)

motor_logger = logging.getLogger('motor_log')

file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
motor_logger.addHandler(file_handler)

motor_logger.setLevel(logging.INFO)

root_logger = logging.getLogger(ROOT_LOGGER_NAME)

from Hardware.abstract_motor_controller import AbstractMotorController
from Hardware.abstract_sensor import AbstractSensor
from Hardware.MT_balance import MT_balance

class Manager(QThread):
    """
    this class acts as the chief executive for the application. It is in charge of recieving commands from the UI,
    dictating actions to other classes, and emitting feedback back to the UI

    Signals:
        logger_signal: convey info to the user via a feedback widget
        finished_signal: emitted when the thread is ready to be deleted.

        description_signal = pyqtSignal(str): Convey script metadata to UI
        created_on_signal = pyqtSignal(str): Convey script metadata to UI
        num_tasks_signal = pyqtSignal(str): Convey script metadata to UI

    Slots:
        execute_command: execute a command given to the application

    Methods:

    """
    #Script metadata
    description_signal = pyqtSignal(str)
    created_on_signal = pyqtSignal(str)
    created_by_signal = pyqtSignal(str)
    num_tasks_signal = pyqtSignal(int)
    script_name_signal = pyqtSignal(str)

    #Compartmentalize into motor interface thread later
    MotorCommands = pyqtSignal(str)

    step_number_signal = pyqtSignal(int)

    script_info_signal = pyqtSignal(list)

    plot_signal = pyqtSignal(object,object)

    logger_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    Motors = None

    def __init__(self, parent: Optional[QObject], config: dict):
        super().__init__(parent=parent, objectName=u"manager_thread")

        self.script = None
        self.stay_alive = True

        self.config = config
        self.devices = list()

        self.cmd = 'POS'

        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # -> check if we are simulating hardware
        self.SIMULATE_HARDWARE = config['Debugging']['simulate_hw']

        if self.SIMULATE_HARDWARE:
            self.Motors = AbstractMotorController(config=self.config)
            self.thermocouple = AbstractSensor(config=self.config)
            self.balance = MT_balance(config=self.config)
            self.Oscilloscope = AbstractOscilloscope(config=self.config)
            self.Oscilloscope.connect()
            self.devices.append(self.Oscilloscope)
            self.devices.append(self.Motors)
            self.devices.append(self.thermocouple)
            self.devices.append(self.balance)

    def connect_hardware(self):
        for device in self.devices:
            device.connect()

    def disconnect_hardware(self):
        for device in self.devices:
            device.disconnect()



    def run(self) -> None:
        """
        Overloaded function from QThread, this is the main scope control thread
        function.
        """
        self.mutex.lock()

        # -> try to connect to the motor
        msg = f"SIMULATE HARDWARE is: {self.SIMULATE_HARDWARE}"
        self.log_msg(level='info', message=msg)

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
            if cmd_ray[0] == 'LOAD':
                self.log_msg('info', message="Loading script")
                try:
                    cmd_ray.pop(0)
                    path = ' '.join(cmd_ray)
                    self.load_script(path)
                except Exception as e:
                    self.log_msg("info", f"Error in load script: {e}")
                self.cmd = ''
            elif cmd_ray[0] == 'RUN':
                self.log_msg('info', message="Running script")
                try:
                    self.run_script()
                except Exception as e:
                    self.log_msg("info", f"Error in run script: {e}")

                self.cmd == ''
            elif cmd_ray[0] == 'CLOSE':
                self.stay_alive = False
                break
            elif cmd_ray[0] == 'CONNECT':
                self.connect_hardware()
            elif cmd_ray[0] == 'MOTOR':
                self.Motors.exec_command(self.cmd)
            #What to do when there is no command
            else:
                pass

            self.Motors.get_position()

            self.thermocouple.get_reading()
            time,voltage = self.Oscilloscope.capture()
            self.plot_signal.emit(time,voltage)
            self.cmd = ""

        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    def load_script(self, path):
        self.script = open(path, "r")

        # Send name of script to UI
        split_path = path.split('/')
        name = split_path[len(split_path)-1]
        self.script_name_signal.emit(name)

        # Load the top level metadata and emit it to the UI
        for line in self.script:
            line = line.upper()
            # If an empty line is detected that means the end of the metadata is reached.
            print(line)
            if line == '\n' or line == '[TASK0]':
                break

            ray = line.split(' = ')

            if ray[0] == '# OF TASKS':
                self.num_tasks_signal.emit(int(ray[1].replace('"', "")))
            elif ray[0] == 'CREATEDON':
                self.created_on_signal.emit(ray[1].replace('"', ""))
            if ray[0] == 'CREATEDBY':
                self.created_by_signal.emit(ray[1].replace('"', ""))
            elif ray[0] == 'DESCRIPTION':
                self.description_signal.emit(ray[1].replace('"', ""))

        self.script_info_signal.emit(
            [{"Task type": "Task 1", "Arg 1": 5, "Arg 2": "banana"}, {"Task type": "Task 2", "Arg 3": 12}])

    def run_script(self):
        for command in self.script:
            command = command.upper()
            self.log_msg('info', message=command)
            if '[TASK' in command:
                step_number = int(command.replace('[TASK', '').replace(']', ''))
                self.step_number_signal.emit(step_number)

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
    def exec_command(self, command):
        self.cmd = command
        self.condition.wakeAll()

    def wrap_up(self):
        pass
