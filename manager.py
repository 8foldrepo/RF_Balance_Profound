import sys
import re
import pyvisa
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutex, QThread, QWaitCondition, pyqtSignal, pyqtSlot
from collections import OrderedDict
import distutils.util
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
import time as t
import numpy as np
from scipy import integrate
from Utilities.useful_methods import log_msg, get_element_distances, get_awg_on_values, blank_test_data, \
    generate_calibration_data
from Utilities.formulas import calculate_power_from_balance_reading
from definitions import ROOT_DIR
import os

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
wtf_logger.addHandler(file_handler)
wtf_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

pump_status = ""
tank_status = ""


# todo: continue adding prebuilt methods for all of the actions in script editor
class Manager(QThread):
    sensor_refresh_interval_s: float
    last_sensor_update_time: float
    # Dialog signals
    user_prompt_signal = pyqtSignal(str)  # str is message for user to read
    user_prompt_pump_not_running_signal = pyqtSignal(str)  # str is pump status
    user_prompt_signal_water_too_low_signal = pyqtSignal(str)  # str is water level
    write_cal_data_to_ua_signal = pyqtSignal(list)  # list is 2d array of calibration data
    retracting_ua_warning_signal = pyqtSignal()
    script_complete_signal = pyqtSignal(list, list)  # Contains a pass/fail list of booleans and a list of descriptions

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

    def __init__(self, config: dict, parent=None):
        super().__init__(parent=parent)
        QThread.currentThread().setObjectName("manager_thread")
        print()
        # decreasing these improves the refresh rate of the sensors, at the cost of responsiveness
        self.sensor_refresh_interval_s = .2
        self.last_sensor_update_time = 0.0

        self.app = QApplication.instance()
        self.test_data = blank_test_data()

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

        self.element = 1

        # Script control vars
        self.scripting = False
        self.continue_var = True
        self.retry_var = False  # keep track of whether user wants to try script iteration, default false

        # Keeps track of script step in progress
        self.step_complete = True

        # step_index = -1 if no script is being run. It is also the way to check if the script has been aborted
        self.step_index = -1

        # ResourceManager for the oscilloscope and function generators
        self.rm = None
        self.devices = list()
        self.add_devices()

    def test_code(self):
        # # todo: test code, remove later
        # self.scripting = True
        #
        #
        var_dict = dict()
        # var_dict["Task type"] = "Find element \"n\""
        # var_dict["Element"] = "Element 1"
        # var_dict["X Incr. (mm)"] = "0.250000"
        # var_dict["X #Pts."] = "21"
        # var_dict["Theta Incr. (deg)"] = "-0.400000"
        # var_dict["Theta #Pts."] = "41"
        # var_dict["Scope channel"] = "Channel 1"
        # var_dict["Acquisition type"] = "N Averaged Waveform"
        # var_dict["Averages"] = "16"
        # var_dict["Data storage"] = "Do not store"
        # var_dict["Storage location"] = "UA results directory"
        # var_dict["Data directory"] = ""
        # var_dict["Max. position error (+/- mm)"] = "0.200000"
        # var_dict["ElementPositionTest"] = "FALSE"
        # var_dict["Max angle variation (deg)"] = "2.000000"
        # var_dict["BeamAngleTest"] = "FALSE"
        # var_dict["Frequency settings"] = "Avg. Low frequency"
        # var_dict["Auto set timebase"] = "TRUE"
        # var_dict["#Cycles.Capture"] = "10"
        # var_dict["#Cycles.Delay"] = "0"
        # var_dict["Frequency (MHz)"] = "4.400000"
        # var_dict["Amplitude (mV)"] = "50.000000"
        # var_dict["Burst count"] = "50"
        # return var_dict

        # self.find_element(var_dict)

        var_dict["Element"] = "Current"
        var_dict["Frequency range"] = "Low frequency"
        var_dict["RFB.#on/off cycles"] = "3"
        var_dict["RFB.On time (s)"] = "10.000000"
        var_dict["RFB.Off time (s)"] = "10.000000"
        var_dict["RFB.Threshold"] = "0.050000"
        var_dict["RFB.Offset"] = "0.500000"
        var_dict["Set frequency options"] = "Common peak frequency"
        var_dict["Frequency (MHz)"] = "4.200000"
        var_dict["Amplitude (mVpp)"] = "100.000000"
        var_dict["Storage location"] = "UA results directory"
        var_dict["Data directory"] = ""
        var_dict["RFB target position"] = "Average UA RFB position"
        var_dict["RFB target angle"] = "-90.000000"
        var_dict["EfficiencyTest"] = "TRUE"
        var_dict["Pa max (target, W)"] = "4.000000"
        var_dict["Pf max (limit, W)"] = "12.000000"
        var_dict["Reflection limit (%)"] = "70.000000"

        self.measure_element_efficiency_rfb(var_dict=var_dict)

    def add_devices(self):
        # -> check if we are simulating hardware
        if self.config['Debugging']['simulate_motors']:
            from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
            self.Motors = AbstractMotorController(config=self.config)
        else:
            from Hardware.VIX_Motor_Controller import VIX_Motor_Controller
            self.Motors = VIX_Motor_Controller(config=self.config, lock=self.motor_control_lock)

        if self.config['Debugging']['simulate_oscilloscope']:
            from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope
            self.Oscilloscope = AbstractOscilloscope()
        else:
            from Hardware.keysight_oscilloscope import KeysightOscilloscope
            self.rm = pyvisa.ResourceManager()
            self.Oscilloscope = KeysightOscilloscope(config=self.config, resource_manager=self.rm)

        if self.config['Debugging']['simulate_ua_interface']:
            from Hardware.Abstract.abstract_interface_box import UAInterfaceBox
            self.UAInterface = UAInterfaceBox(config=self.config)
        else:
            from Hardware.ua_interface_box import UAInterfaceBox
            self.UAInterface = UAInterfaceBox(config=self.config)

        if self.config['Debugging']['simulate_hw']:
            from Hardware.Abstract.abstract_awg import AbstractAWG
            from Hardware.Abstract.abstract_balance import AbstractBalance
            from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
            from Hardware.Abstract.abstract_power_meter import PowerMeter
            from Hardware.Abstract.abstract_io_board import IO_Board

            from Hardware.Abstract.abstract_sensor import AbstractSensor
            self.thermocouple = AbstractSensor(config=self.config)
            self.AWG = AbstractAWG(config=self.config)
            self.Balance = AbstractBalance(config=self.config)
            self.Forward_Power_Meter = PowerMeter(config=self.config, device_key='Forward_Power_Meter')
            self.Reflected_Power_Meter = PowerMeter(config=self.config, device_key='Reflected_Power_Meter')
            self.IO_Board = IO_Board(config=self.config)

        else:
            from Hardware.mini_circuits_power_meter import PowerMeter
            from Hardware.MT_balance import MT_balance
            from Hardware.ni_daq_board import NI_DAQ
            from Hardware.mini_circuits_power_meter import PowerMeter
            from Hardware.NI_thermocouple import Thermocouple
            from Hardware.keysight_awg import KeysightAWG
            if self.rm is None:
                self.rm = pyvisa.ResourceManager()
            self.AWG = KeysightAWG(config=self.config, resource_manager=self.rm)
            self.Balance = MT_balance(config=self.config)
            self.IO_Board = NI_DAQ(config=self.config, simulate_sensors=self.config['Debugging']['simulate_sensors'])
            self.Forward_Power_Meter = PowerMeter(config=self.config, device_key='Forward_Power_Meter')
            self.Reflected_Power_Meter = PowerMeter(config=self.config, device_key='Reflected_Power_Meter')
            self.thermocouple = Thermocouple(config=self.config)

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
                        self.realtime_capture_and_plot()
                    else:
                        pass
                    self.update_sensors()
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

    def update_sensors(self):
        # Return if there the user is not looking at positional feedback
        if self.parent is not None:
            if not hasattr(self.parent, 'tabWidget'):
                return

        if t.time() - self.last_sensor_update_time > self.sensor_refresh_interval_s:
            self.last_sensor_update_time = t.time()

            if self.IO_Board.connected():
                self.IO_Board.get_water_level()

            if self.IO_Board.connected():
                self.IO_Board.get_ua_pump_reading()

            if self.thermocouple.connected:
                self.thermocouple.get_reading()

            # TODO: uncomment if continuous position feedback this is deemed useful
            # Only refresh motor position if they are connected
            if self.Motors.connected:
                lock_aquired = self.motor_control_lock.tryLock()
                if lock_aquired:
                    self.Motors.get_position(mutex_locked=True)
                    self.motor_control_lock.unlock()

    def capture_scope(self, plot=True, channel=1):
        try:
            time, voltage = self.Oscilloscope.capture(channel=channel)
            if plot:
                self.plot_scope(time, voltage)
            return time, voltage
        except pyvisa.errors.InvalidSession:
            self.log(level='error', message="Could not capture, oscilloscope resource closed")
        return [], []

    def plot_scope(self, time, voltage):
        time_elapsed = t.time() - self.starttime
        if time_elapsed != 0:
            self.refresh_rate = (round(1 / (time_elapsed), 1))

        self.plot_signal.emit(time, voltage, self.refresh_rate)

    # noinspection PyUnresolvedReferences
    def realtime_capture_and_plot(self):
        # Do these things if a script is not being run

        # Only capture if the scan tab is selected
        if not self.parent.scan_tab_widget.plot_ready:
            return
        if not self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex()) == 'Scan':
            return

        tabs = self.parent.scan_tab_widget.scan_tabs

        if not tabs.tabText(tabs.currentIndex()) == "1D Scan":
            return

        time, voltage = self.capture_scope()

        self.plot_scope(time, voltage)

        self.starttime = t.time()

    # noinspection PyUnresolvedReferences
    def load_script(self, path):
        self.abort(log=False)

        self.script = open(path, "r")

        # Send name of script to UI
        split_path = path.split('/')
        self.test_data["script_name"] = split_path[len(split_path) - 1]
        self.script_name_signal.emit(self.test_data["script_name"])

        tasks = []  # the upper layer of our variable list
        self.loops = []
        self.taskExecOrder = []
        elementNamesForLoop = []
        taskNoForLoop = []
        currentLine = -1
        loop_index_tracker = 0
        addingElementsToLoop = False
        buildingLoop = False
        taskVars = OrderedDict()  # the list of variables for the individual task
        taskNo = -2  # keeps track of the task number for indexing
        f = open(path, "r")
        for line in self.script:
            ray = line.split(' = ')

            # Populate script metadata to UI using signals
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

                # if we're on a line that adds an element name for the loop
                if addingElementsToLoop and "Element" in x0:
                    # split the left side of the variable assigner by space
                    elementNamePre = x0.split(' ')
                    # retrieve the second word of the left side, that's the element name
                    elementName = elementNamePre[1]
                    elementNamesForLoop.append(int(elementName))

                if "End loop" in x1:  # script will have "End loop" in right side of task type to end loop block
                    buildingLoop = False  # set the building loop flag to false since the loop block is done
                    self.loops.append(list([list(elementNamesForLoop), list(taskNoForLoop)]))
                    elementNamesForLoop.clear()
                    taskNoForLoop.clear()
                    self.taskExecOrder.pop()

                    # appends a 2 item list in taskExecOrder, the first part being the element within the loops
                    # sublist and the second item being the iteration number for that item in its loop
                    for i in range(len(self.loops[len(self.loops) - 1][0])):
                        for j in range(len(self.loops[len(self.loops) - 1][1])):
                            self.taskExecOrder.append([self.loops[len(self.loops) - 1][1][j], i + 1,
                                                       loop_index_tracker])
                    loop_index_tracker = loop_index_tracker + 1

                # if we're building a loop & are not in the name adding phase
                if buildingLoop and not addingElementsToLoop:

                    # ensure the task no. isn't already in the task list for the loop
                    if taskNo not in taskNoForLoop:
                        taskNoForLoop.append(
                            taskNo)  # add the current task no. to the list of tasks we need to run in loop
        f.close()

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

    # get UA serial no. and append behind date

    # Updates script step and executes the next step if applicable, and implements abort, continue, and retry
    @pyqtSlot()
    def advance_script(self):
        if self.taskNames is None:
            self.abort()
            return

        if self.retry_var is True:
            self.step_index = self.step_index - 1
            self.step_complete = True
            self.retry_var = False  # sets the retry variable to false so the retry function can happen again

        # advance to the next step if the previous has been completed
        if self.step_complete:
            self.step_index = self.step_index + 1

        # if a script is being executed, and the step index is valid, and the previous step is complete,
        # run the next script step

        if self.step_index > len(self.taskNames):
            self.script_complete()
            return

        if self.taskArgs is not None and self.taskNames is not None and self.taskExecOrder is not None:
            if 0 <= self.step_index < len(self.taskNames):
                inside_iteration = False
                iteration_number = None

                if len(self.taskExecOrder[
                           self.step_index]) == 3:  # elements that are a part of a loop will have a third sub element notating which loop it's from
                    self.test_data["script_log"].append([
                        f"Iteration {self.taskExecOrder[self.step_index][1]} of {len(self.loops[self.taskExecOrder[self.step_index][2]][0])}",
                        '', '', ''])
                    inside_iteration = True
                    iteration_number = self.taskExecOrder[self.step_index][1]

                if self.step_complete:
                    self.step_complete = False
                    self.run_script_step()
                    if inside_iteration:
                        self.test_data["script_log"].append([f"Iteration {iteration_number} complete", '', '', ''])
                        inside_iteration = False

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
            self.save_results(args)
        elif name.upper() == "Prompt user for action".upper():
            self.prompt_user_for_action(args)
        elif "Home system".upper() in name.upper():
            self.home_system(args)

        self.task_index_signal.emit(self.step_index + 1)

        # below helps explain loop and list logic
        # if len(self.taskExecOrder[self.step_index]) == 3:
        #     print(f"looped element {self.taskExecOrder[self.step_index][0]} is in iteration {self.taskExecOrder[self.step_index][1]} from loop {self.loops[self.taskExecOrder[self.step_index][2]]}")

    '''Aborts script'''

    @pyqtSlot()
    def abort(self, log=True):
        if log:
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
            # check if script has been aborted
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

    '''Run when the script finishes its final step. Shows a dialog with pass/fail results and enables the UI'''

    def script_complete(self):
        # Fetch pass list and description list from testdata
        pass_list = [None] * 11
        description_list = [None] * 11
        for i in range(10):
            pass_list[i] = self.test_data['results_summary'][i][15]
            description_list[i] = self.test_data['results_summary'][i][16]

        # Add ua write result to output
        pass_list[10] = self.test_data['write_result']
        description_list[10] = ''

        self.script_complete_signal.emit(pass_list, description_list)
        self.scripting = False
        self.enable_ui_signal.emit()

        self.test_data["script_log"].append(['Script complete', '', '', ''])

    '''Collects metadata from user and prompts user until water level is ok'''

    def pretest_initialization(self, var_dict):
        # add first 4 lines of scriptlog
        self.test_data["script_log"].append([f"{self.test_data['serial_number']}-{self.test_data['test_date_time']}",
                                             '', '', ''])  # this is the first line
        self.test_data["script_log"].append(["Running script: ", self.test_data['script_name'], '', '', ''])
        self.test_data["script_log"].append(["Pretest_initialization", '', '', ''])
        self.test_data["script_log"].append(['', "Prompt username+UA serial", 'OK', ''])

        # Check if wtfib is connected and add that to the scriptlog
        if self.UAInterface.UA_Read_Result:
            self.test_data["script_log"].append(["", "Get UA Serial", "Connected", "OK"])
        else:
            self.test_data["script_log"].append(["", "Get UA Serial", "Connected", "FAIL"])
            if self.config["Debugging"]['end_script_on_errors']: return self.abort()

        # Show dialogs until pump is on and the water sensor reads level
        while True:
            if not self.IO_Board.get_ua_pump_reading():  # if the pump is not running
                # launch the dialog box signifying this issue
                self.user_prompt_pump_not_running_signal.emit(pump_status)
                try:
                    self.wait_for_cont()
                except AbortException:
                    self.test_data["script_log"].append(['', 'Check/prompt UA Pump', 'FAIL', 'Closed by user'])
                    return self.abort()
            else:
                self.test_data["script_log"].append(['', 'Check/prompt UA Pump', 'OK', ''])
                break

        # todo: have ua inserted to certain x position like in the ScriptResults.log
        try:
            self.home_system(var_dict={"Axis to home": "All Axes"})
            self.test_data["script_log"].append(['', "Home all", f"OK; X={self.Motors.coords_mm[0]}; "
                                                                 f"Theta={self.Motors.coords_mm[1]}", ''])
        except Exception as e:
            self.test_data['script_log'].append(['', 'Home all', f"FAIL: {e}", ''])
            if self.config["Debugging"]['end_script_on_errors']: return self.abort()

        try:
            self.test_data["script_log"].append(['', 'Insert UA', f"UA Inserted to X={self.Motors.coords_mm[0]}"])
        except Exception as e:
            self.test_data["script_log"].append(['', 'Insert UA', f'FAIL {e}'])
            if self.config["Debugging"]['end_script_on_errors']: return self.abort()

        if self.thermocouple.is_connected:
            self.test_data["script_log"].append(['', 'CheckThermocouple', 'OK', ''])
        else:
            self.test_data["script_log"].append(['', 'CheckThermocouple', 'FAIL', ''])
            if self.config["Debugging"]['end_script_on_errors']: return self.abort()
            # have the script aborted or wait for thermocouple?

        burst_mode, unused = self.AWG.GetBurst()

        # Configure function generator
        func_var_dict = dict()
        func_var_dict["Amplitude (mVpp)"] = self.config[self.AWG.device_key]['amplitude_V'] * 1000
        func_var_dict["Frequency (MHz)"] = self.test_data['low_frequency_MHz']
        func_var_dict["Mode"] = "Toneburst"
        func_var_dict["Enable output"] = True
        func_var_dict["#Cycles"] = self.config[self.AWG.device_key]['burst_cycles']
        func_var_dict["Set frequency options"] = "From config cluster"  # Todo: what does this mean?
        self.configure_function_generator(func_var_dict)

        # todo: have the user be prompted to ensure the power amplifier is on; check if successful if not log FAIL

        # Prompt user to turn on power amp
        while True:
            self.user_prompt_signal.emit("Please ensure that the power amplifier is on")
            try:
                self.wait_for_cont()
            except AbortException as e:
                self.test_data["script_log"].append(['', 'Prompt PowerAmp', 'FAIL', 'Closed by user'])
                return self.abort()

            self.test_data["script_log"].append(['', 'Prompt PowerAmp', 'OK', ''])
            break

        # todo: create data directories here
        try:
            list_of_paths = self.config["Paths"]
            for x in range(len(list_of_paths)):
                directory_to_check = list_of_paths[x][1]
                if not os.path.exists(directory_to_check):
                    os.makedirs(directory_to_check)
            self.test_data["script_log"].append(['', 'CreateDataDirectories', 'OK', ''])
        except Exception as e:
            self.test_data["script_log"].append(['', 'CreateDataDirectories', f'FAIL {e}', ''])

        try:
            self.log("Checking ability to log")
            self.test_data["script_log"].append(['', 'Create h/w log', 'OK', ''])
        except Exception as e:
            self.test_data["script_log"].append(['', 'Create h/w log', f'FAIL {e}', ''])

        # todo: initialize results FGV here
        try:
            self.test_data["script_log"].append(['', 'Initialize results FGV', 'OK', ''])
        except Exception as e:
            self.test_data["script_log"].append(['', 'Initialize results FGV', f'FAIL {e}', ''])

        # todo: duplicate main script?
        try:
            self.test_data["script_log"].append(['', 'duplicate main script', 'OK', ''])
        except Exception as e:
            self.test_data["script_log"].append(['', 'Duplicate main script', f'FAIL {e}', ''])

        while True:
            water_level = self.IO_Board.get_water_level()
            if not water_level == 'level':  # if the water level is not level
                # launch the dialog box signifying this issue
                self.user_prompt_signal_water_too_low_signal.emit(water_level)
                try:
                    self.wait_for_cont()
                    filled_successfully = self.IO_Board.fill_tank()
                except AbortException:
                    self.test_data["script_log"].append(['', 'Check/prompt water level', 'FAIL', 'Closed by user'])
                    return self.abort()
            else:
                self.test_data["script_log"].append(['', 'Check/prompt water level', 'OK', ''])
                break

        self.step_complete = True

    '''Retrieve metadata from mainwindow and trigger the script to run'''

    @pyqtSlot(dict)
    def pretest_metadata_slot(self, pretest_metadata):
        # reset test data to default values
        self.test_data = blank_test_data()
        self.test_data.update(pretest_metadata)
        self.run_script()

    def element_str_to_int(self, element_str):
        try:
            self.element = int(re.search(r'\d+', str(element_str)).group())
        except:
            self.log(f"Element number not given, using previous element: {self.element}")
        return self.element

    '''Find UA element with given number'''

    def find_element(self, var_dict):
        self.element = self.element_str_to_int(var_dict['Element'])
        x_increment_MM = float(var_dict['X Incr. (mm)'])
        XPts = int(var_dict['X #Pts.'])
        thetaIncrDeg = float(var_dict['Theta Incr. (deg)'])
        thetaPts = int(var_dict['Theta #Pts.'])
        scope_channel = int(var_dict['Scope channel'][8:])
        acquisition_type = var_dict['Acquisition type']
        averages = int(re.search(r'\d+', str(var_dict['Averages'])).group())
        # todo: add data storage
        data_storage = var_dict['Data storage']
        storage_location = var_dict['Storage location']
        data_directory = var_dict["Data directory"]
        maxPosErrMM = float(var_dict["Max. position error (+/- mm)"])
        elemPosTest = bool(var_dict["ElementPositionTest"])

        self.test_data["script_log"].append(['Find element "n"', 'OK', '', ''])

        try:  # at this point in the script, the checks have been performed already in pretest_initialization so no need to wrap in if statements
            self.test_data["script_log"].append(['', 'PreChecks',
                                                 f'Tank fill status {self.IO_Board.get_water_level()}, UA pump status '
                                                 f'{self.IO_Board.get_pump_reading()}', ''])
        except Exception as e:
            self.test_data["script_log"].append(['', 'PreChecks', f'FAIL {e}', ''])

        # Update UI visual to reflect the element we are on
        self.element_number_signal.emit(str(self.element))

        element_x_coordinate = self.element_x_coordinates[self.element]
        element_r_coordinate = self.element_r_coordinates[self.element]
        print(f"Finding element {self.element}, near coordinate x = {element_x_coordinate}, r = {element_r_coordinate}")

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

            time, voltage = self.capture_scope(scope_channel)

            if not data_storage.upper() == 'Do not store'.upper():
                x_sweep_waveforms.append([voltage, time])

            rms = self.find_rms(time_s=time, voltage_v=voltage)

            if rms > x_max_rms:
                x_max_rms = rms
                x_max_position = position

            x_positions.append(position)
            x_rms_values.append(rms)
            self.profile_plot_signal.emit(x_positions, x_rms_values, 'Distance (mm)')

        self.test_data["script_log"].append(
            ['', 'Move to element', f"Moved to X={position}, Th={self.Motors.coords_mm[1]}", ''])

        self.AWG.SetOutput(True)
        self.test_data["script_log"].append(['', "Config UA and FGen", "FGen output enabled", ''])

        self.log(f"Maximum of {x_max_rms} @ x = {x_max_position} mm. Going there.")

        # update element x position
        self.element_x_coordinates[self.element] = x_max_position

        status = self.Motors.go_to_position(['X'], [x_max_position])

        self.autoset_timebase(var_dict)  # script log updated in this method

        self.test_data["script_log"].append(['', 'ScanX Find Peak X:',
                                             f'Start X {self.element_x_coordinates[self.element]} mm; Incr X '
                                             f'{x_increment_MM} mm; #Points {XPts}; Peak X = {x_max_position} '
                                             f'mm; moved to X = {x_max_position} mm'])

        # todo: test this to make sure it triggers if and only if the movement fails
        if not status:
            self.log(level="error", message="Motor movement not successful")
            if self.config["Debugging"]["end_script_on_errors"]:
                self.abort()
                return

        self.test_data["X sweep waveforms"] = x_sweep_waveforms

        # Loop over r through a given range, move to the position where maximal RMS voltage was measured
        r_sweep_waveforms = list()
        position = -1 * (thetaPts * thetaIncrDeg) / 2 + self.config["WTF_PositionParameters"]["ThetaHomeCoord"]

        # begin with arbitrarily low values
        r_max_rms = -1 * sys.float_info.max
        r_max_position = -1 * sys.float_info.max

        r_positions = list()
        r_rms_values = list()

        for i in range(thetaPts):
            # check if the script has been aborted
            if self.step_index == -1:
                return

            self.Motors.go_to_position(['R'], [position])
            position = position + thetaIncrDeg

            voltage, time = self.capture_scope(channel=scope_channel)
            if not data_storage.upper() == 'Do not store'.upper():
                r_sweep_waveforms.append([voltage, time])

            rms = self.find_rms(time_s=time, voltage_v=voltage)

            if rms > r_max_rms:
                r_max_rms = rms
                r_max_position = position

            r_positions.append(position)
            r_rms_values.append(rms)
            self.profile_plot_signal.emit(r_positions, r_rms_values, 'Angle (deg)')

        self.test_data["script_log"].append(['', 'Home theta', 'Home Theta', ''])

        self.Motors.go_to_position(['R'], [r_max_position])
        self.test_data["Theta sweep waveforms"] = r_sweep_waveforms

        self.log(f"Maximum of {r_max_rms} @ theta = {r_max_position} degrees. Going there.")
        self.test_data["script_log"].append(['', 'Scan theta',
                                             f'Start {self.element_r_coordinates[self.element]} deg; Incr {x_increment_MM} deg; #Points {thetaPts}; Peak theta = {r_max_position} deg',
                                             ''])
        self.test_data["script_log"].append(['', 'Home theta', 'Home Theta', ''])
        self.test_data["script_log"].append(
            ['', 'Move to theta max', f'Move to peak: {x_max_position}_{r_max_position}', ''])

        # update element r position
        self.element_r_coordinates[self.element] = r_max_position

        # update results summary
        self.test_data['results_summary'][self.element - 1][1] = "%.2f" % x_max_position
        self.test_data['results_summary'][self.element - 1][2] = "%.2f" % r_max_position
        self.AWG.SetOutput(False)
        self.test_data["script_log"].append(['', 'Disable UA and FGen', 'Disabled FGen output', ''])
        self.test_data["script_log"].append(['', 'End', 'OK', ''])

        self.step_complete = True

    '''Save scan results to a file'''

    def save_results(self, var_dict):  # calibration_data is the data gathered by the UA test
        save_summary_file = bool(distutils.util.strtobool(var_dict["Save summary file"]))
        write_uac_calibration = bool(distutils.util.strtobool(var_dict["Write UA Calibration"]))
        prompt_for_calibration_write = bool(distutils.util.strtobool(var_dict["PromptForCalWrite"]))

        # Todo: test
        if prompt_for_calibration_write:  # displays the "write to UA" dialog box if this variable is true
            # Todo: populate calibration data from test data in useful_methods
            calibration_data = generate_calibration_data(self.test_data)
            self.test_data["write_result"] = self.write_cal_data_to_ua_dialog(calibration_data)
        else:
            self.test_data["write_result"] = "Not Attempted"

        self.test_data["software_version"] = self.config["Software_Version"]

        sum = 0
        count = 0
        for i in range(10):
            sum = sum + float(self.test_data['results_summary'][i][2])
            count = count + 1

        angle_average = sum / count

        self.test_data['results_summary'][10][2] = str(angle_average)

        self.save_results_signal.emit(self.test_data)

        self.step_complete = True

    '''Prompt user for action'''

    def prompt_user_for_action(self, var_dict):
        # todo: test
        prompt_type = var_dict["Prompt type"]
        self.user_prompt_signal.emit(prompt_type)
        self.wait_for_cont()
        self.step_complete = True

    '''Set function generator to desired settings'''

    def configure_function_generator(self, var_dict):
        # todo: test
        mVpp = int(var_dict["Amplitude (mVpp)"])
        fMHz = float(var_dict["Frequency (MHz)"])
        mode = var_dict["Mode"]
        output = bool(var_dict["Enable output"])
        cycles = int(var_dict["#Cycles"])
        frequency_options = var_dict["Set frequency options"]

        self.AWG.SetOutput(output)
        self.AWG.SetFrequency_Hz(int(fMHz * 1000000))
        self.AWG.SetAmplitude_V(mVpp / 1000)
        self.AWG.SetCycles(cycles)

        if mode == "N Cycle":
            self.AWG.SetBurst(True)
        else:
            self.AWG.SetBurst(False)

        self.test_data['script_log'].append(['', 'Config FGen', f'{mVpp}mVpp;{fMHz}MHz,{mode}'])

    def configure_oscilloscope_channels(self, var_dict):
        # todo: implement and test
        pass

    def configure_oscilloscope_timebase(self, var_dict):
        # todo: implement and test
        pass

    def autoset_timebase(self, var_dict):
        usdiv = 0
        dt = 0
        self.test_data['script_log'].append(['', 'AutoSetTimebase', f'{usdiv} usdiv;dt={dt} us'])

    '''Return axis to zero coordinate'''

    def home_system(self, var_dict):
        # TODO: have this be called in pretest_initialization and have it add to script log
        axis_to_home = var_dict['Axis to home']
        if axis_to_home == 'X':
            self.retracting_ua_warning_signal.emit()  # launch the retracting UA in the x direction warning box
            self.Motors.go_home_1d('X')
            try:
                self.wait_for_cont()
            except AbortException:
                self.test_data['script_log'].append(['', f'HOME {axis_to_home}', 'FAIL', 'Warning closed by user'])
                return self.abort()
        elif axis_to_home == 'All Axes':
            self.Motors.go_home()
        elif axis_to_home == 'Theta':
            self.Motors.go_home_1d('R')

        self.step_complete = True
        # self.test_data["script_log"].append(['', "Home all", f"X={X}; Theta={theta}", ''])

    '''Warn the user that the UA is being retracted in x'''

    def retract_ua_warning(self):
        self.retracting_ua_warning_signal.emit()

    '''Move motors to the specified coordinates'''

    def move_system(self, var_dict):
        self.element = self.element_str_to_int(var_dict['Element'])
        target = var_dict["Orientation/target"]

        element_x_coordinate = self.element_x_coordinates[self.element]
        element_r_coordinate = self.element_x_coordinates[self.element]

        # todo: make sure these names match theirs
        # todo: make sure these home coordinates work as expected
        if "Hydrophone" in target:
            self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, 0])
        elif "RFB" in target:
            self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, element_r_coordinate])
        elif "Down" in target:
            self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, -90])

        x_coord_str = "%.2f" % element_x_coordinate
        r_coord_str = "%.1f" % element_r_coordinate
        self.log(f"Moved to {self.element}, at coordinate x={x_coord_str}, r={r_coord_str}")

        self.test_data['script_log'].append(["", "Move to element", f"moved to X={x_coord_str}, Th={r_coord_str}", ''])

    '''Activate the relay for and move to a specified element'''

    def select_ua_channel(self, var_dict):
        self.element = self.element_str_to_int(var_dict['Channel (0=All off)'])
        self.IO_Board.activate_relay_channel(channel_number=self.element)

    def frequency_sweep(self, var_dict):
        # todo: add test to results summary if include_test is True
        # todo: using this setting to decide where to put it (Low frequency or High frequency)
        frequency_range = var_dict["Frequency range"]
        start_freq_MHz = var_dict["Start frequency (MHz)"]
        end_freq_MHz = var_dict["Start frequency (MHz)"]
        coarse_incr_MHz = var_dict["Coarse increment (MHz)"]
        fine_incr_MHz = var_dict["Fine increment (MHz)"]
        burst_count = var_dict["Burst count"]
        amplitude_mVpp = var_dict["Amplitude (mVpp)"]
        scope_channel = var_dict["Scope channel"]
        acquisition_type = var_dict["Acquisition type"]
        averages = var_dict["Averages"]
        data_storage = var_dict["Data storage"]
        # todo: implement these settings
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        peak_VSI_threshold = var_dict["Peak VSI threshold"]
        include_test = var_dict["Include test"]

        self.AWG.SetOutput(True)
        self.AWG.SetAmplitude_V(amplitude_mVpp / 1000)
        self.AWG.SetBurst(True)

        if acquisition_type == "Single Waveform":
            self.Oscilloscope.SetAveraging(1)
        else:
            self.Oscilloscope.SetAveraging(averages)

        coarse_freq_MHz_list, coarse_VSI_list = self.run_frequency_sweep(start_freq_MHz, end_freq_MHz, coarse_incr_MHz,
                                                                         burst_count, scope_channel=scope_channel)

        # todo: enable this in a way that makes sense and add it to the output file
        # fine_freq_MHz_list, fine_VSI_list = self.run_frequency_sweep(start_freq_MHz,end_freq_MHz,fine_incr_MHz,
        #                                                             burst_count, scope_channel = scope_channel)

        if not data_storage == "Do not store":
            if storage_location == "UA results directory":
                path = self.config['Paths']['UA results root directory'] + "\\" + self.test_data[
                    "serial_number"] + "-" + \
                       self.test_data["test_date_time"] + "-frequency_sweep_data.csv"  # retrieve path
            else:
                path = data_directory + "\\" + self.test_data["serial_number"] + "-" + \
                       self.test_data["test_date_time"] + "-frequency_sweep_data.csv"  # retrieve path

            self.log(f"Saving results summary to: {path}")

            if not os.path.exists(os.path.dirname(path)):
                self.log("creating results path...")
                os.makedirs(os.path.dirname(path))

            f = open(path, "w")

            f.write("Frequency (MHz), Voltage squared integral")
            for i in range(len(coarse_freq_MHz_list)):
                f.write(f"{coarse_freq_MHz_list[i]},{coarse_VSI_list[i]}")

    def run_frequency_sweep(self, lower_limit_MHz, upper_limitMHz, freq_step, bursts, scope_channel=1):
        list_of_VSIs = list()
        list_of_frequencies_MHz = list()

        for x in np.arange(lower_limit_MHz, upper_limitMHz, freq_step):
            self.AWG.SetFrequency_Hz(x * 1000000)  # set frequency accoding to step (coarse/fine) and x incremenet
            # add the frequency to the list
            # Find the average rms voltage at a given frequency
            rms_sum = 0
            for i in range(bursts):
                times_s, voltages_v = self.capture_scope(
                    channel=1)  # populates times_s and voltages_v with set frequency
                rms = self.find_rms(times_s, voltages_v)
                rms_sum = rms_sum + rms
            rms_avg = rms_sum / bursts

            list_of_frequencies_MHz.append(x)
            list_of_VSIs.append(rms_avg)

        assert len(list_of_VSIs) == len(list_of_frequencies_MHz)

        self.profile_plot_signal.emit(list_of_frequencies_MHz, list_of_VSIs, "Frequency (Hz)")
        # frequencies will be on the x-axis
        return (list_of_frequencies_MHz, list_of_VSIs)

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

    '''Measure the efficiency of an element'''

    def measure_element_efficiency_rfb(self, var_dict):
        self.test_data["script_log"].append(['Measure element efficiency (RFB)', 'OK', '', ''])

        try:
            # Todo: add those checks anyway just because the script may vary

            # at this point in the script, the checks have been performed already in pretest_initialization so no
            # need to wrap in if statements
            self.test_data["script_log"].append(['', 'PreChecks',
                                                 f'Tank fill status {self.IO_Board.get_water_level()}, UA pump status '
                                                 f'{self.IO_Board.get_pump_reading()}',
                                                 ''])
        except Exception as e:
            self.test_data["script_log"].append(['', 'PreChecks', f'FAIL {e}', ''])

        # Todo: implement zeroing such that balance reading subtracts the averaging reading when the balance is off
        try:
            self.element = int(re.search(r'\d+', str(var_dict['Element'])).group())
        except:
            self.log(f"Element number not given, using current element: {self.element}")

        self.element_number_signal.emit(str(self.element))

        self.select_ua_channel(var_dict={"Channel (0=All off)": var_dict['Element']})
        self.move_system(var_dict={"Element": var_dict['Element'], "Orientation/target": 'RFB'})

        frequency_range = var_dict['Frequency range']
        self.test_data["script_log"].append(['', 'Set frequency range', f"\"{frequency_range}\" range set", ''])
        on_off_cycles = int(var_dict['RFB.#on/off cycles'])
        rfb_on_time = float(var_dict['RFB.On time (s)'])
        rfb_off_time = float(var_dict['RFB.Off time (s)'])

        if frequency_range == "High frequency":
            frequency_Hz = self.test_data['high_frequency_MHz'] * 1000000
        elif frequency_range == "Low frequency":
            frequency_Hz = self.test_data['low_frequency_MHz'] * 1000000
        else:
            self.log("Improper frequency set, defaulting to low frequency")
            frequency_Hz = self.parent.ua_calibration_tab.Low_Frequency_MHz * 1000000

        self.AWG.SetFrequency_Hz(frequency_Hz)
        self.test_data['script_log'].append(
            ['', 'Configure FGen+PwrMeters', f"Frequency set to {frequency_Hz / 1000000} MHz", ''])

        self.Balance.zero_balance_instantly() #todo:see if we need this

        forward_powers_w = list()
        forward_powers_time_s = list()
        reflected_powers_w = list()
        reflected_powers_time_s = list()
        acoustic_powers_w = list()
        acoustic_powers_time_s = list()

        awg_on = list()

        startTime = t.time()
        current_cycle = 1

        self.test_data['script_log'].append(['', 'Start RFB Acquisition', 'Started RFB Action', ''])

        while current_cycle <= on_off_cycles:
            cycle_start_time = t.time()
            # Turn on AWG
            self.log("Turning off AWG")
            self.AWG.SetOutput(False)
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

            #  turn on awg
            self.log("Turning on AWG")
            self.AWG.SetOutput(True)

            while t.time() - cycle_start_time < rfb_on_time + rfb_off_time:  # for the duration of rfb on time
                if self.step_index == -1:
                    return

                forward_power_w = self.Forward_Power_Meter.get_reading() + 0.732  # Todo: remove Demo only
                forward_powers_w.append(forward_power_w)
                forward_powers_time_s.append(t.time() - startTime)

                reflected_power_w = self.Reflected_Power_Meter.get_reading() + .07  # Todo: remove, Demo only
                reflected_powers_w.append(reflected_power_w)
                reflected_powers_time_s.append(t.time() - startTime)

                balance_reading = self.Balance.get_reading()
                if balance_reading is not None:
                    balance_reading = balance_reading + .052  # Todo: remove, Demo only
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
        self.test_data["script_log"].append(['', 'Run on/off sequence', 'RFB Acquisition complete', ''])
        self.test_data["script_log"].append(['', 'Stop RFB Acquisition', "RFB Stopped, data saved", ''])

        # List containing all readings while AWG was on
        acoustic_power_on_data = get_awg_on_values(acoustic_powers_w, awg_on)
        # Mean acoustic power while on
        acoustic_power_on_mean = sum(acoustic_power_on_data) / len(acoustic_power_on_data)

        # List containing all readings while AWG was on
        forward_power_on_data = get_awg_on_values(forward_powers_w, awg_on)
        # Mean acoustic power while on
        forward_power_on_mean = sum(forward_power_on_data) / len(forward_power_on_data)

        if forward_power_on_mean != 0:
            effeciency_percent = acoustic_power_on_mean / forward_power_on_mean
        else:
            effeciency_percent = 0

        # List containing all readings while AWG was on
        reflected_power_on_data = get_awg_on_values(reflected_powers_w, awg_on)
        # Mean acoustic power while on
        reflected_power_on_mean = sum(reflected_power_on_data) / len(reflected_power_on_data)

        if forward_power_on_mean != 0:
            reflected_power_percent = reflected_power_on_mean / forward_power_on_mean
        else:
            reflected_power_percent = 1

        forward_power_max = max(forward_power_on_data)

        water_temperature = self.thermocouple.get_reading()

        if frequency_range == "High frequency":
            # High frequency
            self.test_data['results_summary'][self.element - 1][5] = "%.2f" % (frequency_Hz / 1000000)
            # HF effeciency (%)
            self.test_data['results_summary'][self.element - 1][11] = "%.0f" % effeciency_percent
            self.test_data['results_summary'][self.element - 1][12] = "%.1f" % reflected_power_percent
            self.test_data['results_summary'][self.element - 1][13] = "%.1f" % forward_power_max
            self.test_data['results_summary'][self.element - 1][14] = "%.1f" % water_temperature
        else:  # Default to low frequency
            # Low Frequency
            self.test_data['results_summary'][self.element - 1][3] = "%.2f" % (frequency_Hz / 1000000)
            # LF effeciency (%)
            self.test_data['results_summary'][self.element - 1][7] = "%.0f" % effeciency_percent
            self.test_data['results_summary'][self.element - 1][8] = "%.1f" % reflected_power_percent
            self.test_data['results_summary'][self.element - 1][9] = "%.1f" % forward_power_max
            self.test_data['results_summary'][self.element - 1][10] = "%.1f" % water_temperature

        self.element_number_signal.emit(str(self.element))
        self.step_complete = True

        temp_var_for_next_command = var_dict["Pf max (limit, W)"]
        self.test_data["script_log"].append(['', "Pass/Fail test",
                                             f"Element_{self.element};Pf (W)={forward_power_on_mean};Pr (W)="
                                             f"{reflected_power_on_mean};Pa (W)={acoustic_power_on_mean};Efficiency (%)"
                                             f"={effeciency_percent};RF_Reflection (%)={reflected_power_percent};"
                                             f"Pf Max (W)={forward_power_max};WaterTemp (C)={water_temperature};"
                                             f"Test result=placeholder;Pf Max limit (W)={temp_var_for_next_command}",
                                             ''])

        self.test_data["script_log"].append(['', 'End', '', ''])

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


class AbortException(Exception):
    pass
