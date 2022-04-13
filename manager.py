import sys

import re
import pyvisa
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutex, QObject, QThread, QWaitCondition, pyqtSignal, pyqtSlot
from typing import Optional
from collections import OrderedDict
import distutils.util

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging

log_formatter = logging.Formatter(LOGGER_FORMAT)

import time as t
import numpy as np
from scipy import integrate

from Utilities.useful_methods import log_msg, get_element_distances, get_awg_on_values, blank_test_data
from Utilities.formulas import calculate_power_from_balance_reading
from definitions import ROOT_DIR
import os

balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

pump_status = ""
tank_status = ""


# todo: continue adding prebuilt methods for all of the actions in script editor
class Manager(QThread):
    # Dialog signals
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

    # Emits the number of the task as shown in the .wtf file, not including repeats. Pretest_initialization should be 0
    task_number_signal = pyqtSignal(int)
    # Tracks the index of the task in the order it is executed, including repeats. Pretest_initialization should be 0
    task_index_signal = pyqtSignal(int)

    element_number_signal = pyqtSignal(str)
    script_info_signal = pyqtSignal(list)

    plot_signal = pyqtSignal(object, object)

    logger_signal = pyqtSignal(str)
    enable_ui_signal = pyqtSignal()

    # Tab signal
    profile_plot_signal = pyqtSignal(list, list, str)
    plot_signal = pyqtSignal(list, list, float)  # float is refresh rate

    rfb_args = dict()  # contains info for rfb tab
    update_rfb_tab_signal = pyqtSignal()
    save_results_signal = pyqtSignal(dict)
    # contains

    Motors = None

    def __init__(self, parent: Optional[QObject], config: dict):
        super().__init__(parent=parent, objectName=u"manager_thread")
        self.get_position_cooldown_s = .2  # decreasing this improves the refresh rate of the position, at the cost of responsiveness
        self.last_get_position_time = 0
        self.app = QApplication.instance()
        self.scan_data = dict()
        self.scan_data["script_log"] = list()

        self.scriptlog = self.scan_data["script_log"]

        self.config = config
        self.element_x_coordinates = get_element_distances(
            element_1_index=self.config['WTF_PositionParameters']['X-Element1'],
            element_pitch=self.config['WTF_PositionParameters']['X-Element pitch (mm)'])

        # put a none at position zero because there is no element zero
        self.element_r_coordinates = [None]
        # fill in default theta home coordinates
        for i in range(10):
            self.element_r_coordinates.append(self.config['WTF_PositionParameters']['ThetaHomeCoord'])

        # Used to prevent other threads from accessing the motor class
        self.motor_control_lock = QMutex()

        # Set test_data to default values
        self.test_data = blank_test_data()

        self.freq_highlimit_hz = None
        self.freq_lowlimit_hz = None
        self.parent = parent
        self.stay_alive = True

        # Stores latest command to be executed in the event loop
        self.cmd = ''

        # Event loop control vars
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # Script file
        self.script = None

        # Script data
        self.taskArgs = None
        self.taskExecOrder = None
        self.taskNames = None

        # Script control vars
        self.scripting = False
        self.continue_var = True
        self.retry_var = False  # keep track of whether user wants to try script iteration, default false

        # Keeps track of script step in progress
        self.step_complete = True

        #step_index = -1 if no script is being run. It is also the way to check if the script has been aborted
        self.step_index = -1

        self.devices = list()
        self.add_devices()

    def test_code(self):
        # # todo: test code, remove later
        # self.scripting = True
        #
        #
        variable_list = dict()
        # variable_list["Task type"] = "Find element \"n\""
        # variable_list["Element"] = "Element 1"
        # variable_list["X Incr. (mm)"] = "0.250000"
        # variable_list["X #Pts."] = "21"
        # variable_list["Theta Incr. (deg)"] = "-0.400000"
        # variable_list["Theta #Pts."] = "41"
        # variable_list["Scope channel"] = "Channel 1"
        # variable_list["Acquisition type"] = "N Averaged Waveform"
        # variable_list["Averages"] = "16"
        # variable_list["Data storage"] = "Do not store"
        # variable_list["Storage location"] = "UA results directory"
        # variable_list["Data directory"] = ""
        # variable_list["Max. position error (+/- mm)"] = "0.200000"
        # variable_list["ElementPositionTest"] = "FALSE"
        # variable_list["Max angle variation (deg)"] = "2.000000"
        # variable_list["BeamAngleTest"] = "FALSE"
        # variable_list["Frequency settings"] = "Avg. Low frequency"
        # variable_list["Auto set timebase"] = "TRUE"
        # variable_list["#Cycles.Capture"] = "10"
        # variable_list["#Cycles.Delay"] = "0"
        # variable_list["Frequency (MHz)"] = "4.400000"
        # variable_list["Amplitude (mV)"] = "50.000000"
        # variable_list["Burst count"] = "50"
        # return variable_list

        # self.find_element(variable_list)

        variable_list["Element"] = "Current"
        variable_list["Frequency range"] = "Low frequency"
        variable_list["RFB.#on/off cycles"] = "3"
        variable_list["RFB.On time (s)"] = "10.000000"
        variable_list["RFB.Off time (s)"] = "10.000000"
        variable_list["RFB.Threshold"] = "0.050000"
        variable_list["RFB.Offset"] = "0.500000"
        variable_list["Set frequency options"] = "Common peak frequency"
        variable_list["Frequency (MHz)"] = "4.200000"
        variable_list["Amplitude (mVpp)"] = "100.000000"
        variable_list["Storage location"] = "UA results directory"
        variable_list["Data directory"] = ""
        variable_list["RFB target position"] = "Average UA RFB position"
        variable_list["RFB target angle"] = "-90.000000"
        variable_list["EfficiencyTest"] = "TRUE"
        variable_list["Pa max (target, W)"] = "4.000000"
        variable_list["Pf max (limit, W)"] = "12.000000"
        variable_list["Reflection limit (%)"] = "70.000000"

        self.measure_element_efficiency_rfb(variable_list=variable_list)

    def add_devices(self):
        # -> check if we are simulating hardware
        self.SIMULATE_HARDWARE = self.config['Debugging']['simulate_hw']
        self.SIMULATE_MOTORS = self.config['Debugging']['simulate_motors']
        self.SIMULATE_OSCILLOSCOPE = self.config['Debugging']['simulate_oscilloscope']

        from Hardware.Abstract.abstract_sensor import AbstractSensor
        self.thermocouple = AbstractSensor(config=self.config)

        if self.SIMULATE_MOTORS:
            from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
            self.Motors = AbstractMotorController(config=self.config)
        else:
            from Hardware.VIX_Motor_Controller import VIX_Motor_Controller
            self.Motors = VIX_Motor_Controller(config=self.config, lock=self.motor_control_lock)

        self.rm = None

        if self.SIMULATE_OSCILLOSCOPE:
            from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope
            self.Oscilloscope = AbstractOscilloscope()
        else:
            from Hardware.keysight_oscilloscope import KeysightOscilloscope
            self.rm = pyvisa.ResourceManager()
            self.Oscilloscope = KeysightOscilloscope(config=self.config, resource_manager=self.rm)

        if self.SIMULATE_HARDWARE:
            from Hardware.Abstract.abstract_awg import AbstractAWG
            from Hardware.Abstract.abstract_balance import AbstractBalance
            from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
            from Hardware.Abstract.abstract_power_meter import PowerMeter
            from Hardware.Abstract.abstract_io_board import IO_Board
            from Hardware.Abstract.abstract_interface_box import UAInterfaceBox

            self.AWG = AbstractAWG(config=self.config)
            self.Balance = AbstractBalance(config=self.config)
            self.Forward_Power_Meter = PowerMeter(config=self.config, device_key='Forward_Power_Meter')
            self.Reflected_Power_Meter = PowerMeter(config=self.config, device_key='Reflected_Power_Meter')
            self.IO_Board = IO_Board(config=self.config)
            self.UAInterface = UAInterfaceBox(config=self.config)
        else:
            from Hardware.mini_circuits_power_meter import PowerMeter
            from Hardware.MT_balance import MT_balance
            from Hardware.ua_interface_box import UAInterfaceBox
            from Hardware.ni_daq_board import NI_DAQ
            from Hardware.mini_circuits_power_meter import PowerMeter

            if self.rm is None:
                self.rm = pyvisa.ResourceManager()
            from Hardware.keysight_awg import KeysightAWG
            self.AWG = KeysightAWG(config=self.config, resource_manager=self.rm)
            self.Balance = MT_balance(config=self.config)
            self.UAInterface = UAInterfaceBox(config=self.config)
            self.IO_Board = NI_DAQ(config=self.config)
            self.Forward_Power_Meter = PowerMeter(config=self.config, device_key='Forward_Power_Meter')
            self.Reflected_Power_Meter = PowerMeter(config=self.config, device_key='Reflected_Power_Meter')

        self.devices.append(self.Forward_Power_Meter)
        self.devices.append(self.Reflected_Power_Meter)
        self.devices.append(self.IO_Board)
        self.devices.append(self.UAInterface)
        self.devices.append(self.Motors)
        self.devices.append(self.thermocouple)
        self.devices.append(self.Oscilloscope)
        self.devices.append(self.Balance)
        self.devices.append(self.AWG)

    def connect_hardware(self):
        for device in self.devices:
            device.connect_hardware()
        t.sleep(2)
        # For testing purposes
        # self.findRMS(search_mode="coarse", frequency_mode="LF")

    def disconnect_hardware(self):
        for device in self.devices:
            device.disconnect_hardware()

    def run(self) -> None:
        """
        Overloaded function from QThread, this is the main scope control thread
        function.
        """
        self.mutex.lock()
        self.starttime = t.time()

        self.stay_alive = True

        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 50)

            if self.stay_alive is False:
                break

            self.cmd = self.cmd.upper()
            cmd_ray = self.cmd.split(' ')
            if cmd_ray[0] == 'CLOSE':
                self.wrap_up()
            elif cmd_ray[0] == 'CONNECT':
                self.connect_hardware()
            elif cmd_ray[0] == 'MOTOR':
                self.Motors.exec_command(self.cmd)
            # Todo: For testing purposes, remove later
            elif cmd_ray[0] == 'TEST':
                self.test_code()
            # What to do when there is no command
            else:
                if self.scripting:
                    if self.taskNames is None:
                        self.abort()
                    else:
                        self.advance_script()
                else:
                    if self.Oscilloscope.connected:
                        self.capture_and_plot()
                    else:
                        pass
                    self.update_motor_position()
                    if self.thermocouple.connected:
                        self.thermocouple.get_reading()

            self.cmd = ""
        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    @pyqtSlot()
    def run_script(self):
        if self.scripting:
            self.abort()
        log_msg(self, root_logger, level='info', message="Running script")
        self.scripting = True

    def update_motor_position(self):
        if self.Motors.connected and self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex()) == 'Position':
            if t.time() - self.last_get_position_time > self.get_position_cooldown_s:
                lock_aquired = self.motor_control_lock.tryLock()

                if lock_aquired:
                    self.Motors.get_position(mutex_locked=True)
                    self.last_get_position_time = t.time()
                    self.motor_control_lock.unlock()

    def capture_and_plot(self):
        # Do these things if a script is not being run

        # Only capture if the scan tab is selected
        if not self.parent.scan_tab_widget.plot_ready:
            return
        if not self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex()) == 'Scan':
            return

        tabs = self.parent.scan_tab_widget.scan_tabs

        if not tabs.tabText(tabs.currentIndex()) == "1D Scan":
            return

        try:
            time, voltage = self.Oscilloscope.capture(channel=1)
            time_elapsed = t.time() - self.starttime
            if time_elapsed != 0:
                self.refresh_rate = (round(1 / (time_elapsed), 1))

            self.plot_signal.emit(time, voltage, self.refresh_rate)
        except pyvisa.errors.InvalidSession:
            self.log("Could not plot, oscilloscope resource closed")

        self.starttime = t.time()

    def load_script(self, path):
        # get UA serial no. and append behind date
        self.script = open(path, "r")

        # Send name of script to UI
        split_path = path.split('/')
        self.test_data["script_name"] = split_path[len(split_path) - 1]
        self.script_name_signal.emit(self.test_data["script_name"])

        tasks = []  # the upper layer of our variable list
        loops = []
        self.taskExecOrder = []
        elementNamesForLoop = []
        taskNoForLoop = []
        currentLine = -1
        addingElementsToLoop = False
        buildingLoop = False
        taskVars = OrderedDict()  # the list of variables for the individual task
        taskNo = -2  # keeps track of the task number for indexing
        f = open(path, "r")
        for line in self.script:
            ray = line.split(' = ')

            #Populate script metadata to UI using signals
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
                    tasks.append(OrderedDict(taskVars))
                    taskVars.clear()  # empties out variable list for task since we're ready to move to the next set
                if addingElementsToLoop:  # detects if we're done with the element name block for the loop in script
                    addingElementsToLoop = False  # we're done with the block so set the flag to false
                continue  # move forward one line
            elif '[' in line:  # if the line we're on is a task line
                taskNo = taskNo + 1  # increments the task number counter since we've moved to the next task
                if "Task" in line and not buildingLoop:
                    self.taskExecOrder.append(taskNo)  # adding task number to the execution list
            else:  # above ensures we're not parsing a task header nor blank line
                x0 = ray[0].strip()  # remove trailing/leading spaces
                x1 = ray[1].strip().replace('"', "")  # does above but also removes quotation marks
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
            tasks.append(OrderedDict(taskVars))
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
        self.num_tasks_signal.emit(len(self.taskNames))
        f.close()
        self.scripting = False

    # Updates script step and executes the next step if applicable, and implements abort, continue, and retry
    @pyqtSlot()
    def advance_script(self):
        if self.retry_var is True:
            self.step_index = self.step_index - 1
            self.step_complete = True
            self.retry_var = False  # sets the retry variable to false so the retry function can happen again

        # advance to the next step if the previous has been completed
        if self.step_complete:
            self.step_index = self.step_index + 1

        # if a script is being executed, and the step index is valid, and the previous step is complete,
        # run the next script step

        if self.step_index >= len(self.taskNames):
            self.enable_ui_signal.emit()
            return

        if self.taskArgs is not None and self.taskNames is not None and self.taskExecOrder is not None:
            if 0 <= self.step_index < len(self.taskNames):
                if self.step_complete:
                    self.step_complete = False
                    self.run_script_step()

        if not self.scripting:
            self.enable_ui_signal.emit()

    '''Executes script step with given step index in taskNames/taskArgs'''

    def run_script_step(self):
        if self.taskArgs is None or self.taskNames is None or self.taskExecOrder is None:
            self.abort()
            return

        name = self.taskNames[self.step_index]  # sets name (str) to current iteration in taskNames list
        args = self.taskArgs[self.step_index]  # sets args (list) to current iteration in taskArgs list

        self.task_number_signal.emit(self.taskExecOrder[self.step_index][0])
        self.task_index_signal.emit(self.step_index)

        if not self.taskExecOrder[self.step_index][1] is None:  # if the element in the self.taskExecOrder isn't None
            # below: set the element to be operated on to the one in self.taskExecOrder
            args['Element'] = self.taskExecOrder[self.step_index][1]

        if "Measure element efficiency (RFB)".upper() in name.upper():
            self.measure_element_efficiency_rfb(args)
        elif name.upper() == "Pre-test initialisation".upper():
            self.pretest_initialization(args)
        elif "Find element n".upper() in name.upper():
            self.find_element(args)
        elif name.upper() == "Save results".upper():
            self.save_results(args, self.test_data)
        elif name.upper() == "Prompt user for action".upper():
            self.prompt_user_for_action(args)
        elif "Home system".upper() in name.upper():
            self.home_system(args)

        self.task_index_signal.emit(self.step_index + 1)

    '''Aborts script'''

    @pyqtSlot()
    def abort(self):
        self.log('Aborting script')
        # Reset script control variables
        self.scripting = False
        self.step_index = -1
        self.step_complete = True
        self.continue_var = True
        self.task_number_signal.emit(0)
        self.task_index_signal.emit(0)
        self.enable_ui_signal.emit()
        # Todo: add option to save before exiting

    '''Sets continue variable to False and waits for it to be true, disabling scripting if abort_var is true'''
    def wait_for_cont(self):
        self.continue_var = False
        while not self.continue_var:
            #check if script has been aborted
            if self.step_index == -1:
                # Always handle this exception
                raise AbortException

    '''Continues execution of script'''

    @pyqtSlot()
    def cont(self):
        self.continue_var = True

    '''Retries current step'''

    @pyqtSlot()
    def retry(self):
        self.retry_var = True

    def write_cal_data_to_ua_button(self):
        # Todo: make this method write calibration data to UA
        pass

    '''Collects metadata from user and prompts user until water level is ok'''

    def pretest_initialization(self, variable_list):
        # todo: add first 4 lines of scriptlog
        self.scriptlog.append([f"{self.test_data['serial_number']}-{self.test_data['test_date_time']}", '', '', ''])  # this is the first line
        self.scriptlog.append(["Running script: ", self.test_data['script_name'], '', '', ''])
        self.scriptlog.append(["Pretest_initialization", '', '', ''])

        # Check if wtfib is connected and add that to the scriptlog
        if self.UAInterface.is_connected:
            self.scriptlog.append(["", "Get UA Serial", "Connected", "OK"])
        else:
            self.scriptlog.append(["", "Get UA Serial", "Connected", "FAIL"])
            return "pretest_init fail"
        # Show dialogs until pump is on and the water sensor reads level
        # todo: have ua inserted to certain x position like in the ScriptResults.log
        while True:
            break  # todo: remove this line later. for testing only
            if not self.IO_Board.get_pump_reading():  # if the pump is not running
                # launch the dialog box signifying this issue
                self.user_prompt_pump_not_running_signal.emit(pump_status)
                try:
                    self.wait_for_cont()
                except AbortException:
                    self.scriptlog.append('', 'Check/prompt UA Pump', 'FAIL', '')
                    return self.abort()
            else:
                self.scriptlog.append('', 'Check/prompt UA Pump', 'OK', '')

                if self.thermocouple.is_connected():
                    self.scriptlog.append('', 'CheckThermocouple', 'OK', '')
                else:
                    self.scriptlog.append('', 'CheckThermocouple', 'FAIL', '')
                    # have the script aborted or wait for thermocouple?

                burst_mode, unused = self.AWG.GetBurst()
                if burst_mode == 1:
                    burst_mode = "Toneburst"
                else:
                    burst_mode = "Continuous"

                self.scriptlog.append(['', 'Config FGen', f"{round(self.AWG.getAmplitudeV()*1000, 0)}mVpp;{round(self.AWG.getFreq_Hz()/1000000, 2)}MHz;{burst_mode}", ''])

                # todo: have the user be prompted to ensure the power amplifier is on; check if successful if not log FAIL
                try:
                    self.scriptlog.append(['', 'Prompt PowerAmp', 'OK', ''])
                except:
                    self.scriptlog.append(['', 'Prompt PowerAmp', 'FAIL', ''])

                # todo: create data directories here
                try:
                    self.scriptlog.append(['', 'CreateDataDirectories', 'OK', ''])
                except:
                    self.scriptlog.append(['', 'CreateDataDirectories', 'FAIL', ''])

                # todo: create h/w log here
                try:
                    self.scriptlog.append(['', 'Create h/w log', 'OK', ''])
                except:
                    self.scriptlog.append(['', 'Create h/w log', 'FAIL', ''])

                # todo: initialize results FGV here
                try:
                    self.scriptlog.append(['', 'Initialize results FGV', 'OK', ''])
                except:
                    self.scriptlog.append(['', 'Initialize results FGV', 'FAIL', ''])

                # todo: duplicate main script?
                try:
                    self.scriptlog.append(['', 'duplicate main script', 'OK', ''])
                except:
                    self.scriptlog.append(['', 'Duplicate main script', 'FAIL', ''])

                water_level = self.IO_Board.get_water_level()
                if not water_level == 'level':  # if the water level is not level
                    # launch the dialog box signifying this issue
                    self.user_prompt_signal_water_too_low_signal.emit(water_level)
                    try:
                        self.wait_for_cont()
                    except AbortException:
                        self.scriptlog.append(['', 'Check/prompt water level', 'FAIL', ''])
                        return
                else:
                    self.scriptlog.append(['', 'Check/prompt water level', 'OK', ''])
                    break

        self.step_complete = True

    '''latches info from user in MainWindow to manager local vars'''

    @pyqtSlot(dict)
    def pretest_metadata_slot(self, pretest_metadata):
        #reset test data to default values
        self.test_data = blank_test_data()
        self.test_data.update(pretest_metadata)
        self.run_script()
        self.scriptlog.append(['', "Prompt username+UA serial", 'OK', ''])

    '''Find UA element with given number'''

    def find_element(self, variable_list):
        self.scriptlog.append(['Find element "n"', 'OK', '', ''])
        element = int(re.search(r'\d+', str(variable_list['Element'])).group())

        # Update UI visual to reflect the element we are on
        self.element_number_signal.emit(str(element))

        element_x_coordinate = self.element_x_coordinates[element]
        element_r_coordinate = self.element_r_coordinates[element]
        print(f"Finding element {element}, near coordinate x = {element_x_coordinate}, r = {element_r_coordinate}")

        t.sleep(.1)
        x_increment_MM = float(variable_list['X Incr. (mm)'])
        XPts = int(variable_list['X #Pts.'])
        thetaIncrDeg = float(variable_list['Theta Incr. (deg)'])
        thetaPts = int(variable_list['Theta #Pts.'])
        scope_channel = int(variable_list['Scope channel'][8:])
        acquisition_type = variable_list['Acquisition type']
        averages = int(variable_list['Averages'])
        data_storage = variable_list['Data storage']
        storage_location = variable_list['Storage location']
        data_directory = variable_list["Data directory"]
        maxPosErrMM = float(variable_list["Max. position error (+/- mm)"])
        elemPosTest = bool(variable_list["ElementPositionTest"])

        # Configure hardware
        frequency_Hz = self.test_data['low_frequency_MHz'] * 1000000
        self.AWG.SetFrequency_Hz(frequency_Hz)
        self.AWG.SetOutput(True)

        if acquisition_type.upper() == 'N Averaged Waveform'.upper():
            self.Oscilloscope.SetAveraging(averages)
        else:
            self.Oscilloscope.SetAveraging(1)

        # Loop over x through a given range, move to the position where maximal RMS voltage was measured
        x_sweep_waveforms = list()
        x_positions = list()
        x_rms_values = list()

        # sweep from the expected element position minus the max error to the expected element position plus max error
        position = -1 * (XPts * x_increment_MM) / 2 + element_x_coordinate

        # begin with arbitrarily low values
        x_max_rms = -1 * sys.float_info.max
        x_max_position = -1 * sys.float_info.max
        for i in range(XPts):
            if self.step_index == -1:
                return
            self.Motors.go_to_position(['X'], [position])
            position = position + abs(x_increment_MM)

            voltage, time = self.Oscilloscope.capture(scope_channel)
            if not data_storage.upper() == 'Do not store'.upper():
                x_sweep_waveforms.append([voltage, time])

            rms = self.find_rms(time_s=time, voltage_v=voltage)

            if rms > x_max_rms:
                x_max_rms = rms
                x_max_position = position

            x_positions.append(position)
            x_rms_values.append(rms)
            self.profile_plot_signal.emit(x_positions, x_rms_values, 'Distance (mm)')

        self.log(f"Maximum of {x_max_rms} @ x = {x_max_position} mm. Going there.")

        # update element x position
        self.element_x_coordinates[element] = x_max_position

        status = self.Motors.go_to_position(['X'], [x_max_position])

        # todo: test this to make sure it triggers if and only if the movement fails
        if not status:
            self.log(level="error", message="Motor movement not successful")
            if self.config["Debugging"]["end_script_on_errors"]:
                self.abort()
                return

        self.scan_data["X sweep waveforms"] = x_sweep_waveforms

        # Loop over r through a given range, move to the position where maximal RMS voltage was measured
        r_sweep_waveforms = list()
        position = -1 * (thetaPts * thetaIncrDeg) / 2 + self.config["WTF_PositionParameters"]["ThetaHomeCoord"]

        # begin with arbitrarily low values
        r_max_rms = -1 * sys.float_info.max
        r_max_position = -1 * sys.float_info.max

        r_positions = list()
        r_rms_values = list()

        for i in range(thetaPts):
            #check if the script has been aborted
            if self.step_index == -1:
                return

            self.Motors.go_to_position(['R'], [position])
            position = position + thetaIncrDeg

            voltage, time = self.Oscilloscope.capture(scope_channel)
            if not data_storage.upper() == 'Do not store'.upper():
                r_sweep_waveforms.append([voltage, time])

            rms = self.find_rms(time_s=time, voltage_v=voltage)

            if rms > r_max_rms:
                r_max_rms = rms
                r_max_position = position

            r_positions.append(position)
            r_rms_values.append(rms)
            self.profile_plot_signal.emit(r_positions, r_rms_values, 'Angle (deg)')

        self.Motors.go_to_position(['R'], [r_max_position])
        self.scan_data["Theta sweep waveforms"] = r_sweep_waveforms

        self.log(f"Maximum of {r_max_rms} @ theta = {r_max_position} degrees. Going there.")
        # update element r position
        self.element_r_coordinates[element] = r_max_position

        # update results summary
        self.test_data['results_summary'][element - 1][1] = "%.2f" % x_max_position
        self.test_data['results_summary'][element - 1][2] = "%.2f" % r_max_position
        self.step_complete = True

    '''Measure the efficiency of an element'''

    def measure_element_efficiency_rfb(self, variable_list):
        # Todo: implement zeroing such that balance reading subtracts the averaging reading when the balance is off
        element = int(re.search(r'\d+', str(variable_list['Element'])).group())
        element_x_coordinate = self.element_x_coordinates[element]
        element_r_coordinate = self.element_x_coordinates[element]
        print(f"Measuring effeciency of {element}, at coordinate x={element_x_coordinate}, r={element_r_coordinate}")
        self.element_number_signal.emit(str(element))
        self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, element_r_coordinate])
        frequency_range = variable_list['Frequency range']
        on_off_cycles = int(variable_list['RFB.#on/off cycles'])
        rfb_on_time = float(variable_list['RFB.On time (s)'])
        rfb_off_time = float(variable_list['RFB.Off time (s)'])

        if frequency_range == "High frequency":
            frequency_Hz = self.test_data['high_frequency_MHz'] * 1000000
        elif frequency_range == "Low frequency":
            frequency_Hz = self.test_data['low_frequency_MHz'] * 1000000
        else:
            self.log("Improper frequency set, defaulting to low frequency")
            frequency_Hz = self.parent.ua_calibration_tab.Low_Frequency_MHz * 1000000

        self.AWG.SetFrequency_Hz(frequency_Hz)
        self.AWG.SetOutput(False)

        self.Balance.zero_balance_instantly()

        forward_powers_w = list()
        forward_powers_time_s = list()
        reflected_powers_w = list()
        reflected_powers_time_s = list()
        acoustic_powers_w = list()
        acoustic_powers_time_s = list()

        awg_on = list()

        startTime = t.time()
        current_cycle = 1

        while current_cycle <= on_off_cycles:
            cycle_start_time = t.time()
            self.AWG.SetOutput(True)
            while t.time() - cycle_start_time < rfb_on_time:  # for the duration of rfb on time
                if self.step_index == -1:
                    return

                forward_power_w = self.Forward_Power_Meter.get_reading()
                forward_powers_w.append(forward_power_w)
                forward_powers_time_s.append(t.time() - startTime)

                reflected_power_w = self.Reflected_Power_Meter.get_reading()
                reflected_powers_w.append(reflected_power_w)
                reflected_powers_time_s.append(t.time() - startTime)

                balance_reading = self.Balance.get_reading()
                if balance_reading is not None:
                    acoustic_power_w = calculate_power_from_balance_reading(balance_reading)
                    acoustic_powers_w.append(acoustic_power_w)
                    acoustic_powers_time_s.append(t.time() - startTime)
                    awg_on.append(True)

                # package data to send it to the rfb ui tab
                self.rfb_args['forward_s'] = forward_powers_time_s
                self.rfb_args['forward_w'] = forward_powers_w
                self.rfb_args['reflected_s'] = reflected_powers_time_s
                self.rfb_args['reflected_w'] = reflected_powers_w
                self.rfb_args['acoustic_s'] = acoustic_powers_time_s
                self.rfb_args['acoustic_w'] = acoustic_powers_w
                self.rfb_args['awg_on'] = awg_on
                self.rfb_args['grams'] = balance_reading
                self.rfb_args['forward_power_w'] = forward_power_w
                self.rfb_args['reflected_power_w'] = reflected_power_w
                self.update_rfb_tab_signal.emit()

                self.app.processEvents()

            #  turn off awg
            self.AWG.SetOutput(False)

            while t.time() - cycle_start_time < rfb_on_time + rfb_off_time:  # for the duration of rfb on time
                if self.step_index == -1:
                    return

                forward_power_w = self.Forward_Power_Meter.get_reading()
                forward_powers_w.append(forward_power_w)
                forward_powers_time_s.append(t.time() - startTime)

                reflected_power_w = self.Reflected_Power_Meter.get_reading()
                reflected_powers_w.append(reflected_power_w)
                reflected_powers_time_s.append(t.time() - startTime)

                balance_reading = self.Balance.get_reading()
                if balance_reading is not None:
                    acoustic_power_w = calculate_power_from_balance_reading(balance_reading)
                    acoustic_powers_w.append(acoustic_power_w)
                    acoustic_powers_time_s.append(t.time() - startTime)
                    awg_on.append(False)

                # package data to send it to the rfb ui tab
                self.rfb_args['forward_s'] = forward_powers_time_s
                self.rfb_args['forward_w'] = forward_powers_w
                self.rfb_args['reflected_s'] = reflected_powers_time_s
                self.rfb_args['reflected_w'] = reflected_powers_w
                self.rfb_args['acoustic_s'] = acoustic_powers_time_s
                self.rfb_args['acoustic_w'] = acoustic_powers_w
                self.rfb_args['awg_on'] = awg_on
                self.rfb_args['grams'] = balance_reading
                self.rfb_args['forward_power_w'] = forward_power_w
                self.rfb_args['reflected_power_w'] = reflected_power_w
                self.update_rfb_tab_signal.emit()
                self.app.processEvents()

            current_cycle = current_cycle + 1  # we just passed a cycle at this point in the code

        print(f"Final time: {t.time() - startTime}")

        # List containing all readings while AWG was on
        acoustic_power_on_data = get_awg_on_values(acoustic_powers_w, awg_on)
        # Mean acoustic power while on
        acoustic_power_on_mean = sum(acoustic_power_on_data) / len(acoustic_power_on_data)

        # List containing all readings while AWG was on
        forward_power_on_data = get_awg_on_values(forward_powers_w, awg_on)
        # Mean acoustic power while on
        forward_power_on_mean = sum(forward_power_on_data) / len(forward_power_on_data)

        effeciency_percent = acoustic_power_on_mean / forward_power_on_mean

        # List containing all readings while AWG was on
        reflected_power_on_data = get_awg_on_values(reflected_powers_w, awg_on)
        # Mean acoustic power while on
        reflected_power_on_mean = sum(reflected_power_on_data) / len(reflected_power_on_data)

        reflected_power_percent = reflected_power_on_mean / forward_power_on_mean

        forward_power_max = max(forward_power_on_data)

        water_temperature = self.thermocouple.get_reading()

        if frequency_range == "High frequency":
            # High frequency
            self.test_data['results_summary'][element - 1][5] = "%.2f" % (frequency_Hz / 1000000)
            # HF effeciency (%)
            self.test_data['results_summary'][element - 1][11] = "%.0f" % effeciency_percent
            self.test_data['results_summary'][element - 1][12] = "%.1f" % reflected_power_percent
            self.test_data['results_summary'][element - 1][13] = "%.1f" % forward_power_max
            self.test_data['results_summary'][element - 1][14] = "%.1f" % water_temperature
        else:  # Default to low frequency
            # Low Frequency
            self.test_data['results_summary'][element - 1][3] = "%.2f" % (frequency_Hz / 1000000)
            # LF effeciency (%)
            self.test_data['results_summary'][element - 1][7] = "%.0f" % effeciency_percent
            self.test_data['results_summary'][element - 1][8] = "%.1f" % reflected_power_percent
            self.test_data['results_summary'][element - 1][9] = "%.1f" % forward_power_max
            self.test_data['results_summary'][element - 1][10] = "%.1f" % water_temperature

        self.element_number_signal.emit(str(element))
        self.step_complete = True

    '''Save scan results to a file'''

    def save_results(self, variable_list, calibration_data):  # calibration_data is the data gathered by the UA test
        save_summary_file = bool(distutils.util.strtobool(variable_list["Save summary file"]))
        write_uac_calibration = bool(distutils.util.strtobool(variable_list["Write UA Calibration"]))
        prompt_for_calibration_write = bool(distutils.util.strtobool(variable_list["PromptForCalWrite"]))

        self.test_data["write_result"] = self.UAInterface.UA_Write_Result
        self.test_data["software_version"] = self.config["Software_Version"]

        sum = 0
        count = 0
        for i in range(10):
            sum = sum + float(self.test_data['results_summary'][i][2])
            count = count + 1

        angle_average = sum / count

        self.test_data['results_summary'][10][2] = str(angle_average)

        self.save_results_signal.emit(self.test_data)

        if prompt_for_calibration_write:  # displays the "write to UA" dialog box if this variable is true
            self.write_cal_data_to_ua_dialog(calibration_data)

        self.step_complete = True

    '''Prompt user for action'''

    def prompt_user_for_action(self, variable_list):
        prompt_type = variable_list["Prompt type"]
        self.step_complete = True

    '''Return axis to zero coordinate'''

    def home_system(self, variable_list):
        # TODO: have this be called in pretest_initialization and have it add to script log
        axis_to_home = variable_list['Axis to home']
        if axis_to_home == 'X':
            self.retracting_ua_warning_signal.emit()  # launch the retracting UA in the x direction warning box
            try:
                self.wait_for_cont()
            except AbortException:
                return self.abort()

        # TODO: have the pump home in the desired direction

        self.step_complete = True
        # self.scriptlog.append(['', "Home all", f"X={X}; Theta={theta}", ''])

    '''Warn the user that the UA is being retracted in x'''

    def retract_ua_warning(self):
        self.retracting_ua_warning_signal.emit()

    # calibration_data should be a 2d list: 1st col: cal data array, 2nd col: low freq, 3rd col: high freq
    def write_cal_data_to_ua_dialog(self, calibration_data):
        self.write_cal_data_to_ua_signal.emit(calibration_data)

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
            self.cmd = ''
            return
        if 'ABORT' in command.upper():
            self.abort()
            self.cmd = ''
            return
        self.cmd = command
        self.condition.wakeAll()

    def wrap_up(self):
        for device in self.devices:
            device.wrap_up()
        self.stay_alive = False

    def log(self, message, level='info'):
        log_msg(self, root_logger=root_logger, message=message, level=level)

    def frequency_sweep(self, search_mode, frequency_mode):
        if search_mode == "fine":
            self.step = self.config["FrequencyParameters"]["Search"]["FineIncr(MHz)"] * 1000000
        elif search_mode == "coarse":
            self.step = self.config["FrequencyParameters"]["Search"]["CoarseIncr(MHz)"] * 1000000

        if frequency_mode == "HF":
            self.freq_lowlimit_hz = self.config["FrequencyParameters"]["HF"]["LowFreqLimit(MHz)"] * 1000000
            self.freq_highlimit_hz = self.config["FrequencyParameters"]["HF"]["HighFreqLimit(MHz)"] * 1000000
        elif frequency_mode == "LF":
            self.freq_lowlimit_hz = self.config["FrequencyParameters"]["LF"]["LowFreqLimit(MHz)"] * 1000000
            self.freq_highlimit_hz = self.config["FrequencyParameters"]["LF"]["HighFreqLimit(MHz)"] * 1000000

        self.list_of_rms_values = list()
        self.list_of_frequencies = list()

        for x in np.arange(self.freq_lowlimit_hz, self.freq_highlimit_hz, self.step):
            self.AWG.SetFrequency_Hz(x)  # set frequency accoding to step (coarse/fine) and x incremenet
            self.list_of_frequencies.append(x)  # add the frequency to the list
            self.times_s, self.voltages_v = self.Oscilloscope.capture(1)
            # populates times_s and voltages_v with set frequency
            self.voltages_v_squared = np.square(self.voltages_v)  # squares every value in the voltage graph
            self.list_of_rms_values.append(
                integrate.simps(self.voltages_v_squared, self.times_s, dx=None, axis=0))  # returns single value
            times_s, voltages_v = self.Oscilloscope.capture(1)  # populates times_s and voltages_v with set frequency

            self.list_of_rms_values.append(self.find_rms(times_s, voltages_v))
        self.profile_plot_signal.emit(self.list_of_frequencies, self.list_of_rms_values, "Frequency (Hz)")
        # frequencies will be on the x-axis

    '''Returns the voltage squared integral of a oscilloscope waveform'''

    def find_rms(self, time_s, voltage_v):
        dx = 0
        for i in range(1, len(time_s)):
            dx = time_s[i] - time_s[i - 1]
            if not dx == 0:
                break

        voltages_v_squared = np.square(voltage_v)

        if dx == 0:
            self.log(level='Error', message='Error in find_rms. No delta x found, cannot integrate')
            return

        return integrate.simps(y=voltages_v_squared, dx=dx, axis=0)


class AbortException(Exception):
    pass
