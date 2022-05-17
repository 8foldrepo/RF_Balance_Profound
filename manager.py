import distutils.util
import logging
import os
import re
import sys
import time as t
from collections import OrderedDict
from statistics import mean
from typing import List

import numpy as np
import pyvisa
from PyQt5.QtCore import QMutex, QThread, QWaitCondition, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication
from scipy import integrate

from Hardware.Abstract.abstract_awg import AbstractAWG
from Hardware.Abstract.abstract_balance import AbstractBalance
from Hardware.Abstract.abstract_device import AbstractDevice
from Hardware.Abstract.abstract_io_board import AbstractIOBoard
from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
from Hardware.Abstract.abstract_oscilloscope import AbstractOscilloscope
from Hardware.Abstract.abstract_sensor import AbstractSensor
from Hardware.Abstract.abstract_ua_interface import AbstractUAInterface
from Utilities.FileSaver import FileSaver
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.rfb_data_logger import RFBDataLogger
from Utilities.useful_methods import log_msg, get_element_distances, generate_calibration_data
from data_structures.rfb_data import RFBData
from data_structures.test_data import TestData
from data_structures.variable_containers import FileMetadata, SystemInfo
from definitions import ROOT_DIR, WaterLevel, FrequencyRange

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger("wtf_log")
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode="w")
file_handler.setFormatter(log_formatter)
wtf_logger.addHandler(file_handler)
wtf_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

pump_status = ""
tank_status = ""


class Manager(QThread):
    # Devices
    devices: List[AbstractDevice]
    AWG: AbstractAWG
    Balance: AbstractBalance
    IO_Board: AbstractIOBoard
    Forward_Power_Meter: AbstractSensor
    Reflected_Power_Meter: AbstractSensor
    thermocouple: AbstractSensor
    Oscilloscope: AbstractOscilloscope
    Motors: AbstractMotorController
    UAInterface: AbstractUAInterface

    # Output file handler
    file_saver: FileSaver
    rfb_logger: RFBDataLogger

    # Used for polling sensors while software is idle
    sensor_refresh_interval_s: float
    last_sensor_update_time: float

    # Signal section
    # Dialog signals
    user_prompt_signal = pyqtSignal(str,
                                    bool)  # str is message for user to read, bool is whether or not to restrict the continue button
    user_prompt_pump_not_running_signal = pyqtSignal(str)  # str is pump status
    user_prompt_signal_water_too_low_signal = pyqtSignal()  # str is water level
    user_prompt_signal_water_too_high_signal = pyqtSignal()
    write_cal_data_to_ua_signal = pyqtSignal(list)  # list is 2d array of calibration data
    retracting_ua_warning_signal = pyqtSignal()
    script_complete_signal = pyqtSignal(list, list)  # Contains a pass/fail list of booleans and a list of descriptions
    user_info_signal = pyqtSignal(str)

    system_info_signal = pyqtSignal(SystemInfo)

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
    enable_ui_signal = pyqtSignal(bool)

    # Tab signal
    profile_plot_signal = pyqtSignal(list, list, str)
    plot_signal = pyqtSignal(list, list, float)  # float is refresh rate

    update_rfb_tab_signal = pyqtSignal()
    # contains

    # sets the current tab text of the main window (must match a tab name of the main window
    set_tab_signal = pyqtSignal(str)

    Motors = None

    # Global variables section

    def __init__(self, system_info, config: dict, parent=None):
        """Initializes various critical variables for this class, as well as setting thread locking mechanisms."""
        super().__init__(parent=parent)
        self.oscilloscope_channel = 1
        self.last_rfb_update_time = t.time()
        self.access_level = "Operator"  # Defaults to operator access
        self.rfb_logger = None  # TODO: should this be self.rfb_logger = RFBDataLogger?
        self.warn = str(logging.WARNING)  # sets variable for shorter typing
        self.error = str(logging.ERROR)  # sets variable for shorter typing
        # decreasing these values improves the refresh rate of the sensors at the cost of responsiveness
        self.sensor_refresh_interval_s = 0.2
        self.last_sensor_update_time = 0.0

        self.config = config
        self.system_info = system_info

        self.app = QApplication.instance()
        self.test_data = TestData()
        self.file_saver = FileSaver(config=self.config)

        self.element_x_coordinates = get_element_distances(
            element_1_index=self.config["WTF_PositionParameters"]["X-Element1"],
            element_pitch=self.config["WTF_PositionParameters"]["X-Element pitch (mm)"],
        )

        # put a none at position zero because there is no element zero
        self.element_r_coordinates = [None]
        # fill in default theta home coordinates
        for i in range(10):
            self.element_r_coordinates.append(
                self.config["WTF_PositionParameters"]["ThetaHomeCoord"]
            )

        # Used to prevent other threads from accessing the motor class
        self.motor_control_lock = QMutex()
        self.start_time = t.time()
        self.loops = []
        self.frequency_high_limit_Hz = None
        self.frequency_low_limit_Hz = None
        self.parent = parent
        self.stay_alive = True

        # Stores the latest command to be executed in the event loop
        self.command = ""

        # Event loop control variables
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # Script file
        self.script = None

        # Script data
        self.task_arguments = None
        self.task_execution_order = None
        self.task_names = None

        self.element = 1

        # Tracks whether a script is being executed
        self.currently_scripting = False
        self.was_scripting = False

        # Flags for the wait_for_cont method, when a dialog is waiting for user action
        self.continue_clicked = True
        self.retry_clicked = False
        self.abort_clicked = False

        self.abort_immediately_var = False

        # Initializes the retry count for retry step functionality in scripts
        self.retry_count = 0

        # Keeps track of script step in progress
        # step_index = -1 if no script is being run.
        self.step_index = -1

        # ResourceManager for the oscilloscope and function generators
        self.rm = None
        self.devices = list()
        self.add_devices()

    def add_devices(self):
        """
        Import and instantiate device classes, and append them to a list. If the config says to simulate hardware,
        use the simulated class instead.
        """

        self.access_level = self.parent.access_level_combo.currentText()
        simulate_access = self.access_level.upper() != "Operator".upper()

        if self.config["Debugging"]["simulate_motors"] and simulate_access:
            from Hardware.Simulated.simulated_motor_controller import (SimulatedMotorController)
            self.Motors = SimulatedMotorController(config=self.config)
        else:
            from Hardware.parker_motor_controller import ParkerMotorController
            self.Motors = ParkerMotorController(config=self.config, lock=self.motor_control_lock)

        if self.config["Debugging"]["simulate_oscilloscope"] and simulate_access:
            from Hardware.Simulated.simulated_oscilloscope import SimulatedOscilloscope
            self.Oscilloscope = SimulatedOscilloscope(config=self.config)
        else:
            from Hardware.keysight_oscilloscope import KeysightOscilloscope
            self.rm = pyvisa.ResourceManager()
            self.Oscilloscope = KeysightOscilloscope(config=self.config, resource_manager=self.rm)

        if self.config["Debugging"]["simulate_ua_interface"] and simulate_access:
            from Hardware.Simulated.simulated_ua_interface import SimulatedUAInterface
            self.UAInterface = SimulatedUAInterface(config=self.config)
        else:
            from Hardware.ua_interface import UAInterface
            self.UAInterface = UAInterface(config=self.config)

        if self.config["Debugging"]["simulate_awg"] and simulate_access:
            from Hardware.Simulated.simulated_awg import SimulatedAWG

            self.AWG = SimulatedAWG(config=self.config)
        else:
            from Hardware.keysight_awg import KeysightAWG

            if self.rm is None:
                self.rm = pyvisa.ResourceManager()
            self.AWG = KeysightAWG(config=self.config, resource_manager=self.rm)

        if self.config["Debugging"]["simulate_balance"] and simulate_access:
            from Hardware.Simulated.simulated_balance import SimulatedBalance
            self.Balance = SimulatedBalance(config=self.config)
        else:
            from Hardware.mt_balance import MT_balance
            self.Balance = MT_balance(config=self.config)

        if self.config["Debugging"]["simulate_power_meters"] and simulate_access:
            from Hardware.Simulated.simulated_power_meter import PowerMeter

            self.Forward_Power_Meter = PowerMeter(config=self.config, device_key="Forward_Power_Meter")
            self.Reflected_Power_Meter = PowerMeter(config=self.config, device_key="Reflected_Power_Meter")
        else:
            from Hardware.mini_circuits_power_meter import PowerMeter
            self.Forward_Power_Meter = PowerMeter(config=self.config, device_key="Forward_Power_Meter")
            self.Reflected_Power_Meter = PowerMeter(config=self.config, device_key="Reflected_Power_Meter")

        if self.config["Debugging"]["simulate_io_board"] and simulate_access:
            from Hardware.Simulated.simulated_io_board import SimulatedIOBoard
            self.IO_Board = SimulatedIOBoard(config=self.config)
        else:
            from Hardware.dio_board import DIOBoard
            self.IO_Board = DIOBoard(config=self.config, simulate_sensors=self.config["Debugging"]["simulate_sensors"])

        if self.config["Debugging"]["simulate_thermocouple"]:
            from Hardware.Simulated.simulated_thermocouple import SimulatedThermocouple
            self.thermocouple = SimulatedThermocouple(config=self.config)
        else:
            from Hardware.ni_thermocouple import NIThermocouple
            self.thermocouple = NIThermocouple(config=self.config)

        self.devices.append(self.Forward_Power_Meter)
        self.devices.append(self.Reflected_Power_Meter)
        self.devices.append(self.IO_Board)
        self.devices.append(self.UAInterface)
        self.devices.append(self.Motors)
        self.devices.append(self.thermocouple)
        self.devices.append(self.Oscilloscope)
        self.devices.append(self.Balance)
        self.devices.append(self.AWG)

    @pyqtSlot()
    def connect_hardware(self):
        """Attempts to connect all hardware in the devices list, warns user if hardware could not connect and waits for their
        response. Also sets the class' oscilloscope channel and averages and emits signal to MainWindow.py"""
        i = 0
        while i < len(self.devices):
            device = self.devices[i]
            connected, feedback = device.connect_hardware()
            if not connected:
                self.user_prompt_signal.emit(f"{device.device_key} Could not connect\n\n{feedback}", False)
                try:
                    self.__wait_for_cont()
                except RetryException:
                    i = i - 1
                except AbortException:
                    self.app.exit(-1)
            i = i + 1

        self.oscilloscope_averages = self.Oscilloscope.averages
        self.oscilloscope_channel = self.Oscilloscope.channel
        self.update_system_info()
        self.enable_ui_signal.emit(True)

    def update_system_info(self):
        """
        Retrieve system info from devices, pass them to the system info tab, which overwrites systeminfo.ini
        with the info it finds
        """
        info = SystemInfo()
        info.oscilloscope_sn = self.Oscilloscope.get_serial_number()
        if info.oscilloscope_sn is None:
            self.sequence_pass_fail('Interrupt action', "Oscilloscope serial number not found")
        info.awg_sn = self.AWG.get_serial_number()
        if info.awg_sn is None:
            self.sequence_pass_fail('Interrrupt action', "AWG serial number not found")
        info.forward_power_sn = self.Forward_Power_Meter.get_serial_number()
        if info.forward_power_sn is None:
            self.sequence_pass_fail('Interrupt action', "AWG serial number not found")
        info.reflected_power_sn = self.Reflected_Power_Meter.get_serial_number()
        info.thermocouple_sn = self.thermocouple.get_serial_number()
        info.rf_balance_sn = self.Balance.get_serial_number()
        if info.rf_balance_sn is None:
            self.sequence_pass_fail('Interrupt action', "Balance serial number not found")
        self.system_info_signal.emit(info)

    @pyqtSlot()
    def disconnect_hardware(self):
        """Safely disconnect all devices"""
        self.enable_ui_signal.emit(False)
        self.abort_after_step()
        for device in self.devices:
            device.disconnect_hardware()

    def run(self) -> None:
        """
        Core event loop of the manager thread. For any other methods to be executed in the manager thread
        They must be called from this method.
        """
        QThread.currentThread().setObjectName("manager_thread")
        self.mutex.lock()
        self.start_time = t.time()

        self.stay_alive = True

        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 50)

            if self.stay_alive is False:
                break

            # code block below checks the first part of the split command_ray to see what command is
            self.command = self.command.upper()
            command_ray = self.command.split(" ")
            if command_ray[0] == "CLOSE":
                self.wrap_up()
            elif command_ray[0] == "CONNECT":
                self.connect_hardware()
            elif command_ray[0] == "CAPTURE":
                self.capture_oscilloscope_and_plot()
            elif command_ray[0] == "STEP":
                self.advance_script()
            elif command_ray[0] == "ABORT":
                self.abort_after_step()
            else:  # What to do when there is no command
                # If a script has just ended, show script_complete dialog
                if self.currently_scripting:
                    if self.task_names is None:
                        self.abort_after_step()
                        self.enable_ui_signal.emit(True)
                    else:
                        self.advance_script()
                else:
                    if self.Oscilloscope.connected and self.config["Debugging"]["oscilloscope_realtime_capture"]:
                        self.capture_oscilloscope_and_plot()
                    else:
                        pass
                    self.update_sensors()
                    if self.thermocouple.connected:
                        self.thermocouple.get_reading()

            # Show script complete dialog whenever a script finishes
            if not self.currently_scripting and self.was_scripting:
                if self.task_names is not None:
                    finished = self.step_index == len(self.task_names) - 1
                else:
                    finished = False
                self.script_complete(finished=finished)
            self.was_scripting = self.currently_scripting

            self.command = ""
        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    @pyqtSlot()
    def run_script(self):
        """Triggers when the user hits the run script button in the UI, sets various scripting variables to appropriate
        values and logs"""
        self.abort_immediately()
        log_msg(self, root_logger, level="info", message="Running script")
        self.currently_scripting = True
        self.was_scripting = True
        self.abort_immediately_var = False

    def update_sensors(self):
        """Attempts to update the last sensor update time, the water level, thermocouple reading, and ua pump status.
        Returns if the user is not looking at positional feedback"""
        if self.parent is not None and not hasattr(self.parent, "tabWidget"):
            return

        if t.time() - self.last_sensor_update_time > self.sensor_refresh_interval_s:
            self.last_sensor_update_time = t.time()

            if self.IO_Board.connected:
                self.IO_Board.get_water_level()

            if self.IO_Board.connected:
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

    def capture_scope(self, channel=1, plot=True):
        """captures time and voltage data from the oscilloscope hardware, stores them into two separate lists and returns
        them to the calling function. Defaults to channel 1 on the oscilloscope and sets the plot flag to true"""
        try:
            time, voltage = self.Oscilloscope.capture(channel=channel)
            if plot:
                self.plot_scope(time, voltage)
            return time, voltage
        except pyvisa.errors.InvalidSession:
            self.log(level='error', message="Could not capture, oscilloscope resource closed")
        except TypeError:
            self.log(level='error', message="Cold not capture")
        return [], []

    def plot_scope(self, time, voltage):
        """takes the time and voltage data (lists) from the oscilloscope and sends a signal to main window to plot them"""
        time_elapsed = t.time() - self.start_time
        if time_elapsed == 0:
            return

        refresh_rate = round(1 / time_elapsed, 1)
        self.plot_signal.emit(time, voltage, refresh_rate)

    # noinspection PyUnresolvedReferences
    def capture_oscilloscope_and_plot(self):
        """Captures an oscilloscope trace and plots it to the scan tab, assuming the plot is ready"""

        if self.oscilloscope_averages != self.Oscilloscope.averages:
            self.Oscilloscope.set_averaging(self.oscilloscope_averages)

        # Only capture if the scan tab is selected
        if not self.parent.scan_tab_widget.plot_ready:
            return
        if self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex()) != 'Scan':
            return

        time, voltage = self.capture_scope(channel=self.oscilloscope_channel)

        self.plot_scope(time, voltage)
        self.start_time = t.time()

    # noinspection PyUnresolvedReferences
    def load_script(self, path):
        """takes the script file and parses the info within it into various lists and dictionaries so the program can
         run the script, requires a path argument to the script"""
        self.abort_after_step(log=False)

        # Send name of script to UI
        split_path = path.split("/")
        self.test_data.script_name = split_path[len(split_path) - 1]
        self.script_name_signal.emit(self.test_data.script_name)

        tasks = []  # the upper layer of our task list
        self.task_execution_order = []
        element_names_for_loop = []
        task_number_for_loop = []
        current_line = -1
        loop_index_tracker = 0
        adding_elements_to_loop = False
        building_loop = False
        task_variables = OrderedDict()  # the list of variables for the individual task
        task_number = -2  # keeps track of the task number for indexing
        f = open(path, "r")
        for line in f:
            ray = line.split(" = ")

            # Populate script metadata to UI using signals
            if ray[0].upper() == "# OF TASKS":
                self.num_tasks_signal.emit(int(ray[1].replace('"', "")))
            elif ray[0].upper() == "CREATEDON":
                self.created_on_signal.emit(ray[1].replace('"', ""))
            if ray[0].upper() == "CREATEDBY":
                self.created_by_signal.emit(ray[1].replace('"', ""))
            elif ray[0].upper() == "DESCRIPTION":
                self.description_signal.emit(ray[1].replace('"', ""))

            current_line = current_line + 1
            if line == '\n':
                if task_variables:  # ensures task variable list isn't empty; prevents adding empty sub lists to main list
                    tasks.append(OrderedDict(task_variables))
                    task_variables.clear()  # empties out variable list for task since we're ready to move to the next set
                if adding_elements_to_loop:  # detects if we're done with the element name block for the loop in script
                    adding_elements_to_loop = False  # we're done with the block so set the flag to false
                continue  # move forward one line
            elif '[' in line:  # if the line we're on is a task line
                task_number = task_number + 1  # increments the task number counter since we've moved to the next task
                if "Task" in line and not building_loop:
                    self.task_execution_order.append(task_number)  # adding task number to the execution list
            else:  # above ensures we're not parsing a task header nor blank line
                x0 = ray[0].strip()  # remove trailing/leading spaces
                x1 = ray[1].strip().replace('"', "")  # does above but also removes quotation marks
                task_variables[x0] = x1  # add the temporary variable pair to the task's variable list

                if "# of Tasks" in x0:
                    number_of_tasks = x1

                if "Loop over elements" in x1:  # detects if we've encountered a loop builder task
                    building_loop = True  # set a flag that we're building a loop for the script
                    adding_elements_to_loop = True  # set a flag that we're adding element names from script for loop

                # if we're on a line that adds an element name for the loop
                if adding_elements_to_loop and "Element" in x0:
                    # split the left side of the variable assigner by space
                    element_name_to_split = x0.split(" ")
                    # retrieve the second word of the left side, that's the element name
                    element_name = element_name_to_split[1]
                    element_names_for_loop.append(int(element_name))

                if "End loop" in x1:  # script will have "End loop" in right side of task type to end loop block
                    building_loop = False  # set the building loop flag to false since the loop block is done
                    self.loops.append(list([list(element_names_for_loop), list(task_number_for_loop)]))
                    element_names_for_loop.clear()
                    task_number_for_loop.clear()
                    self.task_execution_order.pop()

                    # appends a 2 item list in taskExecOrder, the first part being the element within the loops
                    # sublist and the second item being the iteration number for that item in its loop
                    for i in range(len(self.loops[len(self.loops) - 1][0])):
                        for j in range(len(self.loops[len(self.loops) - 1][1])):
                            self.task_execution_order.append([self.loops[len(self.loops) - 1][1][j], i + 1,
                                                              loop_index_tracker])
                    loop_index_tracker = loop_index_tracker + 1

                # if we're building a loop & are not in the name adding phase
                if building_loop and not adding_elements_to_loop:

                    # ensure the task no. isn't already in the task list for the loop
                    if task_number not in task_number_for_loop:
                        # add the current task no. to the list of tasks we need to run in loop
                        task_number_for_loop.append(task_number)
        f.close()

        if task_variables:  # ensures task variable list isn't empty; prevents adding empty sub lists to main list
            tasks.append(OrderedDict(task_variables))
            task_variables.clear()  # empties out variable list for task since we're ready to move to the next set

        for i in range(len(self.task_execution_order)):  # if the task step does not have element, set the element to "None" type in order to make it a list
            if not isinstance(self.task_execution_order[i], list):
                self.task_execution_order[i] = [self.task_execution_order[i], None]

        self.task_names = list()  # makes the task_names object into a list
        for i in range(len(self.task_execution_order)):
            if "Task type" in tasks[self.task_execution_order[i][0] + 1].keys():  # tasks and task_execution_order are offset by 1
                self.task_names.append(tasks[self.task_execution_order[i][0] + 1]["Task type"])

        self.task_arguments = list()  # makes the task_arguments object into a list
        for i in range(len(self.task_execution_order)):
            # tasks[self.taskExecOrder[i][0] + 1].pop("Task type", None)
            self.task_arguments.append(tasks[self.task_execution_order[i][0] + 1])  # task_arguments and task_execution_order are offset by 1

        self.script_info_signal.emit(tasks)
        self.num_tasks_signal.emit(len(self.task_names))

    # get UA serial no. and append behind date

    @pyqtSlot()
    def advance_script(self):
        """Updates script step and executes the next step if applicable, and implements abort, continue, and retry"""
        if self.task_names is None:
            self.abort_after_step()
            self.enable_ui_signal.emit(True)
            return

        if self.retry_clicked is True:
            self.step_index = self.step_index - 1
            self.retry_clicked = False  # sets the retry variable to false so the retry function can happen again

        # advance to the next step if the previous has been completed
        self.step_index = self.step_index + 1

        # if a script is being executed, and the step index is valid, and the previous step is complete,
        # run the next script step

        if self.step_index > len(self.task_names):
            self.currently_scripting = False
            return

        if self.task_arguments is not None and self.task_names is not None and self.task_execution_order is not None:
            if 0 <= self.step_index < len(self.task_names):
                inside_iteration = False
                iteration_number = None

                if (
                        len(self.task_execution_order[self.step_index]) == 3
                ):  # elements that are a part of a loop will have a third sub element
                    # notating which loop it's from
                    self.test_data.log_script(
                        [f"Iteration {self.task_execution_order[self.step_index][1]} of "
                         f"{len(self.loops[self.task_execution_order[self.step_index][2]][0])}", "", "", "", ]
                    )
                    inside_iteration = True
                    iteration_number = self.task_execution_order[self.step_index][1]

                self.run_script_step()
                if inside_iteration:
                    self.test_data.log_script([f"Iteration {iteration_number} complete", '', '', ''])
                    inside_iteration = False

        if not self.currently_scripting:
            self.enable_ui_signal.emit(True)

    def run_script_step(self):
        """Executes script step with given step index in taskNames/taskArgs"""
        if self.task_arguments is None or self.task_names is None or self.task_execution_order is None:
            self.abort_after_step()
            self.enable_ui_signal.emit(True)
            return

        name = self.task_names[self.step_index]  # sets name (str) to current iteration in taskNames list
        args = self.task_arguments[self.step_index]  # sets args (list) to current iteration in taskArgs list

        self.task_number_signal.emit(self.task_execution_order[self.step_index][0])
        self.task_index_signal.emit(self.step_index)

        if self.task_execution_order[self.step_index][1] is not None:  # if the element in the self.taskExecOrder isn't None
            # below: set the element to be operated on to the one in self.taskExecOrder
            args['Element'] = self.task_execution_order[self.step_index][1]

        if "Measure element efficiency (RFB)".upper() in name.upper():
            self.measure_element_efficiency_rfb_multithreaded(args)
        elif name.upper() == "Pre-test initialisation".upper():
            self.pretest_initialization(args)
        elif "Find element".upper() in name.upper():
            self.find_element(args)
        elif name.upper() == "Save results".upper():
            self.save_results(args)
        elif name.upper() == "Prompt user for action".upper():
            self.prompt_user_for_action(args)
        elif "Home system".upper() in name.upper():
            self.home_system(args)
        elif "Oscilloscope Channels".upper() in name.upper():
            self.configure_oscilloscope_channels(args)
        elif "Oscilloscope Timebase".upper() in name.upper():
            self.configure_oscilloscope_timebase(args)
        elif "Function Generator".upper() in name.upper():
            self.configure_function_generator(args)
        elif "Autoset Timebase".upper() in name.upper():
            self.autoset_timebase(args)
        elif "Home System".upper() in name.upper():
            self.home_system(args)
        elif "Move System".upper() in name.upper():
            self.move_system(args)
        elif "Select Channel".upper() in name.upper():
            self.select_ua_channel(args)
            raise Exception

        self.task_index_signal.emit(self.step_index + 1)

        # below helps explain loop and list logic
        # if len(self.taskExecOrder[self.step_index]) == 3:
        #     print(f"looped element {self.taskExecOrder[self.step_index][0]} is in iteration {self.taskExecOrder
        #     [self.step_index][1]} from loop {self.loops[self.taskExecOrder[self.step_index][2]]}")

    @pyqtSlot()
    def abort_after_step(self, log=True):
        """Aborts script when current step is done running"""

        if log:
            self.log("Aborting script after step")
        # Reset script control variables
        self.currently_scripting = False
        self.step_index = -1
        self.abort_immediately_var = False
        self.task_number_signal.emit(0)
        self.task_index_signal.emit(0)
        # Todo: add option to save before exiting

    @pyqtSlot()
    def abort_immediately(self):
        """
        Aborts script as soon as the current step checks abort_immediately var and returns or the step finishes.
        Any long-running step should check abort_immediately_var frequently and return false if the var is true
        """
        log = True
        if log:
            self.log("Aborting script")
        # Reset script control variables
        self.currently_scripting = False
        self.step_index = -1
        self.abort_immediately_var = True
        self.task_number_signal.emit(0)
        self.task_index_signal.emit(0)
        self.enable_ui_signal.emit(True)
        # Todo: add option to save before exiting

    def cont_if_cont_clicked(self) -> bool:
        """
        Waits and returns true if the user presses continue. Returns false if the user clicks abort or retry.
        Call this method after showing a dialog, and return if the result is false.
        """
        try:
            self.__wait_for_cont()
            return True
        except AbortException as e:
            self.test_data.log_script(["", "User prompt", "FAIL", "Closed by user"])
            self.abort_after_step()
            return False
        except RetryException:
            self.test_data.log_script(["", "User prompt", "Retry step", ""])
            self.log("Retrying step")
            self.retry_clicked = True
            return False

    def __wait_for_cont(self):
        """
        Sets continue variable to False and waits for it to be true, raising exceptions if the user
        wants to abort or retry. Always handle these exceptions.
        """
        self.continue_clicked = False
        self.retry_clicked = False
        self.abort_clicked = False

        while not self.continue_clicked:
            # check if script has been aborted
            if self.retry_clicked:
                self.retry_clicked = False
                # Always handle this exception
                raise RetryException
            if self.abort_clicked:
                self.abort_clicked = False
                # Always handle this exception
                raise AbortException
            if self.abort_immediately_var:
                self.abort_immediately()

    @pyqtSlot()
    def continue_clicked(self):
        """Flags cont_clicked to continue the current step"""
        self.continue_clicked = True

    @pyqtSlot()
    def retry_clicked(self):
        """Flags cont_clicked to retry the current step"""
        self.retry_clicked = True

    @pyqtSlot()
    def abort_clicked(self):
        """Flags cont_clicked to abort the current step"""
        self.abort_clicked = True

    def write_calibration_data_to_ua_button(self):
        # Todo: make this method write calibration data to UA
        pass

    def script_complete(self, finished=False):
        """Run when the script finishes its final step. Shows a dialog with pass/fail results and enables the UI"""
        # Fetch pass list and description list from testdata
        pass_list = list([None] * 11)
        description_list = list([None] * 11)

        if finished:
            device_result = 'PASS'
        else:
            device_result = 'DNF'

        for i in range(10):
            pass_list[i] = self.test_data.results_summary[i][15]
            if pass_list[i].upper() == 'FAIL':
                device_result = 'FAIL'
            description_list[i] = self.test_data.results_summary[i][16]

        # Add ua write result to output
        if self.test_data.write_result:
            pass_list[10] = "PASS"
        else:
            pass_list[10] = "FAIL"

        # add the result for the device as a whole to the results_summary
        self.test_data.set_pass_result(11, device_result)

        self.script_complete_signal.emit(pass_list, description_list)
        self.currently_scripting = False
        self.enable_ui_signal.emit(True)

        self.test_data.log_script(["Script complete", "", "", ""])

    def pretest_initialization(self, var_dict):
        """Home the UA, perform hardware checks, and prompt the user until they pass,
        takes in a variable dict as a parameter"""

        # add first 4 lines of scriptlog
        self.test_data.log_script([f"{self.test_data.serial_number}-{self.test_data.test_date_time}",
                                   '', '', ''])  # this is the first line
        self.test_data.log_script(["Running script: ", self.test_data.script_name, '', '', ''])
        self.test_data.log_script(["Pretest_initialization", '', '', ''])
        self.test_data.log_script(['', "Prompt username+UA serial", 'OK', ''])

        # Check if wtfib is connected and add that to the script log
        if self.test_data.serial_number != "":
            self.test_data.log_script(["", "Get UA Serial", "Connected", "OK"])
        else:
            self.test_data.log_script(["", "Get UA Serial", "Connected", "FAIL"])
            cont = self.sequence_pass_fail(error_detail="Get UA Serial in pretest initialisation failed",
                                           action_type="Interrupt action")
            if not cont:
                return
            self.retry_clicked = False

        # Show dialogs until pump is on and the water sensor reads level
        while True:
            if not self.IO_Board.get_ua_pump_reading():  # if the pump is not running
                # launch the dialog box signifying this issue
                self.user_prompt_pump_not_running_signal.emit(pump_status)
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return
            else:
                self.test_data.log_script(["", "Check/prompt UA Pump", "OK", ""])
                break

        # todo: have ua inserted to certain x position like in the ScriptResults.log

        home_successful = self.home_system(var_dict={"Axis to home": "All Axes"})

        if home_successful:
            self.test_data.log_script(['', "Home all", f"OK; X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}", ''])
        else:
            self.test_data.log_script(['', "Home all", f"FAIL; X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}", ''])
            cont = self.sequence_pass_fail(action_type='Interrupt action',
                                           error_detail='Home all has failed in pretest initialisation')
            if not cont:
                return

        self.test_data.log_script(['', 'Insert UA', f"UA Inserted to X={self.Motors.coords_mm[0]}"])

        if self.thermocouple.connected:
            self.test_data.log_script(["", "CheckThermocouple", "OK", ""])
        else:
            self.test_data.log_script(["", "CheckThermocouple", "FAIL", ""])
            cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail='Thermocouple failed check')
            if not cont:
                return

        # Configure function generator
        func_var_dict = dict()
        func_var_dict["Amplitude (mVpp)"] = self.config[self.AWG.device_key]["amplitude_V"] * 1000
        func_var_dict["Frequency (MHz)"] = self.test_data.low_frequency_MHz
        func_var_dict["Mode"] = "Toneburst"
        func_var_dict["Enable output"] = True
        func_var_dict["#Cycles"] = self.config[self.AWG.device_key]['burst_cycles']
        func_var_dict["Set frequency options"] = "From config cluster"
        self.configure_function_generator(func_var_dict)

        # Prompt user to turn on power amp
        while True:
            self.user_prompt_signal.emit("Please ensure that the power amplifier is on", False)

            cont = self.cont_if_cont_clicked()
            if not cont:
                return

            self.test_data.log_script(["", "Prompt PowerAmp", "OK", ""])
            break

        if self.file_saver.directories_created:
            self.test_data.log_script(["", "CreateDataDirectories", "OK", ""])
        else:
            self.test_data.log_script(["", "CreateDataDirectories", f"FAIL", ""])

        try:
            self.log("Checking ability to log")
            self.test_data.log_script(["", "Create h/w log", "OK", ""])
        except Exception as e:
            self.test_data.log_script(["", "Create h/w log", f"FAIL {e}", ""])

        self.test_data.log_script(["", "Initialize results FGV", "OK", ""])
        self.test_data.log_script(["", "duplicate main script", "OK", ""])

        while True:
            water_level = self.IO_Board.get_water_level()

            if water_level == WaterLevel.below_level:  # if the water level is not level
                # launch the dialog box signifying this issue
                self.user_prompt_signal_water_too_low_signal.emit()
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return

                self.IO_Board.fill_tank()
            elif water_level == WaterLevel.above_level:  # if the water level is not level
                # launch the dialog box signifying this issue
                self.user_prompt_signal_water_too_high_signal.emit()
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return

                self.IO_Board.fill_tank()
            else:
                self.test_data.log_script(["", "Check/prompt water level", "OK", ""])
                break

    @pyqtSlot(TestData)
    def begin_script_slot(self, test_data: TestData):
        """Receive test metadata from the MainWindow, and begin a script."""

        # reset test data to default values
        self.test_data.set_blank_values()

        # reset their representation in the UI
        self.test_data.show_results_summary.emit(self.test_data.results_summary)
        self.test_data.show_script_log.emit(self.test_data.script_log)

        self.test_data.test_comment = test_data.test_comment
        self.test_data.serial_number = test_data.serial_number
        self.test_data.operator_name = test_data.operator_name
        self.test_data.low_frequency_MHz = test_data.low_frequency_MHz
        self.test_data.high_frequency_MHz = test_data.high_frequency_MHz
        self.test_data.hardware_code = test_data.hardware_code
        self.test_data.test_date_time = test_data.test_date_time
        self.test_data.schema = test_data.schema
        try:
            self.file_saver.create_folders(test_data=self.test_data)
        except PermissionError:
            self.user_prompt_signal.emit("Access to the results folder is denied, change it in local.yaml."
                                         "Copy default.yaml if local.yaml does not exist.", False)
            return self.abort_after_step()
        self.run_script()

    def element_str_to_int(self, element_str):
        try:
            self.element = int(re.search(r"\d+", str(element_str)).group())
        except:
            self.log(f"Element number not given, using previous element: {self.element}")
        return self.element

    def find_element(self, var_dict):
        """
        Find UA element with given number by scanning for a maximum VSI or RMS
        returns a boolean indicating whether to continue the script
        """
        self.element = self.element_str_to_int(var_dict["Element"])
        x_increment_MM = float(var_dict["X Incr. (mm)"])
        XPts = int(var_dict["X #Pts."])
        thetaIncrDeg = float(var_dict["Theta Incr. (deg)"])
        thetaPts = int(var_dict["Theta #Pts."])
        self.oscilloscope_channel = int(var_dict["Scope channel"][8:])
        acquisition_type = var_dict["Acquisition type"]
        averages = int(re.search(r"\d+", str(var_dict["Averages"])).group())
        data_storage = var_dict["Data storage"]
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        maxPosErrMM = float(var_dict["Max. position error (+/- mm)"])
        elemPosTest = bool(var_dict["ElementPositionTest"])
        max_angle_variation_Deg = float(var_dict["Max angle variation (deg)"])
        beam_angle_test = bool(var_dict["BeamAngleTest"])
        frequency_settings = var_dict["Frequency settings"]
        frequency_MHz = float(var_dict["Frequency (MHz)"])
        amplitude_mVpp = float(var_dict["Amplitude (mV)"])
        burst_count = int(float(var_dict["Burst count"]))

        # If on the first element, set the tab to the scan tab
        if self.element == 1:
            self.set_tab_signal.emit("Scan")

        self.test_data.log_script(['Find element "n"', "OK", "", ""])

        try:  # at this point in the script, the checks have been performed already in pretest_initialization so no
            # need to wrap in if statements
            self.test_data.log_script(['', 'PreChecks',
                                       f'Tank fill status {self.IO_Board.get_water_level()}, UA pump status '
                                       f'{self.IO_Board.get_ua_pump_reading()}', ''])
        except Exception as e:
            self.test_data.log_script(["", "PreChecks", f"FAIL {e}", ""])

        # Update UI visual to reflect the element we are on
        self.element_number_signal.emit(str(self.element))

        element_x_coordinate = self.element_x_coordinates[self.element]
        element_r_coordinate = self.element_r_coordinates[self.element]
        # self.log(f"Finding element {self.element}, near coordinate x = {element_x_coordinate}, r = {element_r_coordinate}")

        # Configure hardware
        self.select_ua_channel(var_dict={"Element": self.element})

        # Configure function generator
        awg_var_dict = dict()
        awg_var_dict["Amplitude (mVpp)"] = amplitude_mVpp
        awg_var_dict["Frequency (MHz)"] = frequency_MHz
        awg_var_dict["Mode"] = "Toneburst"
        awg_var_dict["Enable output"] = "False"
        awg_var_dict["#Cycles"] = burst_count
        if "low".upper() in frequency_settings.upper():
            awg_var_dict["Set frequency options"] = 'Common low frequency'
        elif "high".upper() in frequency_settings.upper():
            awg_var_dict["Set frequency options"] = 'Common high frequency'
        elif "config cluster".upper() in frequency_settings.upper():
            awg_var_dict["Set frequency options"] = frequency_settings
        else:
            self.user_prompt_signal.emit("Invalid frequency parameter", False)
            return self.abort_after_step()

        self.configure_function_generator(awg_var_dict)

        self.test_data.log_script(["", "Config UA and FGen", "FGen output enabled", ""])

        # todo: populate var_dict and make sure method is implemented
        autoset_var_dict = dict()
        self.autoset_timebase(autoset_var_dict)  # script log updated in this method

        self.Motors.go_to_position(['R'], [-180])
        cont = self.scan_axis(axis='X', num_points=XPts, increment=x_increment_MM, ref_position=element_x_coordinate,
                              go_to_peak=True, data_storage=data_storage, acquisition_type=acquisition_type,
                              averages=averages)
        if not cont:
            return False

        self.home_system({'Axis to home': 'Theta'})
        if beam_angle_test:
            cont = self.scan_axis(axis='Theta', num_points=thetaPts, increment=thetaIncrDeg,
                                  ref_position=self.config["WTF_PositionParameters"]["ThetaHydrophoneCoord"],
                                  go_to_peak=False, data_storage=data_storage, acquisition_type=acquisition_type,
                                  averages=averages)

            if not cont:
                return False

        self.home_system({"Axis to home": "Theta"})

        self.AWG.set_output(False)
        self.test_data.log_script(['', 'Disable UA and FGen', 'Disabled FGen output', ''])
        self.test_data.log_script(['', 'End', 'OK', ''])
        return True

    # Reference position is the center of the scan range

    def scan_axis(self, axis, num_points, increment, ref_position, data_storage, go_to_peak, scope_channel=1,
                  acquisition_type='N Averaged Waveform', averages=1) -> bool:
        if axis == 'X':
            axis_letter = 'X'
        elif axis == 'Theta':
            axis_letter = 'R'
        else:
            self.user_prompt_signal.emit("Invalid axis parameter, aborting", False)
            return self.abort_after_step()
        if self.Motors.rotational_ray[self.Motors.ax_letters.index(axis_letter)]:
            units_str = "deg"
            axis_label = "Angle (deg)"
        else:
            units_str = "mm"
            axis_label = "Distance (mm)"

        if acquisition_type.upper() == "N Averaged Waveform".upper():
            self.Oscilloscope.set_averaging(averages)
        else:
            self.Oscilloscope.set_averaging(1)

        # Loop over x through a given range, move to the position where maximal RMS voltage was measured
        positions = list()
        vsi_values = list()

        # sweep from the expected element position minus the max error to the expected element position plus max error
        position = -1 * (num_points * increment) / 2 + ref_position

        # begin with arbitrarily low values which will be overwritten
        max_vsi = -1 * sys.float_info.max
        max_position = -1 * sys.float_info.max

        for i in range(num_points):
            if self.abort_immediately_var:
                # Stop the current method and any parent methods that called it
                return False

            self.Motors.go_to_position([axis_letter], [position])
            position = position + increment

            times_s, voltages_v = self.capture_scope(channel=self.oscilloscope_channel)
            if times_s == [] or voltages_v == []:
                cont = self.sequence_pass_fail(action_type='Interrupt action',
                                               error_detail='Oscilloscope capture failed')
                if not cont:
                    return False

            if 'Store entire waveform'.upper() in data_storage.upper():
                self.save_hydrophone_waveform(axis=axis, waveform_number=i + 1, times_s=times_s,
                                              voltages_v=voltages_v)

            vsi = self.find_vsi(times_s=times_s, voltages_v=voltages_v)

            try:
                if vsi > max_vsi:
                    max_vsi = vsi
                    max_position = position
            except TypeError:
                return False

            positions.append(position)
            vsi_values.append(vsi)
            self.profile_plot_signal.emit(positions, vsi_values, axis_label)

        self.test_data.log_script(['', 'Move to element', f"Moved to X={'%.2f' % self.Motors.coords_mm[0]}, "
                                                          f"Th={'%.2f' % self.Motors.coords_mm[1]}", ''])

        self.log(f"Maximum of {max_vsi} @ {axis} = {max_position} {units_str}")

        if axis == "X":
            self.element_x_coordinates[self.element] = max_position
        else:
            self.element_r_coordinates[self.element] = max_position

        self.test_data.set_max_position(axis, self.element, max_position)

        status_str = f'Start {axis} {"%.2f" % self.element_x_coordinates[self.element]} mm; Incr {axis} ' \
                     f'{increment} {units_str}; #Points {num_points}; Peak {axis} = ' \
                     f'{"%.2f" % max_position} 'f'mm;'

        if go_to_peak:
            status = self.Motors.go_to_position([axis_letter], [max_position])
            status_str = status_str + f" moved to {axis} = {max_position} {units_str}"

        self.test_data.log_script(["", f"Scan{axis} Find Peak {axis}:", status_str, ""])

        if not 'Do not store'.upper() == data_storage.upper():
            self.save_scan_profile(positions=positions, vsi_values=vsi_values, axis=axis)

        return True

    def save_hydrophone_waveform(self, axis, waveform_number, times_s, voltages_v):
        """Saves an oscilloscope trace using the file handler"""
        metadata = FileMetadata()
        metadata.element_number = self.element
        metadata.axis = f"{axis}"
        metadata.waveform_number = f"{axis}{waveform_number:03}"
        metadata.serial_number = self.test_data.serial_number
        metadata.X = self.Motors.coords_mm[0]
        metadata.Theta = self.Motors.coords_mm[1]
        metadata.frequency_MHz = self.AWG.state["frequency_Hz"] / 1000000
        metadata.amplitude_mVpp = self.AWG.state["amplitude_V"] * 1000
        if self.AWG.state["burst_on"]:
            metadata.source_signal_type = "Toneburst"
        else:
            metadata.source_signal_type = "Continuous"
        metadata.num_cycles = self.AWG.state["burst_cycles"]

        self.file_saver.store_waveform(metadata=metadata, times=times_s, voltages=voltages_v)

    def save_scan_profile(self, axis, positions, vsi_values):
        """Saves a voltage squared integral vs distance"""
        metadata = FileMetadata()
        metadata.element_number = self.element
        metadata.axis = f"{axis}"
        metadata.serial_number = self.test_data.serial_number
        metadata.X = self.Motors.coords_mm[0]
        metadata.Theta = self.Motors.coords_mm[1]
        metadata.frequency_MHz = self.AWG.state["frequency_Hz"] / 1000000
        metadata.amplitude_mVpp = self.AWG.state["amplitude_V"] * 1000
        if self.AWG.state["burst_on"]:
            metadata.source_signal_type = "Toneburst"
        else:
            metadata.source_signal_type = "Continuous"
        metadata.num_cycles = self.AWG.state["burst_cycles"]

        self.file_saver.save_find_element_profile(metadata=metadata, positions=positions, vsi_values=vsi_values)

    def save_efficiency_test_data(self, f_time_s, f_power_w, r_time_s, r_power_w, a_time_s, a_power_w):
        """Saves a voltage squared integral vs distance """
        metadata = FileMetadata()
        metadata.element_number = self.element
        metadata.serial_number = self.test_data.serial_number
        metadata.X = self.Motors.coords_mm[0]
        metadata.Theta = self.Motors.coords_mm[1]
        metadata.frequency_MHz = self.AWG.state["frequency_Hz"] / 1000000
        metadata.amplitude_mVpp = self.AWG.state["amplitude_V"] * 1000
        if self.AWG.state["burst_on"]:
            metadata.source_signal_type = "Toneburst"
        else:
            metadata.source_signal_type = "Continuous"
        metadata.num_cycles = self.AWG.state["burst_cycles"]

        self.file_saver.store_measure_rfb_waveform_csv(  # TODO: you don't have forward_power, reflected_power, nor acoustic_power arguments in the store_measure_rfb_waveform_csv method
            metadata,
            forward_power=[f_time_s, f_power_w],
            reflected_power=[r_time_s, r_power_w],
            acoustic_power=[a_time_s, a_power_w],
        )

    def save_results(self, var_dict):
        """Saves test summary data stored in self.test_data to a file on disk using the file handler self.file_saver"""
        save_summary_file = bool(distutils.util.strtobool(var_dict["Save summary file"]))
        write_uac_calibration = bool(distutils.util.strtobool(var_dict["Write UA Calibration"]))
        prompt_for_calibration_write = bool(distutils.util.strtobool(var_dict["PromptForCalWrite"]))

        # Todo: test
        if prompt_for_calibration_write:  # displays the "write to UA" dialog box if this variable is true
            self.user_prompt_signal.emit("Write calibration data to UA", False)
            cont = self.cont_if_cont_clicked()  # sets cont variable to true if user clicked continue
            if not cont:  # if user did not click continue, return
                return

        self.test_data.software_version = self.config["Software_Version"]
        self.test_data.calculate_angle_average()

        calibration_data = generate_calibration_data(self.test_data)
        self.UAInterface.write_data(calibration_data)

        # Save results summary to results folder
        self.file_saver.save_test_results_summary_and_log(test_data=self.test_data)

    def prompt_user_for_action(self, var_dict):
        """Prompt user for action"""
        prompt_type = var_dict["Prompt type"]
        if "Other".upper() in prompt_type.upper():
            try:
                prompt_type = var_dict["Prompt message"]
            except KeyError:
                prompt_type = "Blank Prompt"

            self.user_prompt_signal.emit(prompt_type, False)
        else:
            self.user_prompt_signal.emit(prompt_type, False)

        cont = self.cont_if_cont_clicked()  # waits for the user to click continue
        if not cont:  # if the user did not click continue, return
            return

    def configure_function_generator(self, var_dict):
        """Set function generator to desired settings"""
        # todo: test
        mVpp: int = int(var_dict["Amplitude (mVpp)"])
        frequency_mhz: float = float(var_dict["Frequency (MHz)"])
        mode = var_dict["Mode"]
        output = bool(var_dict["Enable output"])
        frequency_options = var_dict["Set frequency options"]

        if frequency_options == "Common low frequency" or frequency_options == 'Element pk low frequency':
            frequency_mhz = self.test_data.low_frequency_MHz
        elif frequency_options == "Common high frequency" or frequency_options == 'Element pk high frequency':
            frequency_mhz = self.test_data.high_frequency_MHz
        elif frequency_options == "From config cluster":
            # TODO: what is config cluster?
            # TODO: fill this part of the code
            pass
        else:
            self.user_prompt_signal.emit("Invalid frequency parameter, aborting", False)
            return self.abort_after_step()

        self.AWG.set_output(output)
        self.AWG.set_frequency_hz(int(frequency_mhz * 1000000))
        self.test_data.log_script(
            ["", "Configure FGen+PwrMeters", f"Frequency set to {frequency_mhz} MHz", "", ])
        self.AWG.set_amplitude_v(mVpp / 1000)

        if mode == "N Cycle":
            self.AWG.set_burst(True)
            cycles = int(var_dict["#Cycles"])
            self.AWG.set_cycles(cycles)
        else:
            self.AWG.set_burst(False)

        self.test_data.log_script(["", "Config FGen", f"{mVpp}mVpp;{frequency_mhz}MHz,{mode}"])

    def configure_oscilloscope_channels(self, var_dict):
        # todo: test
        c1_enabled = bool(var_dict["Channel 1 Enabled"])
        # todo: implement capture from channel 2 (stretch), must also enable the menu options in qtdesigner
        c2_enabled = bool(var_dict["Channel 2 Enabled"])
        g1_mV_div = float(var_dict["Gain 1"])
        g2_mV_div = float(var_dict["Gain 2"])
        o1_mV = float(var_dict["Offset 1"])
        o2_mV = float(var_dict["Offset 2"])
        if c1_enabled:
            self.Oscilloscope.set_vertical_scale_V(g1_mV_div / 1000, 1)
            self.Oscilloscope.set_vertical_offset_V(1, o1_mV / 1000)
        if c2_enabled:
            self.Oscilloscope.set_vertical_scale_V(g2_mV_div / 1000, 2)
            self.Oscilloscope.set_vertical_offset_V(2, o2_mV / 1000)

    def configure_oscilloscope_timebase(self, var_dict):
        # todo: test
        timebase_us = float(var_dict["Timebase"])
        delay_us = float(var_dict["Delay"])
        self.Oscilloscope.set_horizontal_scale_sec(timebase_us / 1000000)
        self.Oscilloscope.set_horizontal_offset_sec(delay_us / 1000000)

    def autoset_timebase(self, var_dict):
        self.Oscilloscope.autoset_oscilloscope_timebase()

    def home_system(self, var_dict) -> bool:
        """Return axis to zero coordinate, returns whether or not to continue the script"""
        # TODO: have this be called in pretest_initialization and have it add to script log
        axis_to_home = var_dict["Axis to home"]

        successful_go_home = False
        if axis_to_home == "All Axes":
            self.retracting_ua_warning_signal.emit()  # launch the retracting UA in the x direction warning box
            cont = self.cont_if_cont_clicked()
            if not cont:
                return False
            successful_go_home = self.Motors.go_home()
            self.test_data.log_script(['', "Home all", f"X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}",
                                       f'Successful:{successful_go_home}'])
        elif axis_to_home == 'X':
            self.retracting_ua_warning_signal.emit()  # launch the retracting UA in the x direction warning box
            cont = self.cont_if_cont_clicked()
            if not cont:
                return False
            successful_go_home = self.Motors.go_home_1d("X")
            self.test_data.log_script(["", f"Home  X", f"Home X", f'Successful:{successful_go_home}'])
        elif axis_to_home == "Theta":
            successful_go_home = self.Motors.go_home_1d("R")
            self.test_data.log_script(["", f"Home Theta", f"Home Theta", f'Successful:{successful_go_home}'])
        else:
            self.test_data.log_script(['', f'Home {axis_to_home}', 'FAIL', 'axis unrecognized'])

        if not successful_go_home:
            cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail='Go home failed')
            return cont
        return True

    def retract_ua_warning(self):
        """Warn the user that the UA is being retracted in x"""
        self.retracting_ua_warning_signal.emit()

    def move_system(self, var_dict):
        """Move motors to the specified coordinates"""
        move_type = var_dict["Move Type"]

        if "Go To".upper() in move_type.upper():
            x_pos = float(var_dict["X POS"])
            move_x = bool(var_dict["Move X"])
            theta_pos = float(var_dict["Theta POS"])
            move_theta = bool(var_dict["Move Theta"])
            axes = []
            coords = []
            if move_x:
                axes.append("X")
                coords.append(x_pos)
            if move_theta:
                axes.append("R")
                coords.append(theta_pos)
            self.Motors.go_to_position(axes, coords)
        else:
            self.element = self.element_str_to_int(var_dict["Element"])
            target = var_dict["Target"]
            element_x_coordinate = self.element_x_coordinates[self.element]
            element_r_coordinate = self.element_r_coordinates[self.element]

            # todo: make sure these names match theirs
            # todo: make sure these home coordinates work as expected
            if "Hydrophone" in target:
                self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -180])
            elif "RFB" in target:
                self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, element_r_coordinate])
            elif "Down" in target:
                self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -90])

            x_coord_str = "%.2f" % element_x_coordinate
            r_coord_str = "%.1f" % element_r_coordinate
            self.log(f"Moved to {self.element}, at coordinate x={x_coord_str}, r={r_coord_str}")

            self.test_data.log_script(["", "Move to element", f"moved to X={x_coord_str}, Th={r_coord_str}", ''])

    # todo: test
    def select_ua_channel(self, var_dict):
        """Activate the relay for and move to a specified element"""
        self.element = self.element_str_to_int(var_dict["Element"])
        self.IO_Board.activate_relay_channel(channel_number=self.element)

    def frequency_sweep(self, var_dict):
        # todo: add test to results summary if include_test is True
        # todo: using this setting to decide where to put it (Low frequency or High frequency)
        frequency_range = FrequencyRange[var_dict["Frequency range"].lower().replace(" ", "_")]
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

        self.AWG.set_output(True)
        self.AWG.set_amplitude_v(amplitude_mVpp / 1000)
        self.AWG.set_burst(True)

        if acquisition_type == "Single Waveform":
            self.Oscilloscope.set_averaging(1)
        else:
            self.Oscilloscope.set_averaging(averages)

        coarse_freq_MHz_list, coarse_VSI_list = self.run_frequency_sweep(start_freq_MHz, end_freq_MHz, coarse_incr_MHz,
                                                                         burst_count, channel=scope_channel)

        # todo: enable this in a way that makes sense and add it to the output file
        # fine_freq_MHz_list, fine_VSI_list = self.run_frequency_sweep(start_freq_MHz,end_freq_MHz,fine_incr_MHz,
        #                                                             burst_count, scope_channel = scope_channel)

        if data_storage == "Store entire waveform":
            # todo: move to file_saver object
            if storage_location == "UA results directory":
                path = self.config['Paths']['UA results root directory'] + "\\" + self.test_data.serial_number + "-" + \
                       self.test_data.test_date_time + "-frequency_sweep_data.csv"  # retrieve path
            else:
                path = data_directory + "\\" + self.test_data.serial_number + "-" + \
                       self.test_data.test_date_time + "-frequency_sweep_data.csv"  # retrieve path

            # todo: implement
            self.file_saver.save_frequency_sweep()

            if not os.path.exists(os.path.dirname(path)):
                self.log("creating results path...")
                os.makedirs(os.path.dirname(path))

            f = open(path, "w")

            f.write("Frequency (MHz), Voltage squared integral")
            for i in range(len(coarse_freq_MHz_list)):
                f.write(f"{coarse_freq_MHz_list[i]},{coarse_VSI_list[i]}")

    def run_frequency_sweep(self, lower_limit_MHz, upper_limitMHz, freq_step, bursts, channel=1):
        list_of_VSIs = list()
        list_of_frequencies_MHz = list()

        for x in np.arange(lower_limit_MHz, upper_limitMHz, freq_step):
            self.AWG.set_frequency_hz(x * 1000000)  # set frequency accoding to step (coarse/fine) and x incremenet
            # add the frequency to the list
            # Find the average vsi voltage at a given frequency
            vsi_sum = 0
            for i in range(bursts):
                # populates times_s and voltages_v with set frequency
                times_s, voltages_v = self.capture_scope(channel=1)
                vsi = self.find_vsi(times_s, voltages_v)
                vsi_sum = vsi_sum + vsi
            vsi_avg = vsi_sum / bursts

            list_of_frequencies_MHz.append(x)
            list_of_VSIs.append(vsi_avg)

        assert len(list_of_VSIs) == len(list_of_frequencies_MHz)

        self.profile_plot_signal.emit(list_of_frequencies_MHz, list_of_VSIs, "Frequency (Hz)")

        # frequencies will be on the x-axis
        return (list_of_frequencies_MHz, list_of_VSIs)

    def find_vsi(self, times_s, voltages_v):
        """Returns the voltage squared integral of a oscilloscope waveform"""
        dx = 0
        for i in range(1, len(times_s)):
            dx = times_s[i] - times_s[i - 1]
            if not dx == 0:
                break

        voltages_v_squared = np.square(voltages_v)

        if dx == 0:
            self.log(level='Error', message='Error in find_vsi. No delta x found, cannot integrate')
            return

        return integrate.simps(y=voltages_v_squared, dx=dx, axis=0)

    def measure_element_efficiency_rfb_multithreaded(self, var_dict):
        """Measure the efficiency of an element"""
        self.element = self.element_str_to_int(var_dict["Element"])

        # Retrieve test parameters from the script and typecast them from strings
        # High frequency or Low frequency, convert to FrequencyRange enum
        frequency_range = FrequencyRange[var_dict["Frequency range"].lower().replace(" ", "_")]
        on_off_cycles = int(var_dict["RFB.#on/off cycles"])
        rfb_on_time = float(var_dict["RFB.On time (s)"])
        rfb_off_time = float(var_dict["RFB.Off time (s)"])
        threshold = float(var_dict["RFB.Threshold"])
        offset = float(var_dict["RFB.Offset"])
        set_frequency_options = var_dict["Set frequency options"]
        frequency_MHz = float(var_dict["Frequency (MHz)"])
        amplitude_mVpp = float(var_dict["Amplitude (mVpp)"])
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        target_position = var_dict["RFB target position"]
        target_angle = var_dict["RFB target angle"]
        efficiency_test = bool(var_dict["EfficiencyTest"])
        Pa_max = var_dict["Pa max (target, W)"]
        Pf_max = var_dict["Pf max (limit, W)"]
        reflection_limit = var_dict["Reflection limit (%)"]

        test_result = "DNF"
        # Show in the results summary that the test has begun by showing DNF
        self.test_data.set_pass_result(self.element, test_result)

        # Warn the user if the test time is too short to analyze properly
        settling_time = self.config["Analysis"]['settling_time_s']
        if rfb_on_time <= settling_time or rfb_on_time <= settling_time:  # TODO: these are identical, did you mean to put another condition?
            self.user_prompt_signal.emit("Warning: the on or off intervals are less than the sensor settling time "
                                         "specified in the config file. Either change it or load a different script",
                                         False)
            cont = self.cont_if_cont_clicked()
            if not cont:
                return

        # Create an empty RFB data structure
        self.rfb_data = RFBData(element=self.element,
                                water_temperature_c=self.thermocouple.get_reading(),
                                frequency_range=frequency_range,
                                Pf_max=Pf_max,
                                Pa_max=Pa_max,
                                ref_limit=reflection_limit, config=self.config)

        self.element_number_signal.emit(str(self.element))
        # If on the first element, set the tab to the rfb tab
        if self.element == 1:
            self.set_tab_signal.emit("RFB")

        # todo: replace this with an insert at the end to check if the step finished successfully
        self.test_data.log_script(["Measure element efficiency (RFB)", "OK", "", ""])

        # Hardware checks
        try:
            # at this point in the script, the checks have been performed already in pretest_initialization so no
            # need to wrap in if statements
            self.test_data.log_script(['', 'PreChecks',
                                       f'Tank fill status {self.IO_Board.get_water_level()}, UA pump status '
                                       f'{self.IO_Board.get_ua_pump_reading()}', ''])
        except Exception as e:
            self.test_data.log_script(["", "PreChecks", f"FAIL {e}", ""])

        self.select_ua_channel(var_dict={"Element": self.element})
        self.move_system(var_dict={"Element": self.element, "Move Type": "Move to element", "Target": 'RFB'})

        self.test_data.log_script(['', 'Set frequency range', f"\"{frequency_range}\" range set", ''])

        # Configure function generator
        awg_var_dict = dict()
        awg_var_dict["Amplitude (mVpp)"] = amplitude_mVpp
        awg_var_dict["Frequency (MHz)"] = frequency_MHz
        awg_var_dict["Mode"] = "Continous"
        awg_var_dict["Enable output"] = "False"
        awg_var_dict["#Cycles"] = ""
        if "Common".upper() in set_frequency_options.upper() and frequency_range == FrequencyRange.low_frequency:
            awg_var_dict["Set frequency options"] = 'Common low frequency'
        elif "Common".upper() in set_frequency_options.upper() and frequency_range == FrequencyRange.high_frequency:
            awg_var_dict["Set frequency options"] = 'Common high frequency'
        elif "config cluster".upper() in set_frequency_options.upper():
            awg_var_dict["Set frequency options"] = set_frequency_options
        else:
            self.user_prompt_signal.emit("Invalid frequency parameter, aborting", False)
            return self.abort_after_step

        self.configure_function_generator(awg_var_dict)

        self.Balance.zero_balance_instantly()

        self.test_data.log_script(["", "Start RFB Acquisition", "Started RFB Action", ""])

        # Run test
        # Begin multi-threaded capture from the power meters and the balance and cycle the awg on and off
        self.__begin_rfb_logger_thread(self.rfb_data)

        start_time = t.time()
        current_cycle = 1

        # Extra off cycle at beginning
        self.log(f"Turning off AWG T = {'%.2f' % (t.time() - start_time)}")
        self.AWG.set_output(False)
        # for the duration of rfb off time
        while t.time() - start_time < rfb_off_time:
            cont = self.refresh_rfb_tab()
            if not cont:
                return False

        while current_cycle <= on_off_cycles:
            cycle_start_time = t.time()

            #  turn on awg
            self.log(f"Turning on AWG T = {'%.2f' % (t.time() - start_time)}")
            self.AWG.set_output(True)
            # for the duration of rfb on time
            while t.time() - cycle_start_time < rfb_on_time:
                cont = self.refresh_rfb_tab()
                if not cont:
                    return

            # Turn off AWG
            self.log(f"Turning off AWG T = {'%.2f' % (t.time() - start_time)}")
            self.AWG.set_output(False)
            # for the duration of rfb off time
            while t.time() - cycle_start_time < rfb_on_time + rfb_off_time:
                cont = self.refresh_rfb_tab()
                if not cont:
                    return

            current_cycle = (current_cycle + 1)  # we just passed a cycle at this point in the code

        start_time = t.time()  # todo: variable is unused here, should this be self.start_time?
        self.__wrap_up_rfb_logger()

        self.test_data.log_script(["", "Run on/off sequence", "RFB Acquisition complete", ""])
        self.test_data.log_script(["", "Stop RFB Acquisition", "RFB Stopped, data saved", ""])

        data_is_valid, feedback = self.rfb_data.data_is_valid()

        if not data_is_valid:
            cont = self.sequence_pass_fail(action_type='Interrupt action',
                                           error_detail=f'Element_{self.element:02} {feedback}')
            if not cont:
                return

        self.rfb_data.trim_data()
        self.rfb_data.end_of_test_data_analysis()

        test_result, comment = self.rfb_data.get_pass_result()

        # prompt user if test failed
        if test_result.upper() == 'FAIL':
            cont = self.sequence_pass_fail(action_type='Pass fail action',
                                           error_detail=f'Element_{self.element:02} Failed efficiency test')
            if not cont:
                return
        elif test_result.upper() == 'DNF':
            cont = self.sequence_pass_fail(action_type='Interrupt action',
                                           error_detail=f'Element_{self.element:02} Failed efficiency test')
            if not cont:
                return
        elif test_result.upper() == 'PASS':
            self.log(f"test result for {self.element} has passed", self.info)
        else:
            self.log("self.rfb_data.get_pass_result() has returned an invalid result, aborting", self.warn)
            self.user_info_signal.emit("self.rfb_data.get_pass_result() has returned an invalid result, aborting")
            return self.abort_after_step()

        self.retry_clicked = False

        self.test_data.update_results_summary_with_efficiency_results(
            frequency_range=frequency_range,
            element=self.element,
            frequency_Hz=self.AWG.state["frequency_Hz"],
            efficiency_percent=self.rfb_data.efficiency_percent,
            reflected_power_percent=self.rfb_data.reflected_power_percent,
            forward_power_max=self.rfb_data.forward_power_max_extrapolated,
            water_temperature_c=self.rfb_data.water_temperature_c,
            test_result=test_result,
            comment=comment
        )

        self.test_data.log_script(self.rfb_data.get_result_log_entry())

        ### Start block of code to move to file_saver class extract_file_data(test_data: TestData)

        balance_readings_mg = [value * 1000 for value in self.rfb_logger.balance_readings_g]
        # Time (s),Mass (mg),Acoustic Power (W), Pf(W), Pr(W)
        raw_data = [
            self.rfb_logger.times_s,
            balance_readings_mg,
            self.rfb_logger.acoustic_powers_w,
            self.rfb_logger.f_meter_readings_w,
            self.rfb_logger.r_meter_readings_w,
        ]

        absorption = ["Off", 1.000690]
        transducer_size = ["Off", 1.013496]
        focusing = ["Off", 1.000000]

        buffer = self.config["Analysis"]["samples_to_remove_at_end"]

        # transition_times_s/transition_amp_w[0] = start on, [1] = end on, [2] = start off, [3] = end off
        num_cycles = len(self.rfb_data.on_time_intervals_s)
        transition_times_s = [[float('nan')] * num_cycles, [float('nan')] * num_cycles, [float('nan')] * num_cycles,
                              [float('nan')] * num_cycles]
        for i in range(num_cycles):
            if not i == 0:
                # Beginning of on transition
                transition_times_s[0][i] = self.rfb_data.times_s[self.rfb_data.off_indices[i - 1][1]]
            else:
                # Beginning of on transition
                transition_times_s[0][i] = self.rfb_data.times_s[self.rfb_data.awg_on_ray.index(True) - buffer]
            # Beginning of off transition
            transition_times_s[2][i] = self.rfb_data.times_s[self.rfb_data.on_indices[i][1]]

            transition_times_s[1][i] = self.rfb_data.on_time_intervals_s[i][0]  # End of on transition
            transition_times_s[3][i] = self.rfb_data.off_time_intervals_s[i][0]  # End of off transition

        transition_amp_w = [[float('nan')] * num_cycles, [float('nan')] * num_cycles, [float('nan')] * num_cycles,
                            [float('nan')] * num_cycles]
        for i in range(num_cycles):
            if not i == 0:
                # Beginning of on transition
                transition_amp_w[0][i] = self.rfb_data.acoustic_powers_w[self.rfb_data.off_indices[i - 1][1]]
            else:
                # Beginning of on transition
                transition_amp_w[0][i] = self.rfb_data.acoustic_powers_w[self.rfb_data.awg_on_ray.index(True) - buffer]
            # Beginning of off transition
            transition_amp_w[2][i] = self.rfb_data.acoustic_powers_w[self.rfb_data.on_indices[i][1]]

            transition_amp_w[1][i] = self.rfb_data.acoustic_powers_w[self.rfb_data.on_indices[i][0]]  # End of on transition
            transition_amp_w[3][i] = self.rfb_data.acoustic_powers_w[self.rfb_data.off_indices[i][0]]  # End of off transition

        power_on_w = transition_amp_w[1]
        power_off_w = transition_amp_w[2]
        cumulative_results = (
            [[mean(power_on_w), mean(power_off_w),
              self.rfb_data.acoustic_power_on_mean],
             [self.rfb_data.p_on_rand_unc, self.rfb_data.p_on_rand_unc, self.rfb_data.p_on_rand_unc],
             [self.rfb_data.p_on_total_unc, self.rfb_data.p_on_total_unc, self.rfb_data.p_on_total_unc]]
        )

        # todo: check that p_on_rand_unc is the one we want
        self.file_saver.store_measure_rfb_waveform_csv(
            element_number=self.element,
            ua_serial_number=self.test_data.serial_number,
            freq_mhz=frequency_MHz,
            diameter_mm=float(
                self.system_info["Hydrophone system"]["Hydrophone Diameter"].split(" ")[0].replace('"', "")
            ),
            propagation_distance_mm=15.000000,
            T_decC=self.rfb_data.water_temperature_c,
            UC_percent=float(self.rfb_data.p_on_rand_unc),
            power_ratio=1.000000,
            g_mpersecsqrd=9.810000,
            cal_fact=14600.571062,
            power_on_w=power_on_w,
            power_off_w=power_off_w,
            cumulative_results=cumulative_results,
            threshold=threshold,
            offset_s=offset,
            absorption=absorption,
            transducer_size=transducer_size,
            focusing=focusing,
            absorb_trans_times=transition_times_s,
            transition_amps=transition_amp_w,
            raw_data=raw_data,
            frequency_range=frequency_range
        )

        ### End extract_file_data

        self.test_data.log_script(["", "End", "", ""])

    def __begin_rfb_logger_thread(self, rfb_data: RFBData):
        self.rfb_logger = RFBDataLogger(rfb_data, self.Balance, self.Forward_Power_Meter, self.Reflected_Power_Meter,
                                        config=self.config)
        self.AWG.output_signal.connect(self.rfb_logger.update_awg_on)
        self.rfb_logger.finished.connect(self.rfb_logger.deleteLater)
        self.rfb_logger.start(priority=QThread.HighPriority)

    def __wrap_up_rfb_logger(self):
        self.rfb_logger.quit()
        t.sleep(0.1)

    # calibration_data should be a 2d list: 1st col: cal data array, 2nd col: low freq, 3rd col: high freq
    def write_cal_data_to_ua_dialog(self, calibration_data):
        # todo: check that a dialog appears
        self.write_cal_data_to_ua_signal.emit(calibration_data)

    # todo: test that this turns off and disconnects all devices
    def wrap_up(self):
        for device in self.devices:
            device.wrap_up()
        self.stay_alive = False

    def log(self, message, level="info"):
        log_msg(self, root_logger=root_logger, message=message, level=level)

    def refresh_rfb_tab(self) -> bool:
        """
        Helper function which retrieves data from the rfb_logger and tells the rfb tab to update
        returns a boolean indicating whether to continue the script
        """
        if self.abort_immediately_var:
            # Stop the current method and any parent methods that called it
            return False

        rfb_cooldown_s = .05
        if t.time() - self.last_rfb_update_time > rfb_cooldown_s:
            self.rfb_data = self.rfb_logger.rfb_data
            self.update_rfb_tab_signal.emit()
            self.last_rfb_update_time = t.time()
        self.app.processEvents()
        return True

    @pyqtSlot(str)
    def exec_command(self, command):
        self.command = command
        self.condition.wakeAll()

    def sequence_pass_fail(self, action_type: str, error_detail: str) -> bool:
        """
        action_type should be either "Interrupt action" or "Pass fail action",
        error_detail should describe what went wrong.
        returns: a boolean indicating whether to continue the script
        when calling, the following is recommended:

        cont = sequence_pass_fail(...)
        if not cont:
            return
         """

        self.log(level='action_type', message=f'{error_detail}')
        self.test_data.log_script(["", action_type, error_detail, ""])

        k1 = 'Sequence pass/fail'
        if k1 in self.config and action_type in self.config[k1]:
            if self.config[k1][action_type].upper() == 'RETRY AUTOMATICALLY':
                self.retry_if_retry_enabled(action_type, error_detail)
                return False
            elif self.config[k1][action_type].upper() == 'NO DIALOG (ABORT)':
                self.log(error_detail + ', aborting script.', self.error)
                self.abort_after_step()
                return False

            elif self.config[k1][action_type].upper() == 'PROMPT FOR RETRY':
                cont = self.prompt_for_retry(error_detail)
                if not cont:
                    return False
            else:
                self.log(
                    "invalid setting for Sequence pass/fail : interrupt action in config file; defaulting to prompt user",
                    self.warn)
                self.prompt_for_retry(error_detail)
        return True

        # todo: make sure that ignoring errors and continuing is reserved for engineers and admin_pass_field

    def prompt_for_retry(self, error_detail: str) -> bool:
        self.user_prompt_signal.emit(F"{error_detail}\n\n"
                                     F"Abort to end the UA testing sequence.\nRetry to re-run"
                                     F" this test.\nContinue to move to the next test in the "
                                     F"sequence.", True)
        cont = self.cont_if_cont_clicked()
        if not cont:
            return False
        return True

    def retry_if_retry_enabled(self, action_type: str, error_detail: str):
        if action_type != 'Interrupt action' and action_type != 'Pass fail action':
            self.log("invalid type passed for action_type in retry_if_retry_enabled, aborting", str(self.warn))
            self.abort_after_step()

        k1 = 'Sequence pass/fail'

        self.retry_clicked = True

        try:
            max_retries = self.config[k1]['Retries']
        except KeyError:
            self.log("no entry for Sequence pass/fail:Retries in config, defaulting to 5 retries", self.warn)
            max_retries = 5  # debug line

        if self.retry_count < max_retries:
            self.retry_count = self.retry_count + 1
            return
        else:
            self.log(f"retry limit reached for {error_detail}, aborting script", self.warn)
            self.abort_after_step()


class AbortException(Exception):
    pass


class RetryException(Exception):
    pass
