from datetime import date

import pyvisa
from PyQt5.QtCore import QMutex, QObject, QThread, QWaitCondition, pyqtSignal, pyqtSlot
from typing import Optional
import distutils.util

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging

log_formatter = logging.Formatter(LOGGER_FORMAT)

import time as t

from Utilities.useful_methods import log_msg
import os
from definitions import ROOT_DIR

balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
from Hardware.Abstract.abstract_sensor import AbstractSensor
from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope
from Hardware.MT_balance import MT_balance
from Hardware.keysight_oscilloscope import KeysightOscilloscope
from Hardware.relay_board import Relay_Board
from Hardware.keysight_awg import KeysightAWG
from Hardware.water_level_sensor import  WaterLevelSensor

pump_status = ""
tank_status = ""


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
    # Dialog signals
    pretest_dialog_signal = pyqtSignal(str)  # str is date (man -> mainwindow)
    user_prompt_signal = pyqtSignal(str)  # str is message for user to read
    user_prompt_pump_not_running_signal = pyqtSignal(str)  # str is pump status
    user_prompt_signal_water_too_low_signal = pyqtSignal(str)  # str is water level
    write_cal_data_to_ua_signal = pyqtSignal(list)  # list is 2d array of calibration data
    retracting_ua_warning_signal = pyqtSignal()

    # Script metadata
    description_signal = pyqtSignal(str)
    created_on_signal = pyqtSignal(str)
    created_by_signal = pyqtSignal(str)
    num_tasks_signal = pyqtSignal(int)
    script_name_signal = pyqtSignal(str)

    # Compartmentalize into motor interface thread later
    MotorCommands = pyqtSignal(str)

    step_number_signal = pyqtSignal(int)

    script_info_signal = pyqtSignal(list)

    plot_signal = pyqtSignal(object, object)
    refresh_rate_signal = pyqtSignal(float)

    logger_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    Motors = None

    script_highlight_signal = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject], config: dict):
        super().__init__(parent=parent, objectName=u"manager_thread")

        self.water_level_good = None  # boolean variable to see if the water is level in the tank
        self.test_comment = None
        self.ua_serial_number = None
        self.operator_name = None
        
        self.step_complete = True
        self.step_index = -1

        self.abort_var = False  # keep track of whether user has aborted script process, default false
        self.retry_var = False  # keep track of whether user wants to try script iteration, default false

        self.parent = parent

        self.taskArgs = None
        self.taskExecOrder = None
        self.taskArgs = None

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

        self.rm = pyvisa.ResourceManager()

        self.Balance = MT_balance(config=self.config)
        self.Pump = Relay_Board(config=self.config, device_key='Pump')
        self.AWG = KeysightAWG(config=self.config, resource_manager=self.rm)
        self.Water_Level_Sensor = WaterLevelSensor(config=self.config)

        self.devices.append(self.Pump)
        self.devices.append(self.Balance)
        self.devices.append(self.AWG)

        if self.SIMULATE_HARDWARE:
            self.Motors = AbstractMotorController(config=self.config)
            self.thermocouple = AbstractSensor(config=self.config)
            self.Oscilloscope = AbstractOscilloscope()
            self.devices.append(self.Motors)
            self.devices.append(self.thermocouple)
        else:
            self.Oscilloscope = KeysightOscilloscope(config=self.config, resource_manager=self.rm)

        self.devices.append(self.Oscilloscope)

    def connect_hardware(self):
        for device in self.devices:
            device.connect_hardware()

    def disconnect_hardware(self):
        for device in self.devices:
            device.disconnect_hardware()

    def run(self) -> None:
        """
        Overloaded function from QThread, this is the main scope control thread
        function.
        """
        self.mutex.lock()
        start_time = t.time()
        # -> try to connect to the motor
        msg = f"SIMULATE HARDWARE is: {self.SIMULATE_HARDWARE}"
        log_msg(self, root_logger, level='info', message=msg)

        self.stay_alive = True

        while self.stay_alive is True:
            # root_logger.info('Waiting in motor thread.')
            # wait_bool = self.condition.wait(self.mutex)
            wait_bool = self.condition.wait(self.mutex, 5)
            # root_logger.info(f"Finished waiting in motor thread. {wait_bool}")

            if self.stay_alive is False:
                break

            self.cmd = self.cmd.upper()
            cmd_ray = self.cmd.split(' ')
            if cmd_ray[0] == 'LOAD':
                log_msg(self, root_logger, level='info', message="Loading script")
                try:
                    cmd_ray.pop(0)
                    path = ' '.join(cmd_ray)
                    self.load_script(path)
                except Exception as e:
                    log_msg(self, root_logger, "info", f"Error in load script: {e}")
                self.cmd = ''
            elif cmd_ray[0] == 'RUN':
                log_msg(self, root_logger, level='info', message="Running script")
                self.abort_var = False  # when we run a new script, this variable should be false
                self.scripting = True   # set variables that will trigger the execution of the script in the main loop
            elif cmd_ray[0] == 'CLOSE':
                print("wrapping up")
                self.wrap_up()
            elif cmd_ray[0] == 'CONNECT':
                self.connect_hardware()
            elif cmd_ray[0] == 'MOTOR':
                self.Motors.exec_command(self.cmd)
            # What to do when there is no command
            else:
                pass

            if self.retry_var is True:
                self.step_index = self.step_index - 1
                self.step_complete = True
                self.retry_var = False  # sets the retry variable to false so the retry function can happen again

            #advance to the next step if the previous has been completed
            if self.scripting and self.step_complete:
                self.step_index = self.step_index + 1

            #if a script is being executed, and the step index is valid, and the previous step is complete,
            #run the next script step
            if self.scripting and 0 <= self.step_index < len(self.taskNames):
                if  self.step_complete:
                    self.step_complete = False
                    self.execute_script_step(self.step_index)
            else:
                #Do these things if a script is not being run
                self.Motors.get_position()
                self.thermocouple.get_reading()

                if self.parent.plot_ready and self.parent.tabWidget.currentIndex() == 5:
                    # The plot exists in the parent MainWindow Class, but has been moved to this Qthread
                    try:
                        time, voltage = self.Oscilloscope.capture(channel=1)
                        time_elapsed = t.time() - start_time
                        if time_elapsed != 0:
                            self.refresh_rate_signal.emit(round(1 / (time_elapsed), 1))

                        self.plot_signal.emit(time, voltage)
                        start_time = t.time()
                    except pyvisa.errors.InvalidSession:
                        self.log("Could not plot, oscilloscope resource closed")

            self.cmd = ""

        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    def load_script(self, path):
        self.scripting = True

        self.script = open(path, "r")

        # Send name of script to UI
        split_path = path.split('/')
        name = split_path[len(split_path) - 1]
        self.script_name_signal.emit(name)

        tasks = []  # the upper layer of our variable list
        loops = []
        self.taskExecOrder = []
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
                    self.taskExecOrder.append(taskNo)  # adding task number to the execution list
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
                    self.taskExecOrder.pop()

                    for i in range(len(loops[len(loops) - 1][0])):
                        for j in range(len(loops[len(loops) - 1][1])):
                            self.taskExecOrder.append([loops[len(loops) - 1][1][j], i + 1])

                if buildingLoop and not addingElementsToLoop:  # if we're building a loop & are not in the name adding phase
                    if taskNo not in taskNoForLoop:  # ensure the task no. isn't already in the task list for the loop
                        taskNoForLoop.append(
                            taskNo)  # add the current task no. to the list of tasks we need to run in loop

        if taskVars:  # ensures task variable list isn't empty; prevents adding empty sub lists to main list
            tasks.append(dict(taskVars))
            taskVars.clear()  # empties out variable list for task since we're ready to move to the next set

        for i in range(len(self.taskExecOrder)):
            if not isinstance(self.taskExecOrder[i], list):
                taskNoRemember = self.taskExecOrder[i]
                toReplace = [taskNoRemember, None]
                self.taskExecOrder[i] = toReplace

        self.taskNames = list()
        for i in range(len(self.taskExecOrder)):
            self.taskNames.append(tasks[self.taskExecOrder[i][0] + 1]['Task type'])

        self.taskArgs = list()
        for i in range(len(self.taskExecOrder)):
            # tasks[self.taskExecOrder[i][0] + 1].pop("Task type", None)
            self.taskArgs.append(tasks[self.taskExecOrder[i][0] + 1])

        self.script_info_signal.emit(tasks)

        self.scripting = False

    def execute_script_step(self, step_index):

        if self.taskArgs is None or self.taskArgs is None or self.taskExecOrder is None:
            self.scripting = False
            return

        if self.abort_var is True:  # checks to see if the abort variable is true
            self.scripting = False
            # exits the tasks loop, the user has aborted the script

        name = self.taskNames[step_index]  # sets name (str) to current iteration in taskNames list
        args = self.taskArgs[step_index]  # sets args (list) to current iteration in taskArgs list

        if not self.taskExecOrder[step_index][1] is None:  # if the element in the self.taskExecOrder isn't None
            # below: set the element to be operated on to the one in self.taskExecOrder
            args['Element'] = self.taskExecOrder[step_index][1]

        if "Measure element efficiency (RFB)".upper() in name.upper():
            self.measure_element_efficiency_rfb(args)
            self.script_highlight_signal(name)
        elif name.upper() == "Pre-test initialisation".upper():
            self.pretest_initialization(args)
            self.script_highlight_signal(name)
        elif "Find element n".upper() in name.upper():
            self.find_element(args)
            self.script_highlight_signal(name)
        elif name.upper() == "Save results".upper():
            self.save_results(args)
            self.script_highlight_signal(name)
        elif name.upper() == "Prompt user for action".upper():
            self.prompt_user_for_action(args)
            self.script_highlight_signal(name)
        elif "Home system".upper() in name.upper():
            self.home_system(args)
            self.script_highlight_signal(name)

        self.step_number_signal.emit(self.taskExecOrder[step_index][0] + 1)

        # below: this should allow for the retry function by setting the iteration variable backwards 1
        # so when it gets incremented it returns to the previous position

    def abort(self):
        self.abort_var = True  # sets the abort variable to true if this method is called
        return

    def retry(self):
        self.retry_var = True
        return

    def cont(self):
        self.step_complete = True  # sets the continue variable to true so script know to continue
        return

    def write_cal_data_to_ua_button(self):
        # Todo: make this method write calibration data to UA
        self.step_complete = True  # this statement should run after writing calibration data to UA
        pass

    def measure_element_efficiency_rfb(self, variable_list):
        element = variable_list['Element']
        frequency_range = variable_list['Frequency range']
        on_off_cycles = variable_list['RFB.#on/off cycles']
        return

    def pretest_initialization(self, variable_list):
        today = date.today()
        formatted_date = today.strftime("%m/%d/%Y")

        self.pretest_dialog_signal.emit(formatted_date)  # sends signal from manager to MainWindow to open dialog box

    @pyqtSlot(str,str,str)  # latches info from user in MainWindow to manager local vars
    def pretest_info_slot(self, operator_name, ua_serial_no, comment):
        self.operator_name = operator_name
        self.ua_serial_number = ua_serial_no
        self.test_comment = comment

        if self.Pump.get_reading() and self.Water_Level_Sensor.get_reading() == 'level':  # if the ua pump is running and the water level is good
            self.step_complete = True  # continue to the next step via setting bool var to true
        else:
            if not self.Pump.get_reading():  # if the pump is not running
                self.user_prompt_pump_not_running()  # launch the dialog box signifying this issue
            if not self.Water_Level_Sensor.get_reading() == 'level':  # if the water level is not good
                self.user_prompt_water_too_low()  # launch the dialog box signifying this issue

        return  # at this point this step is done, and we can return from the method

    def user_prompt_pump_not_running(self):  # this dialog box has a "continue" and an "abort" button
        self.user_prompt_pump_not_running_signal.emit(pump_status)

        if self.step_complete:  # if user clicks continue
            if not self.Pump.get_reading():  # but the issue has not been resolved
                self.step_complete = False  # set the step complete variable to false
                # below: relaunch this method, window will relaunch and will close recursively
                self.user_prompt_pump_not_running()
            else:  # however, if the issue has been solved
                return  # leave the method

        return  # will return from root and recursively called instance of this method

    def user_prompt_water_too_low(self):  # this dialog box has a "continue" and an "abort" button
        self.user_prompt_signal_water_too_low_signal.emit(self.Water_Level_Sensor.get_reading())

        if self.step_complete:  # if user clicks continue
            if self.water_level != "level":  # but the issue has not been resolved
                self.step_complete = False  # set the step complete variable to false
                # below: relaunch this method, window will relaunch and will close recursively
                self.user_prompt_water_too_low()
            else:  # however, if the issue has been solved
                return  # leave the method

        return  # will return from root and recursively called instance of this method

    def user_prompt(self, message):  # message var is message user should see when dialog box opens
        self.user_prompt_signal.emit(message)  # passes message var to be carried by signal

        if self.step_complete:  # if the user selects the continue button
            return  # leave this method

        elif self.abort_var:  # if the user has selected the abort button
            return  # leave this method, the "execute script" method will handle aborting the script
        
        elif self.retry_var:  # if the user selects the retry button
            return  # leave this method, the "execute script" method will handle retrying the current step


    def retract_ua_warning(self):
        self.retracting_ua_warning_signal.emit()

        if self.step_complete:  # the user has clicked the continue button
            return  # leave the method, the step_complete var will remain true

        elif self.abort_var:  # the user has clicked the abort button
            return  # leave the method, the "execute script" method will handle abandoning the script

    def find_element(self, variable_list):
        element = variable_list['Element']
        x_increment_MM = variable_list['X Incr. (mm)']
        XPts = variable_list['X #Pts.']
        thetaIncrDeg = variable_list['Theta Incr. (deg)']
        thetaPts = variable_list['Theta #Pts.']
        scope_channel = variable_list['Scope channel']
        acquisition_type = variable_list['Acquisition type']
        averages = variable_list['Averages']
        data_storage = variable_list['Data storage']
        storage_location = variable_list['Storage location']
        data_directory = variable_list["Data directory"]
        maxPosErrMM = variable_list["Max. position error (+/- mm)"]
        elemPosTest = variable_list["ElementPositionTest"]
        return

    def save_results(self, variable_list, calibration_data):  # calibration_data is the data gathered by the UA test
        save_summary_file = bool(distutils.util.strtobool(variable_list["Save summary file"]))
        write_uac_calibration = bool(distutils.util.strtobool(variable_list["Write UA Calibration"]))
        prompt_for_calibration_write = bool(distutils.util.strtobool(variable_list["prompt_for_calibration_write"]))

        if prompt_for_calibration_write:  # displays the "write to UA" dialog box if this variable is true
            self.write_cal_data_to_ua_dialog(calibration_data)

        return

    def prompt_user_for_action(self, variable_list):
        prompt_type = variable_list["Prompt type"]
        return

    def home_system(self, variable_list):
        axis_to_home = variable_list['Axis to home']
        if axis_to_home == 'X':
            self.retracting_ua_warning_signal.emit()  # launch the retracting UA in the x direction warning box

        if self.step_complete:  # if the user clicks the continue button in the warning box
            self.step_complete = False  # set the variable back to false in order to signify when movement is done
            pass  # TODO: have the pump home in the desired direction
            self.step_complete = True  # movement is done, this step has been completed

        elif self.abort_var:  # if the user click the abort button in the dialog box
            return  # leave this method, the "execute script" method will handle abandoning the currently running script

        return

    # calibration_data should be a 2d list: 1st col: cal data array, 2nd col: low freq, 3rd col: high freq
    def write_cal_data_to_ua_dialog(self, calibration_data):
        self.write_cal_data_to_ua_signal.emit(calibration_data)

        if self.step_complete:  # if the user presses the "write to UA" button in the dialog box
            return  # we already did the code logic to write the calibration data to the ua, so just continue

        elif self.abort_var:  # if the user click the abort button in the dialog box
            return  # leave this method, the "execute script" method will handle abandoning the currently running script
    
    def printList(self, list2):
        for x in range(len(list2)):
            print(list2[x])


    def printList2(self, list2):
        print(str(list2)[1:-1])

    @pyqtSlot(str)
    def exec_command(self, command):
        if 'CLOSE' in command.upper():
            self.log('Wrapping up')
            self.wrap_up()
            return
        self.cmd = command
        self.condition.wakeAll()

    def wrap_up(self):
        for device in self.devices:
            device.wrap_up()
        self.stay_alive = False

    def log(self, message, level='info'):
        log_msg(self, root_logger=root_logger, message=message, level=level)
