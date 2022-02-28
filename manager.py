from PyQt5.QtCore import QMutex, QObject, QThread, QWaitCondition, Qt, pyqtSignal, pyqtSlot
from typing import Optional
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import distutils.util
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
from Hardware.abstract_oscilloscope import AbstractOscilloscope

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
        self.parent = parent

        self.script = None
        self.stay_alive = True

        self.config = config
        self.devices = list()

        self.scripting = False

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
                self.log_msg(level='info', message="Loading script")
                try:
                    cmd_ray.pop(0)
                    path = ' '.join(cmd_ray)
                    self.load_script(path)
                except Exception as e:
                    self.log_msg("info", f"Error in load script: {e}")
                self.cmd = ''
            elif cmd_ray[0] == 'RUN':
                self.log_msg(level='info', message="Running script")
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

            if not self.scripting:
                self.Motors.get_position()
                self.thermocouple.get_reading()
                time,voltage = self.Oscilloscope.capture()
                #The plot exists in the parent MainWindow Class, but has been moved to this Qthread
                if self.parent.plot_ready:
                    self.parent.waveform_plot.plot(time, voltage, pen='k', clear=True)
                else:
                    self.log_msg("Plot blocked")

            self.cmd = ""

        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    def load_script(self, path):
        self.scripting = True

        self.script = open(path, "r")

        # Send name of script to UI
        split_path = path.split('/')
        name = split_path[len(split_path)-1]
        self.script_name_signal.emit(name)

        tasks = []  # the upper layer of our variable list
        loops = []
        taskExecOrder = []
        elementNamesForLoop = []
        taskNoForLoop = []
        currentLine = -1
        addingElementsToLoop = False
        buildingLoop = False
        taskVars = dict()  # the list of variables for the individual task
        taskNo = -2  # keeps track of the task number for indexing
        f = open(path, "r")
        for line in self.script:
            ray = line.split(' = ')

            if ray[0].upper() == '# OF TASKS':
                self.num_tasks_signal.emit(int(ray[1].replace('"', "")))
            elif ray[0].upper() == 'CREATEDON':
                self.created_on_signal.emit(ray[1].replace('"', ""))
            if ray[0].upper() == 'CREATEDBY':
                self.created_by_signal.emit(ray[1].replace('"', ""))
            elif ray[0].upper() == 'DESCRIPTION':
                self.description_signal.emit(ray[1].replace('"', ""))

            currentLine = currentLine + 1
            if line == '\n':
                if taskVars:  # ensures task variable list isn't empty; prevents adding empty sub lists to main list
                    tasks.append(dict(taskVars))
                    taskVars.clear()  # empties out variable list for task since we're ready to move to the next set
                if addingElementsToLoop:  # detects if we're done with the element name block for the loop in script
                    addingElementsToLoop = False  # we're done with the block so set the flag to false
                continue  # move forward one line
            elif '[' in line:  # if the line we're on is a task line
                taskNo = taskNo + 1  # increments the task number counter since we've moved to the next task
                if "Task" in line and not buildingLoop:
                    taskExecOrder.append(taskNo)  # adding task number to the execution list
            else:  # above ensures we're not parsing a task header nor blank line
                x = (line.split('='))  # all other lines are variable assignment lines, no need to check for '='
                x0 = x[0].strip()  # remove trailing/leading spaces
                x1 = x[1].strip().replace('"', "")  # does above but also removes quotation marks
                taskVars[x0] = x1  # add the temporary variable pair to the task's variable list

                if "# of Tasks" in x0:
                    numberOfTasks = x1

                if "Loop over elements" in x1:  # detects if we've encountered a loop builder task
                    buildingLoop = True  # set a flag that we're building a loop for the script
                    addingElementsToLoop = True  # set a flag that we're adding element names from script for loop

                if addingElementsToLoop and "Element" in x0:  # if we're on a line that adds an element name for the loop
                    elementNamePre = x0.split(' ')  # split the left side of the variable assigner by space
                    elementName = elementNamePre[
                        1]  # retrieve the second word of the left side, that's the element name
                    elementNamesForLoop.append(int(elementName))

                if "End loop" in x1:  # script will have "End loop" in right side of task type to end loop block
                    buildingLoop = False  # set the building loop flag to false since the loop block is done
                    loops.append(list([list(elementNamesForLoop), list(taskNoForLoop)]))
                    elementNamesForLoop.clear()
                    taskNoForLoop.clear()
                    taskExecOrder.pop()

                    for i in range(len(loops[len(loops) - 1][0])):
                        for j in range(len(loops[len(loops) - 1][1])):
                            taskExecOrder.append([loops[len(loops) - 1][1][j], i + 1])

                if buildingLoop and not addingElementsToLoop:  # if we're building a loop & are not in the name adding phase
                    if taskNo not in taskNoForLoop:  # ensure the task no. isn't already in the task list for the loop
                        taskNoForLoop.append(
                            taskNo)  # add the current task no. to the list of tasks we need to run in loop

        if taskVars:  # ensures task variable list isn't empty; prevents adding empty sub lists to main list
            tasks.append(dict(taskVars))
            taskVars.clear()  # empties out variable list for task since we're ready to move to the next set

        for i in range(len(taskExecOrder)):
            if not isinstance(taskExecOrder[i], list):
                taskNoRemember = taskExecOrder[i]
                toReplace = [taskNoRemember, None]
                taskExecOrder[i] = toReplace

        taskNames = list()
        for i in range(len(taskExecOrder)):
            taskNames.append(tasks[taskExecOrder[i][0] + 1]['Task type'])

        taskArgs = list()
        for i in range(len(taskExecOrder)):
            #tasks[taskExecOrder[i][0] + 1].pop("Task type", None)
            taskArgs.append(tasks[taskExecOrder[i][0] + 1])

        for i in range(len(taskNames)):
            name = taskNames[i]
            args = taskArgs[i]

            if not taskExecOrder[i][1] is None:  # if the element in the taskExecOrder isn't None
                args['Element'] = taskExecOrder[i][1]  # set the element to be operated on to the one in taskExecOrder

            if "Measure element efficiency (RFB)".upper() in name.upper():
                self.measure_element_efficiency_rfb(args)
            elif name.upper() == "Pre-test initialization".upper():
                pretest_initialization(args)
            elif "Find element n".upper() in name.upper():
                self.find_element(args)
            elif name.upper() == "Save results".upper():
                self.save_results(args)
            elif name.upper() == "Prompt user for action".upper():
                self.prompt_user_for_action(args)
            elif "Home system".upper() in name.upper():
                self.home_system(args)
        print(tasks)
        self.script_info_signal.emit(tasks)

        self.scripting = False

    def run_script(self):
        self.scripting = True

        for command in self.script:
            command = command.upper()
            self.log_msg(level='info', message=command)
            if '[TASK' in command:
                step_number = int(command.replace('[TASK', '').replace(']', ''))
                self.step_number_signal.emit(step_number)

        self.scripting = False

    def measure_element_efficiency_rfb(self, varlist):
        element = varlist['Element']
        freqRange = varlist['Frequency range']
        on_off_cycles = varlist['RFB.#on/off cycles']
        return

    def pretest_initialization(self, varlist):
        return

    def find_element(self, varlist):
        element = varlist['Element']
        xIncrMM = varlist['X Incr. (mm)']
        XPts = varlist['X #Pts.']
        thetaIncrDeg = varlist['Theta Incr. (deg)']
        thetaPts = varlist['Theta #Pts.']
        scopeChannel = varlist['Scope channel']
        AcquisitionType = varlist['Acquisition type']
        averages = varlist['Averages']
        dataStorage = varlist['Data storage']
        storageLocation = varlist['Storage location']
        dataDirectory = varlist["Data directory"]
        maxPosErrMM = varlist["Max. position error (+/- mm)"]
        elemPosTest = varlist["ElementPositionTest"]
        return

    def save_results(self, varlist):
        saveSummaryFile = bool(distutils.util.strtobool(varlist["Save summary file"]))
        WriteUACalibration = bool(distutils.util.strtobool(varlist["Write UA Calibration"]))
        PromptForCalWrite = bool(distutils.util.strtobool(varlist["PromptForCalWrite"]))
        return

    def prompt_user_for_action(self, varlist):
        promptType = varlist["Prompt type"]
        return

    def home_system(self, varlist):
        axisToHome = varlist['Axis to home']
        return

    def printList(self, list2):
        for x in range(len(list2)):
            print(list2[x])

    def printList2(self, list2):
        print(str(list2)[1:-1])

    def log_msg(self, message: str,level: str='info') -> None:
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
