from datetime import date

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

from Utilities.useful_methods import log_msg
import os
from definitions import ROOT_DIR

balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

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

    step_number_signal = pyqtSignal(int)
    expand_step_signal = pyqtSignal(int)

    element_number_signal = pyqtSignal(str)

    script_info_signal = pyqtSignal(list)

    plot_signal = pyqtSignal(object, object)

    logger_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    # Tab signal
    profile_plot_signal = pyqtSignal(list, list, str)
    plot_signal = pyqtSignal(list, list, float) #float is refresh rate
    rfb_plot_signal = pyqtSignal(list,list,list,list,list)

    Motors = None

    def __init__(self, parent: Optional[QObject], config: dict):
        super().__init__(parent=parent, objectName=u"manager_thread")
        self.get_position_cooldown_s = .2  # decreasing this improves the refresh rate of the position, at the cost of responsiveness
        self.last_get_position_time = 0
        self.app = QApplication.instance()
        self.scan_data = dict()

        # Used to prevent other threads from accessing the motor class
        self.motor_control_lock = QMutex()

        self.freq_highlimit_hz = None
        self.freq_lowlimit_hz = None
        self.parent = parent
        self.stay_alive = True

        self.config = config

        # Stores latest command to be executed in the event loop
        self.cmd = ''

        # Event loop control vars
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # Test Data
        self.test_data = None

        # Test Metadata
        self.test_comment = ""
        self.ua_serial_number = ""
        self.operator_name = ""

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
            if cmd_ray[0] == 'LOAD':
                log_msg(self, root_logger, level='info', message="Loading script")
                try:
                    cmd_ray.pop(0)
                    path = ' '.join(cmd_ray)
                    self.load_script(path)
                except Exception as e:
                    log_msg(self, root_logger, "info", f"Error in load script: {e}")
            elif cmd_ray[0] == 'RUN':
                log_msg(self, root_logger, level='info', message="Running script")
                self.abort()
                self.scripting = True
            elif cmd_ray[0] == 'CLOSE':
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
        if not self.parent.plot_ready:
            return
        if not self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex()) == 'Scan':
            return

        tabs = self.parent.scan_tab_widget.scan_tabs

        if not tabs.tabText(tabs.currentIndex()) == "1D Scan":
            return

        # The plot exists in the parent MainWindow Class, but has been moved to this Qthread
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
        taskVars = OrderedDict()  # the list of variables for the individual task
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

        self.scripting = False

    # Updates script step and executes the next step if applicable, and implements abort, continue, and retry
    def advance_script(self):
        if self.scripting is False:
            return

        if self.retry_var is True:
            self.step_index = self.step_index - 1
            self.step_complete = True
            self.retry_var = False  # sets the retry variable to false so the retry function can happen again

        # advance to the next step if the previous has been completed
        if self.scripting and self.step_complete:
            self.step_index = self.step_index + 1

        # if a script is being executed, and the step index is valid, and the previous step is complete,
        # run the next script step

        if self.taskArgs is not None and self.taskNames is not None and self.taskExecOrder is not None:
            if self.scripting and 0 <= self.step_index < len(self.taskNames):

                if self.step_complete:
                    self.step_complete = False
                    self.execute_script_step(self.step_index)
        elif self.step_index >= len(self.taskNames):
            self.abort()

    '''Executes script step with given step index in taskNames/taskArgs'''

    def execute_script_step(self, step_index):
        if self.taskArgs is None or self.taskNames is None or self.taskExecOrder is None:
            self.abort()
            return

        name = self.taskNames[step_index]  # sets name (str) to current iteration in taskNames list
        args = self.taskArgs[step_index]  # sets args (list) to current iteration in taskArgs list

        self.step_number_signal.emit(step_index - 1)
        t.sleep(.1)

        self.expand_step_signal.emit(self.taskExecOrder[step_index][0])

        if not self.taskExecOrder[step_index][1] is None:  # if the element in the self.taskExecOrder isn't None
            # below: set the element to be operated on to the one in self.taskExecOrder
            args['Element'] = self.taskExecOrder[step_index][1]

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

        self.step_number_signal.emit(step_index)

        # below: this should allow for the retry function by setting the iteration variable backwards 1
        # so when it gets incremented it returns to the previous position

    '''Aborts script'''

    @pyqtSlot()
    def abort(self):
        self.log('Aborting script')
        # Reset script control variables
        self.scripting = False
        self.step_index = -1
        self.step_complete = True
        self.continue_var = True
        self.step_number_signal.emit(-1)

        # Todo: add option to save before exiting

        self.erase_metadata()

    def erase_metadata(self):
        self.ua_serial_number = None
        self.test_comment = None
        self.operator_name = None

    '''Sets continue variable to False and waits for it to be true, disabling scripting if abort_var is true'''

    def wait_for_cont(self):
        self.continue_var = False
        while not self.continue_var:
            if self.scripting == False:
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
        today = date.today()
        formatted_date = today.strftime("%m/%d/%Y")

        # Show dialog until name and serial number are input
        while self.operator_name == "" or self.ua_serial_number == "":
            self.pretest_dialog_signal.emit(
                formatted_date)  # sends signal from manager to MainWindow to open dialog box
            try:
                self.wait_for_cont()
            except AbortException:
                return self.abort()

        # Show dialogs until pump is on and the water sensor reads level
        while True:
            if not self.IO_Board.get_pump_reading() == True:  # if the pump is not running
                # launch the dialog box signifying this issue
                self.user_prompt_pump_not_running_signal.emit(pump_status)
                try:
                    self.wait_for_cont()
                except AbortException:
                    return self.abort()
            else:
                water_level = self.IO_Board.get_water_level()
                if not water_level == 'level':  # if the water level is not level
                    # launch the dialog box signifying this issue
                    self.user_prompt_signal_water_too_low_signal.emit(water_level)
                    try:
                        self.wait_for_cont()
                    except AbortException:
                        return
                else:
                    break

        self.step_complete = True

    '''latches info from user in MainWindow to manager local vars'''

    @pyqtSlot(str, str, str)
    def pretest_info_slot(self, operator_name, ua_serial_no, comment):
        self.operator_name = operator_name
        self.ua_serial_number = ua_serial_no
        self.test_comment = comment

        self.cont()

    '''Find UA element with given number'''

    def find_element(self, variable_list):
        try:
            element = int(variable_list['Element'])
        except ValueError:
            element = int(variable_list['Element'][8:])

        x_increment_MM = float(variable_list['X Incr. (mm)'])
        XPts = int(variable_list['X #Pts.'])
        thetaIncrDeg = float(variable_list['Theta Incr. (deg)'])
        thetaPts = int(variable_list['Theta #Pts.'])
        scope_channel = int(variable_list['Scope channel'][8:])
        acquisition_type = variable_list['Acquisition type']
        # Todo: implement averaging
        averages = int(variable_list['Averages'])
        data_storage = variable_list['Data storage']
        storage_location = variable_list['Storage location']
        data_directory = variable_list["Data directory"]
        maxPosErrMM = float(variable_list["Max. position error (+/- mm)"])
        elemPosTest = bool(variable_list["ElementPositionTest"])

        # Loop over x through a given range, move to the position where maximal RMS voltage was measured
        x_sweep_waveforms = list()
        position = -1 * self.config["WTF_PositionParameters"]["X-Element pitch (mm)"] / 2
        x_max_rms = -1
        x_max_position = 0
        x_positions = list()
        x_rms_values = list()

        for i in range(XPts):
            self.Motors.go_to_position(['X'], [position])
            position = position + x_increment_MM

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

        status = self.Motors.go_to_position(['X'], [x_max_position])

        if not status and self.config["debugging"]["end_script_on_errors"]:
            self.abort()
            return

        self.scan_data["X sweep waveforms"] = x_sweep_waveforms

        # Loop over r through a given range, move to the position where maximal RMS voltage was measured
        r_sweep_waveforms = list()
        position = self.config["WTF_PositionParameters"]["ThetaPreHomeMove"]
        r_max_rms = -1
        r_max_position = 0
        r_positions = list()
        r_rms_values = list()

        for i in range(thetaPts):
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

        self.element_number_signal.emit(str(element))
        self.step_complete = True

    '''Measure the efficiency of an element'''

    def measure_element_efficiency_rfb(self, variable_list):
        element = variable_list['Element']
        frequency_range = variable_list['Frequency range']
        on_off_cycles = int(variable_list['RFB.#on/off cycles'])
        rfb_on_time = float(variable_list['RFB.On time (s)'])
        rfb_off_time = float(variable_list['RFB.Off time (s)'])

        five_sec_incr_counter = 0

        current_cycle = 1

        if frequency_range == "High frequency":
            frequency_Hz = self.parent.ua_calibration_tab.High_Frequency_MHz * 1000000
        elif frequency_range == "Low frequency":
            frequency_Hz = self.parent.ua_calibration_tab.Low_Frequency_MHz * 1000000

        else:
            print("Improper frequency set, defaulting to low frequency")
            frequency_Hz = self.parent.ua_calibration_tab.Low_Frequency_MHz * 1000000

        self.AWG.SetFrequency_Hz(frequency_Hz)
        self.AWG.SetOutput(False)

        self.Balance.zero_balance_instantly()

        startTime = t.time()
        five_sec_start_time = t.time()

        times_s = list()
        forward_powers_w = list()
        reflected_powers_w = list()
        balance_readings_g = list()
        oscilloscope_amplitudes= list()

        while current_cycle <= on_off_cycles:
            self.AWG.SetOutput(True)
            cycle_on_start_time = t.time()

            if t.time() - five_sec_start_time >= 5000:
                five_sec_start_time = t.time()
                # every 5 seconds
                five_sec_incr_counter = five_sec_incr_counter + 1

            while t.time() - cycle_on_start_time < rfb_on_time:  # for the duration of rfb on time
                reflected_powers_w.append(self.Reflected_Power_Meter.get_reading())
                forward_powers_w.append(self.Forward_Power_Meter.get_reading())
                balance_readings_g.append(self.Balance.get_reading())
                times_s,volts_v = self.Oscilloscope.capture(1)
                oscilloscope_amplitudes.append(max(volts_v))
                times_s.append(t.time()-startTime)
                self.rfb_plot_signal.emit(times_s, forward_powers_w, reflected_powers_w, balance_readings_g, oscilloscope_amplitudes)
                self.app.processEvents()
                break
        #     #  turn off awg
        #     self.AWG.SetOutput(False)
        #
        #     cycle_off_start_time = t.time()
        #
        #     while cycle_off_start_time - t.time() < rfb_off_time:  # for the duration of rfb on time
        #         reverse_power_watts = self.Reflected_Power_Meter.get_reading()
        #         self.rfb_plot_signal_plot_reverse_power.emit(reverse_power_watts, startTime - t.time())
        #         forward_power_watts = self.Forward_Power_Meter.get_reading()
        #         self.rfb_plot_signal_plot_forward_power.emit(forward_power_watts, startTime - t.time())
        #
        #     current_cycle = current_cycle + 1  # we just passed a cycle at this point in the code
        #
        # self.element_number_signal.emit(str(element))
        # self.step_complete = True

    '''Save scan results to a file'''

    def save_results(self, variable_list, calibration_data):  # calibration_data is the data gathered by the UA test
        save_summary_file = bool(distutils.util.strtobool(variable_list["Save summary file"]))
        write_uac_calibration = bool(distutils.util.strtobool(variable_list["Write UA Calibration"]))
        prompt_for_calibration_write = bool(distutils.util.strtobool(variable_list["PromptForCalWrite"]))

        if prompt_for_calibration_write:  # displays the "write to UA" dialog box if this variable is true
            self.write_cal_data_to_ua_dialog(calibration_data)

        self.step_complete = True

    '''Prompt user for action'''

    def prompt_user_for_action(self, variable_list):
        prompt_type = variable_list["Prompt type"]
        self.step_complete = True

    '''Return axis to zero coordinate'''

    def home_system(self, variable_list):
        axis_to_home = variable_list['Axis to home']
        if axis_to_home == 'X':
            self.retracting_ua_warning_signal.emit()  # launch the retracting UA in the x direction warning box
            try:
                self.wait_for_cont()
            except AbortException:
                return self.abort()

        # TODO: have the pump home in the desired direction

        self.step_complete = True

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
