import distutils.util
import logging
import os
import re
import sys
import time as t
import traceback
from collections import OrderedDict
from typing import List, Tuple
import numpy as np
import pyvisa
from PyQt5 import QtCore
from PyQt5.QtCore import QMutex, QThread, QWaitCondition, pyqtSlot
from PyQt5.QtWidgets import QApplication, QComboBox
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
from Utilities.useful_methods import log_msg, get_element_distances, generate_calibration_data, find_int
from data_structures.rfb_data import RFBData
from data_structures.test_data import TestData
from data_structures.variable_containers import FileMetadata, SystemInfo, WaterLevel, FrequencyRange
from definitions import ROOT_DIR
from Hardware.galil_motor_controller import GalilMotorController

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

    # str is message for user to read, bool is whether to restrict the user from clicking continue/ignore
    user_prompt_signal = QtCore.pyqtSignal(str, bool)  # continue button
    user_prompt_pump_not_running_signal = QtCore.pyqtSignal(str)  # str is pump status
    user_prompt_signal_water_too_low_signal = QtCore.pyqtSignal()  # str is water level
    user_prompt_signal_water_too_high_signal = QtCore.pyqtSignal()
    show_write_cal_data_dialog_signal = QtCore.pyqtSignal(list)  # list is 2d array of calibration data
    retracting_ua_warning_signal = QtCore.pyqtSignal()
    # Contains a pass/fail list of booleans and a list of descriptions
    script_complete_signal = QtCore.pyqtSignal(list, list)
    user_info_signal = QtCore.pyqtSignal(str)
    user_question_signal = QtCore.pyqtSignal(str)  # str is question to be asked

    system_info_signal = QtCore.pyqtSignal(SystemInfo)

    # Script metadata
    description_signal = QtCore.pyqtSignal(str)
    created_on_signal = QtCore.pyqtSignal(str)
    created_by_signal = QtCore.pyqtSignal(str)
    num_tasks_signal = QtCore.pyqtSignal(int)
    script_name_signal = QtCore.pyqtSignal(str)

    # Emits the number of the task as shown in the .wtf file, not including repeats. Pretest_initialization should be 0
    task_number_signal = QtCore.pyqtSignal(int)
    # Tracks the index of the task in the order it is executed, including repeats. Pretest_initialization should be 0
    task_index_signal = QtCore.pyqtSignal(int)

    element_number_signal = QtCore.pyqtSignal(str)
    script_info_signal = QtCore.pyqtSignal(list)

    logger_signal = QtCore.pyqtSignal(str)
    enable_ui_signal = QtCore.pyqtSignal(bool)
    no_script_loaded_signal = QtCore.pyqtSignal()
    critical_error_signal = QtCore.pyqtSignal(str)

    # Tab signal
    profile_plot_signal = QtCore.pyqtSignal(list, list, str)
    plot_signal = QtCore.pyqtSignal(list, list, float)  # float is refresh rate

    update_rfb_tab_signal = QtCore.pyqtSignal()
    # contains

    # sets the current tab text of the main window (must match a tab name of the main window
    set_tab_signal = QtCore.pyqtSignal(list)

    # controls whether the buttons in various tabs are enabled, should be emitting false whenever scripting and vice 
    # versa 
    button_enable_toggle_for_scripting = QtCore.pyqtSignal(bool)

    Motors = None

    # Global variables section

    def __init__(self, system_info, parent, config: dict, access_level='Operator'):
        """Initializes various critical variables for this class, as well as setting thread locking mechanisms."""
        super().__init__(parent=parent)
        self.script_has_description = False
        self.script_description = None
        self.access_level = access_level
        self.error_message = None
        self.thread_cont_mutex = None
        self.critical_error_flag = False
        self.rfb_data = None
        self.no_clicked_variable = None
        self.yes_clicked_variable = None
        self.oscilloscope_averages = 1
        self.abort_guard = False
        self.oscilloscope_channel = 1

        self.warn = str(logging.WARNING)  # sets variable for shorter typing
        self.error = str(logging.ERROR)  # sets variable for shorter typing

        self.config = config
        self.system_info = system_info

        # variables controlling automatic sensor updates
        self.last_rfb_update_time = t.time()
        self.last_profile_update_time = t.time()
        # decreasing these values improves the refresh rate of the sensors at the cost of responsiveness
        self.sensor_refresh_interval_s = self.config['Debugging']['sensor_refresh_interval_s']
        self.last_sensor_update_time = 0.0

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
        for _ in range(10):
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
        # structure of 2D task_execution_order list is [[task number, element_number, loop_number]...]
        self.task_execution_order = None
        self.task_names = None

        self.element = 1

        # Tracks whether a script is being executed
        self.currently_scripting = False
        self.button_enable_toggle_for_scripting.emit(True)  # turn on buttons/fields
        self.was_scripting = False

        # Flags for the wait_for_cont method, when a dialog is waiting for user action
        self.continue_clicked_variable = True
        self.retry_clicked_variable = False
        self.abort_clicked_variable = False

        self.abort_immediately_variable = False

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

        if hasattr(self.parent, 'access_level_combo'):
            if isinstance(self.parent.access_level_combo, QComboBox):
                self.access_level = self.parent.access_level_combo.currentText()

        simulate_access = self.access_level.upper() != "Operator".upper()

        if self.config["Debugging"]["simulate_motors"] and simulate_access:
            from Hardware.Simulated.simulated_motor_controller import (SimulatedMotorController)
            self.Motors = SimulatedMotorController(config=self.config, lock=self.motor_control_lock)
        else:
            self.Motors = GalilMotorController(config=self.config, lock=self.motor_control_lock)

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
        """Attempts to connect all hardware in the devices list, warns user if hardware could not connect and waits
        for their response. Also sets the class' oscilloscope channel and averages and emits signal to MainWindow.py """
        i = 0
        while i < len(self.devices):
            device = self.devices[i]
            connected, feedback = device.connect_hardware()
            if not connected:
                self.user_prompt_signal.emit(f"{device.device_key} Could not connect\n\n{feedback}", False)
                try:
                    self.wait_for_cont()
                except RetryException:
                    i = i - 1
                except AbortException:
                    self.app.exit(-1)
            i = i + 1

        self.oscilloscope_averages = self.Oscilloscope.averages
        self.oscilloscope_channel = self.Oscilloscope.channel
        self.update_system_info()
        self.enable_ui_signal.emit(True)
        self.no_script_loaded_signal.emit()

        # Get the position of the motors
        if self.Motors.connected:
            lock_acquired = self.motor_control_lock.tryLock()
            if lock_acquired:
                self.Motors.get_position(mutex_locked=True)
                self.motor_control_lock.unlock()

    def update_system_info(self):
        """
        Retrieve system info from devices, pass them to the system info tab, which overwrites systeminfo.ini
        with the info it finds
        """
        info = SystemInfo()
        info.oscilloscope_sn = self.Oscilloscope.get_serial_number()
        if info.oscilloscope_sn is None:
            self.enable_ui_signal.emit(True)
            self.sequence_pass_fail('Interrupt action', "Oscilloscope serial number not found")
        info.awg_sn = self.AWG.get_serial_number()
        if info.awg_sn is None:
            self.enable_ui_signal.emit(True)
            self.sequence_pass_fail('Interrupt action', "AWG serial number not found")
        info.forward_power_sn = self.Forward_Power_Meter.get_serial_number()
        if info.forward_power_sn is None:
            self.enable_ui_signal.emit(True)
            self.sequence_pass_fail('Interrupt action', "AWG serial number not found")
        info.reflected_power_sn = self.Reflected_Power_Meter.get_serial_number()
        info.thermocouple_sn = self.thermocouple.get_serial_number()
        info.rf_balance_sn = self.Balance.get_serial_number()
        if info.rf_balance_sn is None:
            self.enable_ui_signal.emit(True)
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
            self.condition.wait(self.mutex, 1)
            if self.stay_alive is False:
                break

            # code block below checks the first part of the split command_ray to see what command is
            command = self.command.upper()
            command_ray = command.split(" ")

            if command_ray[0] == "CLOSE":
                self.wrap_up()
            elif command_ray[0] == "CONNECT":
                self.connect_hardware()
            elif "CAPTURE".upper() in command.upper():
                self.capture_oscilloscope_and_plot()
            elif command_ray[0] == "STEP":
                self.advance_script()
            elif command_ray[0] == "ABORT":
                self.abort_after_step()
            elif command[0:4] == "SCAN":
                self.command_scan(self.command)
            else:  # What to do when there is no command
                # If a script has just ended, show script_complete dialog
                if self.currently_scripting:
                    self.button_enable_toggle_for_scripting.emit(False)  # disable buttons/fields
                    if self.task_names is None:
                        self.abort_after_step()
                        self.enable_ui_signal.emit(True)
                    else:
                        self.advance_script()
                else:
                    self.update_sensors()

            # Show script complete dialog whenever a script finishes
            if not self.currently_scripting and self.was_scripting:
                self.button_enable_toggle_for_scripting.emit(True)  # enabled fields/buttons
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
        """
        Triggers when the user hits the run script button in the UI, sets various scripting variables to appropriate
        values and logs
        """
        self.abort_immediately(log=False)
        log_msg(self, root_logger, level="info", message="Running script")
        self.currently_scripting = True
        self.button_enable_toggle_for_scripting.emit(False)  # disables main window fields/buttons during test
        self.was_scripting = True
        self.abort_immediately_variable = False

    def update_sensors(self):
        """Attempts to update the last sensor update time, the water level, thermocouple reading, oscilloscope trace
        (if applicable) and ua pump status. Runs according to the sensor refresh interval, if the program seems
        unresponsive try increasing the sensor_refresh_interval_s variable in local.yaml
        Returns if the user is not looking at positional feedback"""
        if self.parent is not None and not hasattr(self.parent, "tabWidget"):
            return

        if t.time() - self.last_sensor_update_time > self.sensor_refresh_interval_s:
            self.last_sensor_update_time = t.time()

            if self.thermocouple.connected:
                self.thermocouple.get_reading()

            if self.IO_Board.connected:
                self.IO_Board.get_water_level()

            if self.IO_Board.connected:
                self.IO_Board.get_ua_pump_reading()

            if self.thermocouple.connected:
                self.thermocouple.get_reading()

            if self.Oscilloscope.connected and self.config["Debugging"]["oscilloscope_realtime_capture"]:
                self.capture_oscilloscope_and_plot()
            else:
                pass

    def capture_scope(self, channel: int = 1, plot: bool = True):
        """
        captures time and voltage data from the oscilloscope hardware, stores them into two separate lists and returns
        them to the calling function. Defaults to channel 1 on the oscilloscope and sets the plot flag to true
        """
        try:
            time, voltage = self.Oscilloscope.capture(channel=channel)
            if plot:
                self.plot_scope(time, voltage)
            return time, voltage
        except pyvisa.errors.InvalidSession:
            self.log(level='error', message="Could not capture, oscilloscope resource closed")
        except TypeError:
            self.log(level='error', message="Could not capture")
        return [], []

    def plot_scope(self, time, voltage):
        """
        takes the time and voltage data (lists) from the oscilloscope and sends a signal to main window to plot them
        """
        time_elapsed = t.time() - self.start_time
        if time_elapsed == 0:
            return

        refresh_rate = round(1 / time_elapsed, 1)
        self.plot_signal.emit(time, voltage, refresh_rate)

    # noinspection PyUnresolvedReferences
    def capture_oscilloscope_and_plot(self):
        """
        Captures an oscilloscope trace and plots it to the scan tab, assuming the plot is ready
        """

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

    def load_script(self, path):
        """
        takes the script file and parses the info within it into various lists and dictionaries so the program can
        run the script, requires a path argument to the script
        """
        self.abort_immediately(log=False)  # we don't want the save prompt for this use of abort

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
        self.script_has_description = False
        f = open(path, "r")
        for line in f:
            ray = line.split(" = ")

            # Populate script metadata to UI using signals
            if "# OF TASKS" in ray[0].upper():
                self.num_tasks_signal.emit(int(ray[1].replace('"', "")))
            elif "CREATEDON" in ray[0].upper():
                self.created_on_signal.emit(ray[1].replace('"', ""))
            if "CREATEDBY" in ray[0].upper():
                self.created_by_signal.emit(ray[1].replace('"', ""))
            elif "DESCRIPTION" in ray[0].upper():
                self.script_has_description = True
                self.set_tab_signal.emit(["Edit Script"])
                self.script_description = ray[1].replace('"', "")
                self.description_signal.emit(self.script_description)

            current_line = current_line + 1
            if line == '\n':
                if task_variables:  # ensures task variable list isn't empty; prevents adding empty sub lists to main
                    # list
                    tasks.append(OrderedDict(task_variables))
                    # empties out variable list for task since we're ready to move to the next set
                    task_variables.clear()
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

                if "Loop over elements" in x1:  # detects if we've encountered a loop builder task
                    building_loop = True  # set a flag that we're building a loop for the script
                    adding_elements_to_loop = True  # set a flag that we're adding element names from script for loop

                # if we're on a line that adds an element name for the loop
                if adding_elements_to_loop and "Element" in x0:
                    # split the left side of the variable assigner by space
                    element_name_to_split = x0.split(" ")
                    # retrieve the second word of the left side, that's the element name
                    element_name = element_name_to_split[1]
                    if x1.upper() == 'TRUE':  # we only want to add elements in the loop if it equals "True"
                        element_names_for_loop.append(int(element_name))

                if "End loop" in x1:  # script will have "End loop" in right side of task type to end loop block
                    building_loop = False  # set the building loop flag to false since the loop block is done
                    self.loops.append(list([list(element_names_for_loop), list(task_number_for_loop)]))
                    element_names_for_loop.clear()
                    task_number_for_loop.clear()
                    self.task_execution_order.pop()

                    # appends a 3 item list in taskExecOrder, the first part being the task number
                    # the second item being the element number and the third is the loop number
                    for i in range(len(self.loops[len(self.loops) - 1][0])):
                        for j in range(len(self.loops[len(self.loops) - 1][1])):
                            self.task_execution_order.append(
                                [self.loops[len(self.loops) - 1][1][j], self.loops[len(self.loops) - 1][0][i],
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

        for i in range(
                len(self.task_execution_order)):  # if the task step does not have element, set the element to "None"
            # type in order to make it a list
            if not isinstance(self.task_execution_order[i], list):
                self.task_execution_order[i] = [self.task_execution_order[i], None]

        self.task_names = list()  # makes the task_names object into a list
        for i in range(len(self.task_execution_order)):
            # tasks and task_execution_order are # offset by 1
            if "Task type" in tasks[self.task_execution_order[i][0] + 1].keys():
                self.task_names.append(tasks[self.task_execution_order[i][0] + 1]["Task type"])

        self.task_arguments = list()  # makes the task_arguments object into a list
        for i in range(len(self.task_execution_order)):
            # tasks[self.taskExecOrder[i][0] + 1].pop("Task type", None)
            self.task_arguments.append(
                tasks[self.task_execution_order[i][0] + 1])  # task_arguments and task_execution_order are offset by 1

        if not self.script_has_description:
            self.script_description = ''

        if self.script_description is None or self.script_description == '':
            self.description_signal.emit('')
        else:
            self.description_signal.emit(self.script_description)
        self.script_info_signal.emit(tasks)
        self.num_tasks_signal.emit(len(self.task_names))

        if len(tasks) == 0 or (
                len(tasks) == 1 and '# of Tasks' in tasks[0]):  # checks if there are no tasks, with and without header
            self.user_info_signal.emit(
                "You cannot run a script that has no tasks, please select a script that has tasks.")
            self.abort_immediately()
            self.no_script_loaded_signal.emit()
        else:
            self.set_tab_signal.emit(["Edit Script"])

    # get UA serial no. and append behind date

    @pyqtSlot()
    def advance_script(self):
        """Updates script step and executes the next step if applicable, and implements abort, continue, and retry"""
        try:
            if self.task_names is None:  # we need a task name, otherwise the script cannot continue
                self.abort_immediately()  # abort the script immediately
                self.enable_ui_signal.emit(True)  # re-enable various buttons in the main window
                return  # exit this method

            if self.retry_clicked_variable is True:  # if the user clicked retry on a prompt
                self.step_index = self.step_index - 1  # retry the step via decrementing the step index
                self.retry_clicked_variable = False  # sets the retry variable to false so the retry function may happen
                # again

            # advance to the next step if the previous has been completed
            self.step_index = self.step_index + 1

            # if a script is being executed, and the step index is valid, and the previous step is complete,
            # run the next script step

            if self.step_index > len(self.task_names):
                self.currently_scripting = False
                self.button_enable_toggle_for_scripting.emit(True)  # turn on buttons/fields in main window
                return

            if self.task_arguments is not None and self.task_names is not None and \
                    self.task_execution_order is not None:
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

            if not self.currently_scripting:
                self.enable_ui_signal.emit(True)
                self.button_enable_toggle_for_scripting.emit(True)

        # Catch all errors while advancing the script and handle them by showing the user a dialog with the traceback
        except Exception:
            self.abort_immediately()
            self.error_message = traceback.format_exc()
            traceback.print_exc()
            self.log(traceback.format_exc(), "error")
            self.critical_error_flag = True

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

        # if the element in the self.taskExecOrder isn't None
        if self.task_execution_order[self.step_index][1] is not None:
            # set the element to be operated on to the one in self.taskExecOrder
            args['Element'] = self.task_execution_order[self.step_index][1]

        if "MEASURE ELEMENT EFFICIENCY (RFB)" in name.upper():
            self.measure_element_efficiency_rfb_multithreaded(args)
        elif "PRE-TEST INITIALISATION" in name.upper():
            self.pretest_initialization()
        elif "FIND ELEMENT" in name.upper():
            self.find_element(args)
        elif "SAVE RESULTS" in name.upper():
            self.save_results(args)
        elif "PROMPT USER FOR ACTION" in name.upper():
            self.prompt_user_for_action(args)
        elif "HOME SYSTEM" in name.upper():
            self.home_system(args)
        elif "OSCILLOSCOPE CHANNELS" in name.upper():
            self.configure_oscilloscope_channels(args)
        elif "OSCILLOSCOPE TIMEBASE" in name.upper():
            self.configure_oscilloscope_timebase(args)
        elif "FUNCTION GENERATOR" in name.upper():
            self.configure_function_generator(args)
        elif "AUTOSET TIMEBASE" in name.upper():
            self.autoset_timebase()
        elif "MOVE SYSTEM" in name.upper():
            self.move_system(args)
        elif "SELECT CHANNEL" in name.upper() or "SELECT UA CHANNEL" in name.upper():
            self.select_ua_channel(args)
        elif 'FREQUENCY SWEEP' in name.upper():
            self.frequency_sweep(args)
        else:
            self.log(f"{name} is not a valid task name in the script, aborting immediately", "error")
            self.critical_error_flag = True
            self.error_message = f"{name} is not a valid task name in the script"
            self.abort_immediately()

        self.task_index_signal.emit(self.step_index + 1)

        # below helps explain loop and list logic
        # if len(self.taskExecOrder[self.step_index]) == 3:
        #     print(f"looped element {self.taskExecOrder[self.step_index][0]} is in iteration {self.taskExecOrder
        #     [self.step_index][1]} from loop {self.loops[self.taskExecOrder[self.step_index][2]]}")

    @pyqtSlot()
    def abort_after_step(self, log=True):
        """Aborts script when current step is done running"""

        if self.retry_clicked_variable:
            return
        if log:
            self.log("Aborting script after step")
        # Reset script control variables
        self.currently_scripting = False
        self.button_enable_toggle_for_scripting.emit(True)  # turn on fields/buttons in main window
        self.step_index = -1
        self.abort_immediately_variable = False
        self.task_number_signal.emit(0)
        self.task_index_signal.emit(0)

    @pyqtSlot()
    def abort_immediately(self, log=True):
        """
        Aborts script as soon as the current step checks abort_immediately var and returns or the step finishes.
        Any long-running step should check abort_immediately_var frequently and return false if the var is true
        """
        if log:
            self.log("Aborting script")
        # Reset script control variables
        self.currently_scripting = False
        self.button_enable_toggle_for_scripting.emit(True)  # we are not scripting, enable buttons/fields
        self.step_index = -1
        self.abort_immediately_variable = True
        self.task_number_signal.emit(0)
        self.task_index_signal.emit(0)
        # self.enable_ui_signal.emit(True)

    def cont_if_cont_clicked(self):
        """
        Waits and returns true if the user presses continue. Returns false if the user clicks abort or retry.
        Call this method after showing a dialog, and return if the result is false.
        """
        try:
            self.wait_for_cont()
            return True
        except AbortException:
            self.test_data.log_script(["", "User prompt", "FAIL", "Closed by user"])
            if self.abort_immediately_variable:  # if abort immediately is true
                self.abort_immediately()
                return False
            else:  # if abort immediately is not true
                self.abort_after_step()
                return False
        except RetryException:
            self.test_data.log_script(["", "User prompt", "Retry step", ""])
            self.log("Retrying step")
            self.retry_clicked_variable = True
            return False

    def wait_for_cont(self):
        """
        Sets continue variable to False and waits for it to be true, raising exceptions if the user
        wants to abort or retry. Always handle these exceptions.
        """
        self.continue_clicked_variable = False
        self.retry_clicked_variable = False
        self.abort_clicked_variable = False

        while not self.continue_clicked_variable:
            # check if script has been aborted
            if self.retry_clicked_variable:
                self.retry_clicked_variable = False
                raise RetryException
            if self.abort_clicked_variable:
                self.abort_clicked_variable = False
                raise AbortException
            if self.abort_immediately_variable:
                self.abort_immediately()
                return False
        return True

    def cont_if_answer_clicked(self):
        """
        Waits and returns true if the user presses continue. Returns false if the user clicks close window button.
        Call this method after showing a dialog, and return if the result is false.
        """
        try:
            self.wait_for_answer()
            return True
        except AbortException:
            self.test_data.log_script(["", "User prompt", "FAIL", "Closed by user"])
            if self.abort_immediately_variable:  # if abort immediately is true
                self.abort_immediately()
                return False
            else:  # if abort immediately is not true
                self.abort_after_step()
                return False

    def wait_for_answer(self) -> bool:
        """
        Sets answer variables to false and waits for user to make selection
        """
        self.yes_clicked_variable = False
        self.no_clicked_variable = False

        while not self.yes_clicked_variable and not self.no_clicked_variable:
            if self.yes_clicked_variable:
                self.thread_cont_mutex = True
                return True
            if self.no_clicked_variable:
                self.thread_cont_mutex = True
                return False
    @pyqtSlot()
    def continue_clicked(self):
        """Flags cont_clicked to continue the current step"""
        self.continue_clicked_variable = True
        self.abort_clicked_variable = False
        self.abort_immediately_variable = False

    @pyqtSlot()
    def retry_clicked(self):
        """Flags cont_clicked to retry the current step"""
        self.retry_clicked_variable = True

    @pyqtSlot()
    def abort_clicked(self):
        """Flags cont_clicked to abort the current step"""
        self.abort_clicked_variable = True

    @pyqtSlot()
    def yes_clicked(self):
        """Flags yes_selected to allow user to consent to question"""
        self.yes_clicked_variable = True
        self.no_clicked_variable = False

    @pyqtSlot()
    def no_clicked(self):
        """Flags yes_selected to allow user to consent to question"""
        self.no_clicked_variable = True
        self.yes_clicked_variable = False

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
        if self.test_data.skip_write_to_ua or self.test_data.write_result is None:
            pass_list[10] = "N/A"
        elif self.test_data.write_result:
            pass_list[10] = "PASS"
        else:
            pass_list[10] = "FAIL"

        # add the result for the device as a whole to the results_summary
        self.test_data.set_pass_result(11, device_result)

        self.script_complete_signal.emit(pass_list, description_list)
        if self.critical_error_flag:
            self.critical_error_signal.emit(self.error_message)
        self.critical_error_flag = False  # set this back to false so if user repeats test, same mechanism will work
        self.error_message = ""
        self.currently_scripting = False
        self.button_enable_toggle_for_scripting.emit(True)  # not scripting, turn on buttons/fields
        self.enable_ui_signal.emit(True)

        self.test_data.log_script(["Script complete", "", "", ""])
        self.set_tab_signal.emit(["Results"])

    def pretest_initialization(self):
        """Home the UA, perform hardware checks, and prompt the user until they pass,
        takes in a variable dict as a parameter"""

        # add first 4 lines of script log
        self.test_data.log_script([f"{self.test_data.serial_number}-{self.test_data.test_date_time}",
                                   '', '', ''])  # this is the first line
        self.test_data.log_script(["Running script: ", self.test_data.script_name, '', '', ''])
        self.test_data.log_script(["Pretest_initialization", '', '', ''])
        self.test_data.log_script(['', "Prompt username+UA serial", 'OK', ''])

        # Check if WTF-IB is connected and add that to the script log
        if self.test_data.serial_number != "":
            self.test_data.log_script(["", "Get UA Serial", "Connected", "OK"])
        else:
            self.test_data.log_script(["", "Get UA Serial", "Connected", "FAIL"])
            cont = self.sequence_pass_fail(error_detail="Get UA Serial in pretest initialisation failed",
                                           action_type="Interrupt action")
            if not cont:
                return
            self.retry_clicked_variable = False

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

        home_successful = self.home_system(var_dict={"Axis to home": "All Axes"}, show_prompt=True)

        if home_successful:
            self.test_data.log_script(['', "Home all", f"OK; X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}", ''])
        else:
            self.test_data.log_script(['', "Home all", f"FAIL; X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}", ''])
            if self.abort_immediately_variable:  # we want to abort immediately if the user clicks out of this prompt
                return
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

        if self.abort_immediately_variable:
            return

        self.user_prompt_signal.emit("Please ensure that the power amplifier is on",
                                     False)  # this task cannot be automated
        cont = self.cont_if_cont_clicked()  # wait for continue to be clicked
        if not cont:  # if the user did not click continue
            return  # exit this method, abort/retry flags are handled by the cont_if_cont_clicked method
        self.test_data.log_script(["", "Prompt PowerAmp", "OK", ""])  # at this point, the prompt ran successfully

        if self.file_saver.directories_created:  # check if the saving directories were successfully created
            self.test_data.log_script(["", "CreateDataDirectories", "OK", ""])  # write result to the log script
        else:
            self.test_data.log_script(["", "CreateDataDirectories", f"FAIL", ""])

        try:  # checking the self.log() functionality
            self.log("Checking ability to log")
            self.test_data.log_script(["", "Create h/w log", "OK", ""])
        except Exception as e:  # self.log() doesn't work if this block is ran, report issue to user
            self.test_data.log_script(["", "Create h/w log", f"FAIL {e}", ""])

        self.test_data.log_script(["", "Initialize results FGV", "OK", ""])
        self.test_data.log_script(["", "duplicate main script", "OK", ""])

        while True:
            water_level = self.IO_Board.get_water_level()  # attain the water level from the hardware variable

            if water_level == WaterLevel.below_level:  # if the water level is below level
                # launch the dialog box signifying this issue
                self.user_prompt_signal_water_too_low_signal.emit()
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return
                self.IO_Board.fill_tank()  # if user clicked continue, send the fill tank command
            elif water_level == WaterLevel.above_level:  # if the water level is above level
                # launch the dialog box signifying this issue
                self.user_prompt_signal_water_too_high_signal.emit()
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return

                self.IO_Board.drain_tank_to_level()
            else:
                # log successful water level test if we've reached this point in the code
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
        """Looks for an integer in the string, otherwise returns the current element"""
        try:
            self.element = find_int(element_str)
        except AttributeError:
            self.log(f"Element number not given, using previous element: {self.element}")
        return self.element

    def channel_str_to_int(self, channel_str):
        """Looks for an integer in the string, otherwise returns the current channel"""
        try:
            self.element = int(re.search(r"\d+", str(channel_str)).group())
        except AttributeError:
            self.log(f"Element number not given, using previous element: {self.oscilloscope_channel}")
        return self.element

    def find_element(self, var_dict):
        """
        Find UA element with given number by scanning for a maximum VSI or RMS
        returns a boolean indicating whether to continue the script
        """
        self.set_tab_signal.emit(["Scan", "1D Scan"])
        self.element = self.element_str_to_int(var_dict["Element"])
        x_increment_mm = float(var_dict["X Incr. (mm)"])
        x_points = int(var_dict["X #Pts."])
        theta_increment_degrees = float(var_dict["Theta Incr. (deg)"])
        theta_points = int(var_dict["Theta #Pts."])
        self.oscilloscope_channel = int(var_dict["Scope channel"][8:])
        acquisition_type = var_dict["Acquisition type"]
        averages = int(re.search(r"\d+", str(var_dict["Averages"])).group())
        data_storage = var_dict["Data storage"]
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        # max_position_error_mm = float(var_dict["Max. position error (+/- mm)"])
        element_position_test = bool(var_dict["ElementPositionTest"])
        max_angle_variation_degrees = float(var_dict["Max angle variation (deg)"])
        beam_angle_test = bool(var_dict["BeamAngleTest"])
        frequency_settings = var_dict["Frequency settings"]
        frequency_mhz = float(var_dict["Frequency (MHz)"])
        amplitude_mVpp = float(var_dict["Amplitude (mV)"])
        burst_count = int(float(var_dict["Burst count"]))

        if storage_location == 'UA Results Directory' or data_directory == '':
            storage_location = ''
        else:
            storage_location = data_directory

        # If on the first element, set the tab to the scan tab
        if self.element == 1:
            self.set_tab_signal.emit(["Scan"])

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
        self.log(
            f"Finding element {self.element}, near coordinate x = {element_x_coordinate}, r = {element_r_coordinate}")

        # Configure function generator
        awg_var_dict = dict()
        awg_var_dict["Amplitude (mVpp)"] = amplitude_mVpp
        awg_var_dict["Frequency (MHz)"] = frequency_mhz
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

        self.autoset_timebase()

        if element_position_test:
            self.Motors.go_to_position(['R'], [-180], enable_ui=False)
            cont = self.scan_axis(self.element, axis='X', num_points=x_points, increment=x_increment_mm,
                                  ref_position=element_x_coordinate,
                                  go_to_peak=True, data_storage=data_storage, update_element_position=True,
                                  acquisition_type=acquisition_type,
                                  averages=averages, storage_location=storage_location)
            if not cont:
                return False

        self.home_system({'Axis to home': 'Theta'})

        if beam_angle_test:
            cont = self.scan_axis(self.element, axis='Theta', num_points=theta_points,
                                  increment=theta_increment_degrees,
                                  ref_position=self.config["WTF_PositionParameters"]["ThetaHydrophoneCoord"],
                                  go_to_peak=False, update_element_position=True, data_storage=data_storage,
                                  acquisition_type=acquisition_type,
                                  averages=averages, storage_location=storage_location)

            if not cont:
                return False

        self.home_system({"Axis to home": "Theta"})

        self.AWG.set_output(False)
        self.test_data.log_script(['', 'Disable UA and FGen', 'Disabled FGen output', ''])
        self.test_data.log_script(['', 'End', 'OK', ''])

        if abs(self.element_r_coordinates[self.element] + 90) > max_angle_variation_degrees:
            self.log(level='error', message=f'Maximum theta coordinate of {self.element_r_coordinates[self.element]} '
                                            f'deviates from -90 more than the allowed maximum of '
                                            f'{max_angle_variation_degrees}')
        return True

    # Reference position is the center of the scan range

    def scan_axis(self, element: int, axis, num_points, increment, ref_position, data_storage, go_to_peak,
                  storage_location,
                  update_element_position: bool, scope_channel: int = 1, acquisition_type='N Averaged Waveform',
                  averages=1, filename_stub="FindElement") -> bool:
        """

        Args:
            element:
            axis:
            num_points:
            increment:
            ref_position:
            data_storage: "do not store", "Store entire waveform", "store profiles only"
            go_to_peak:
            storage_location:
            update_element_position:
            scope_channel:
            acquisition_type:
            averages:
            filename_stub:

        Returns: A boolean indicating whether to continue the script
        """

        self.element = element
        self.select_ua_channel(var_dict={"Element": self.element})

        self.oscilloscope_channel = scope_channel

        if axis == 'X':
            axis_letter = 'X'
        elif axis == 'Theta':
            axis_letter = 'R'
        else:
            self.user_prompt_signal.emit("Invalid axis parameter, aborting", False)
            return self.abort_after_step()
        if self.Motors.rotational_ray[self.Motors.ax_letters.index(axis_letter)]:
            pos_units_str = "deg"
            axis_label = "Angle (deg)"
        else:
            pos_units_str = "mm"
            axis_label = "Distance (mm)"

        if acquisition_type.upper() == "N Averaged Waveform".upper():
            self.Oscilloscope.set_averaging(averages)
        else:
            self.Oscilloscope.set_averaging(1)

        # Loop over x through a given range, move to the position where maximal RMS voltage was measured
        positions = list()
        vsi_values = list()
        y_units_str = "RMS Voltage (V)"

        # sweep from the expected element position minus the max error to the expected element position plus max error
        position = -1 * (num_points * increment) / 2 + ref_position

        # begin with arbitrarily low values which will be overwritten
        max_vsi = -1 * sys.float_info.max
        max_position = -1 * sys.float_info.max

        for i in range(num_points):
            if self.abort_immediately_variable:
                # Stop the current method and any parent methods that called it
                return False

            self.Motors.go_to_position([axis_letter], [position], enable_ui=False)
            position = position + increment

            if self.config["Analysis"]["capture_rms_only"]:
                vsi = self.Oscilloscope.get_rms()
            else:
                y_units_str = 'VSI (Voltage Squared Integral)'
                times_s, voltages_v = self.capture_scope(channel=self.oscilloscope_channel)
                if times_s == [] or voltages_v == []:
                    cont = self.sequence_pass_fail(action_type='Interrupt action',
                                                   error_detail='Oscilloscope capture failed', )
                    if not cont:
                        return False

                if 'entire waveform'.upper() in data_storage.upper():
                    self.__save_hydrophone_waveform(axis=axis, waveform_number=i + 1, times_s=times_s,
                                                    voltages_v=voltages_v, storage_location=storage_location,
                                                    filename_stub=filename_stub, x_units_str='Time (s)',
                                                    y_units_str=y_units_str)

                vsi = self.find_vsi(times_s=times_s, voltages_v=voltages_v)

            try:
                if vsi > max_vsi:
                    max_vsi = vsi
                    max_position = position
            except TypeError:
                return False

            positions.append(position)
            vsi_values.append(vsi)
            self.__refresh_profile_plot(positions, vsi_values, axis_label)

        self.test_data.log_script(['', 'Move to element', f"Moved to X={'%.2f' % self.Motors.coords_mm[0]}, "
                                                          f"Th={'%.2f' % self.Motors.coords_mm[1]}", ''])

        self.log(f"Maximum of {max_vsi} @ {axis} = {max_position} {pos_units_str}")

        if update_element_position:
            if axis == "X":
                self.element_x_coordinates[self.element] = max_position
            else:
                self.element_r_coordinates[self.element] = max_position + 90
                # Refresh the angle average in self.test_data
                self.test_data.calculate_angle_average()

        self.test_data.set_max_position(axis, self.element, max_position)

        status_str = f'Start {axis} {"%.2f" % self.element_x_coordinates[self.element]} mm; Incr {axis} ' \
                     f'{increment} {pos_units_str}; #Points {num_points}; Peak {axis} = ' \
                     f'{"%.2f" % max_position} {pos_units_str};'

        if go_to_peak:
            status = self.Motors.go_to_position([axis_letter], [max_position], enable_ui=False)
            if status:
                status_str = status_str + f" moved to {axis} = {max_position} {pos_units_str}"
            else:
                status_str = status_str + f"move to {axis} = {max_position} {pos_units_str} failed"

        self.test_data.log_script(["", f"Scan{axis} Find Peak {axis}:", status_str, ""])

        if 'Do not store'.upper() != data_storage.upper():
            self.__save_scan_profile(positions=positions, vsi_values=vsi_values,
                                     axis=axis, storage_location=storage_location, filename_stub=filename_stub,
                                     x_units_str=axis_label, y_units_str=y_units_str)

        # ensure finished profile plot is plotted on screen
        t.sleep(.05)
        self.__refresh_profile_plot(positions, vsi_values, axis_label)

        if self.app is not None:
            self.app.processEvents()
        return True

    def __refresh_profile_plot(self, x_data, y_data, y_label) -> bool:
        """
        Helper function which refreshes the profile plot tab but not too often to bog down the thread
        """
        if self.abort_immediately_variable:
            # Stop the current method and any parent methods that called it
            return False

        profile_cooldown_s = .05
        if t.time() - self.last_profile_update_time > profile_cooldown_s:
            self.profile_plot_signal.emit(x_data, y_data, y_label)
            self.last_profile_update_time = t.time()

        if self.app is not None:
            self.app.processEvents()
        return True

    def __save_hydrophone_waveform(self, axis, waveform_number, times_s, voltages_v, storage_location, filename_stub,
                                   x_units_str, y_units_str):
        """Saves an oscilloscope trace using the file handler"""
        metadata = FileMetadata()
        metadata.element_number = self.element
        metadata.axis = f"{axis}"
        metadata.x_units_str = x_units_str
        metadata.y_units_str = y_units_str
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

        self.file_saver.store_waveform(metadata=metadata, times=times_s, voltages=voltages_v,
                                       storage_location=storage_location, filename_stub=filename_stub)

    def __save_scan_profile(self, axis, positions, vsi_values, storage_location, filename_stub, x_units_str,
                            y_units_str):
        """Saves a voltage squared integral vs distance"""
        metadata = FileMetadata()
        metadata.element_number = self.element
        metadata.axis = f"{axis}"
        metadata.x_units_str = x_units_str
        metadata.y_units_str = y_units_str
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

        self.file_saver.save_find_element_profile(metadata=metadata, positions=positions, vsi_values=vsi_values,
                                                  storage_location=storage_location, filename_stub=filename_stub)

    def __save_frequency_sweep(self, frequencies, vsi_values, storage_location, filename_stub, y_units_str):
        """Saves voltage squared integral vs frequency data"""
        metadata = FileMetadata()
        metadata.element_number = self.element
        metadata.serial_number = self.test_data.serial_number
        metadata.X = self.Motors.coords_mm[0]
        metadata.Theta = self.Motors.coords_mm[1]
        metadata.nominal_low_frequency_MHz = self.test_data.low_frequency_MHz
        metadata.nominal_high_frequency_MHz = self.test_data.high_frequency_MHz
        metadata.amplitude_mVpp = self.AWG.state["amplitude_V"] * 1000
        metadata.x_units_str = 'Frequency (MHz)'
        metadata.y_units_str = y_units_str
        if self.AWG.state["burst_on"]:
            metadata.source_signal_type = "Toneburst"
        else:
            metadata.source_signal_type = "Continuous"
        metadata.num_cycles = self.AWG.state["burst_cycles"]

        self.file_saver.save_frequency_sweep(metadata=metadata, frequencies=frequencies, vsi_values=vsi_values,
                                             storage_location=storage_location, filename_stub=filename_stub)

    pyqtSlot(dict)

    def save_results(self, var_dict: dict) -> None:
        """Saves test summary data stored in self.test_data to a file on disk using the file handler self.file_saver"""
        try:
            save_summary_file: bool = bool(distutils.util.strtobool(var_dict["Save summary file"]))
        except KeyError:
            self.log(level='warning', message="no 'Save summary file' specified in script, defaulting to false")
            save_summary_file = False
        try:
            write_ua_calibration: bool = bool(distutils.util.strtobool(var_dict["Write UA Calibration"]))
        except KeyError:
            self.log(level='warning', message="no 'Write UA Calibration' specified in script, defaulting to false")
            write_ua_calibration = False
        try:
            prompt_for_calibration_write: bool = bool(distutils.util.strtobool(var_dict["PromptForCalWrite"]))
        except KeyError:
            self.log(level='warning', message="no 'PromptForCalWrite' specified in script, defaulting to false")
            prompt_for_calibration_write = False

        try:
            self.test_data.software_version = self.config["Software_Version"]
        except KeyError:
            self.log("'Software_Version' value not found in config file, defaulting to version 1.0")
            self.test_data.software_version = "1.0"

        self.test_data.calculate_angle_average()

        if prompt_for_calibration_write:  # displays the "write to UA" dialog box if this variable is true
            self.user_prompt_signal.emit("Do you want to write calibration data to UA?", False)

            calibration_data = generate_calibration_data(self.test_data)
            cont = self.cont_if_answer_clicked()  # sets cont variable to true if user clicked continue
            if not cont:  # if user did not click continue, return
                return
            if self.yes_clicked_variable:
                self.UAInterface.write_data(calibration_data)

        elif write_ua_calibration:
            calibration_data = generate_calibration_data(self.test_data)
            self.UAInterface.write_data(calibration_data)
        else:
            self.test_data.skip_write_to_ua = True

        # Save results summary to results folder
        if save_summary_file:  # ask for this in the abort methods
            self.file_saver.save_test_results_summary_and_log(test_data=self.test_data)

    def prompt_user_for_action(self, var_dict: dict) -> None:
        """
        Waits for the user select continue, abort or retry via sending a signal
        to the main window. It extracts the Prompt type and message from the passed
        dict
        """
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

    def configure_function_generator(self, var_dict: dict):
        """
        Set function generator to various desired settings, such as the mVpp, frequency, etc.
        from the passed variable dictionary.
        """
        mVpp: int = int(var_dict["Amplitude (mVpp)"])
        mode: str = var_dict["Mode"]  # INFO: mode can be 'Toneburst' or 'N Cycle'
        output: bool = bool(var_dict["Enable output"])
        frequency_options: str = var_dict["Set frequency options"]

        self.AWG.reset()

        if frequency_options == "Common low frequency" or frequency_options == 'Element pk low frequency':
            frequency_mhz = self.test_data.low_frequency_MHz
        elif frequency_options == "Common high frequency" or frequency_options == 'Element pk high frequency':
            frequency_mhz = self.test_data.high_frequency_MHz
        elif frequency_options == "From config cluster":
            frequency_mhz: float = float(var_dict["Frequency (MHz)"])
        else:
            self.user_prompt_signal.emit("Invalid frequency parameter, aborting", False)
            return self.abort_immediately()

        self.AWG.set_output(output)
        self.AWG.set_frequency_hz(int(frequency_mhz * 1000000))
        self.test_data.log_script(
            ["", "Configure FGen+PwrMeters", f"Frequency set to {frequency_mhz} MHz", "", ])
        self.AWG.set_amplitude_v(mVpp / 1000)

        if mode == "N Cycle" or "burst".upper() in mode.upper():
            self.AWG.set_burst(True)
            cycles = int(var_dict["#Cycles"])
            self.AWG.set_cycles(cycles)
        else:
            self.AWG.set_burst(False)

        self.test_data.log_script(["", "Config FGen", f"{mVpp}mVpp;{frequency_mhz}MHz,{mode}"])

    def configure_oscilloscope_channels(self, var_dict):
        c1_enabled = bool(var_dict["Channel 1 Enabled"])
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
        timebase_us = float(var_dict["Timebase"])
        delay_us = float(var_dict["Delay"])
        self.Oscilloscope.set_horizontal_scale_sec(timebase_us / 1000000)
        self.Oscilloscope.set_horizontal_offset_sec(delay_us / 1000000)

    def autoset_timebase(self):
        self.Oscilloscope.autoset_oscilloscope_timebase()

    def home_system(self, var_dict, show_prompt=False) -> bool:
        """
        Return axis to zero coordinate, returns whether to continue the script
        """
        axis_to_home = var_dict["Axis to home"]

        successful_go_home = False
        if axis_to_home == "All Axes":
            cont = self.retract_ua_warning()  # launch the retracting UA in the x direction warning box
            if not cont:
                return False
            successful_go_home = self.Motors.go_home(enable_ui=False)
            self.test_data.log_script(['', "Home all", f"X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}",
                                       f'Successful:{successful_go_home}'])
            if show_prompt and successful_go_home:
                self.user_info_signal.emit(f'Homing successful, X moved to {self.Motors.coords_mm[0]}, Theta moved to'
                                           f' {self.Motors.coords_mm[1]}')
            cont = self.cont_if_cont_clicked()
            if not cont:
                return False
        elif axis_to_home == 'X':
            cont = self.retract_ua_warning()  # launch the retracting UA in the x direction warning box
            if not cont:
                return False
            successful_go_home = self.Motors.go_home_1d("X", enable_ui=False)
            if successful_go_home and show_prompt:
                self.user_info_signal.emit(f'Homing successful, X moved to {self.Motors.coords_mm[0]}')
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return False
            self.test_data.log_script(["", f"Home  X", f"Home X", f'Successful:{successful_go_home}'])
        elif axis_to_home == "Theta":
            successful_go_home = self.Motors.go_home_1d("R", enable_ui=False)
            if successful_go_home and show_prompt:
                self.user_info_signal.emit(f'Homing successful, Theta moved to {self.Motors.coords_mm[1]}')
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return False
            self.test_data.log_script(["", f"Home Theta", f"Home Theta", f'Successful:{successful_go_home}'])
        else:
            self.test_data.log_script(['', f'Home {axis_to_home}', 'FAIL', 'axis unrecognized'])

        if not successful_go_home:
            cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail='Go home failed')
            return cont

        return True

    def retract_ua_warning(self) -> bool:
        """
        Warn the user that the UA is being retracted in x
        returns: a boolean indicating whether to continue the script
        """
        if self.config["Debugging"]["drain_before_retract"]:
            self.retracting_ua_warning_signal.emit()

            cont = self.cont_if_cont_clicked()
            if not cont:
                return False

        return True

    def move_system(self, var_dict, average_angle=True):
        """
        Move motors to the specified coordinates
        """
        move_type = var_dict["Move Type"]

        if "Go To".upper() in move_type.upper():
            x_pos = float(var_dict["X POS"])
            move_x = bool(var_dict["Move X"])
            theta_pos = float(var_dict["Theta POS"])
            move_theta = bool(var_dict["Move Theta"])
            axes = []
            coordinates = []
            if move_x:
                axes.append("X")
                coordinates.append(x_pos)
            if move_theta:
                axes.append("R")
                coordinates.append(theta_pos)
            self.Motors.go_to_position(axes, coordinates, enable_ui=False)
        else:
            self.element = self.element_str_to_int(var_dict["Element"])
            target = var_dict["Target"]
            element_x_coordinate = self.element_x_coordinates[self.element]
            element_r_coordinate = self.element_r_coordinates[self.element]

            # todo: make sure these names match theirs
            # todo: make sure these home coordinates work as expected
            if "Hydrophone" in target:
                self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -180], enable_ui=False)
            elif "RFB" in target:
                if average_angle:
                    self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, self.test_data.angle_average],
                                               enable_ui=False)
                else:
                    self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, element_r_coordinate,
                                                            self.test_data.angle_average],
                                               enable_ui=False)
            elif "Down" in target:
                self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -90], enable_ui=False)

            x_coord_str = "%.2f" % element_x_coordinate
            r_coord_str = "%.1f" % element_r_coordinate
            self.log(f"Moved to {self.element}, at coordinate x={x_coord_str}, r={r_coord_str}")

            self.test_data.log_script(["", "Move to element", f"moved to X={x_coord_str}, Th={r_coord_str}", ''])

    # todo: test
    def select_ua_channel(self, var_dict):
        """
        Activate the relay for and move to a specified element
        """
        if "Element" in var_dict.keys():
            self.element = self.element_str_to_int(var_dict["Element"])
        elif "Channel" in var_dict.keys():
            self.element = self.element_str_to_int(var_dict["Channel"])
        else:
            self.log(
                "No element defined in variable list for task 'select ua channel', "
                "previous self.element value preserved info")
            return

        self.IO_Board.activate_relay_channel(channel_number=self.element)

    def frequency_sweep(self, var_dict) -> bool:
        # todo: add test to results summary if include_test is True
        # todo: using this setting to decide where to put it (Low frequency or High frequency)

        if "Frequency Range" in var_dict.keys():
            range_str = "Frequency Range"
        else:
            range_str = "Frequency range"

        if 'high'.upper() in range_str.upper():
            frequency_range = FrequencyRange.high_frequency
        else:
            frequency_range = FrequencyRange.low_frequency
        start_freq_MHz = float(var_dict["Start frequency (MHz)"])
        end_freq_MHz = float(var_dict["End frequency (MHz)"])
        coarse_incr_MHz = float(var_dict["Coarse increment (MHz)"])
        fine_incr_MHz = float(var_dict["Fine increment (MHz)"])
        burst_count = int(var_dict["Burst count"])
        amplitude_mVpp = float(var_dict["Amplitude (mVpp)"])
        self.oscilloscope_channel = find_int(var_dict["Scope channel"])
        acquisition_type = var_dict["Acquisition type"]
        averages = int(var_dict["Averages"])
        data_storage = var_dict["Data storage"]
        # todo: implement these settings
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        peak_VSI_threshold = float(var_dict["Peak VSI threshold"])
        include_test = var_dict["Include test"]

        if storage_location == 'UA Results Directory' or data_directory == '':
            storage_location = ''
        else:
            storage_location = data_directory

        # configure function generator
        func_var_dict = dict()
        func_var_dict["Amplitude (mVpp)"] = amplitude_mVpp
        func_var_dict["Frequency (MHz)"] = start_freq_MHz
        func_var_dict["Mode"] = "Toneburst"
        func_var_dict["Enable output"] = True
        func_var_dict["#Cycles"] = burst_count  # Rename to burst_cycles in the future?
        func_var_dict["Set frequency options"] = "From config cluster"
        self.configure_function_generator(func_var_dict)

        if acquisition_type == "Single Waveform":
            self.Oscilloscope.set_averaging(1)
        else:
            self.Oscilloscope.set_averaging(averages)

        if self.config["Analysis"]["capture_rms_only"]:
            y_units_str = 'RMS voltage (V)'
        else:
            y_units_str = 'VSI (Voltage Squared Integral)'

        list_of_frequencies_MHz = list(np.arange(start_freq_MHz, end_freq_MHz, coarse_incr_MHz))
        coarse_freq_MHz_list, coarse_VSI_list, y_units_str, cont = self.run_frequency_sweep(list_of_frequencies_MHz,
                                                                                            data_storage,
                                                                                            storage_location,
                                                                                            y_units_str)

        if not cont:
            return False

        if 'Do not store'.upper() != data_storage.upper():
            self.__save_frequency_sweep(frequencies=coarse_freq_MHz_list, vsi_values=coarse_VSI_list,
                                        storage_location=storage_location, filename_stub='CoarseFrequencySweep',
                                        y_units_str=y_units_str)

        # Run fine VSI sweep
        max_coarse_VSI_index = max(range(len(coarse_VSI_list)), key=coarse_VSI_list.__getitem__)
        fine_start_freq_MHz = max(coarse_freq_MHz_list[max_coarse_VSI_index] - 1, 0)
        fine_stop_freq_MHz = min(coarse_freq_MHz_list[max_coarse_VSI_index] + 1, len(coarse_freq_MHz_list) - 1)
        fine_list_of_frequencies_MHz = list(np.arange(fine_start_freq_MHz, fine_stop_freq_MHz, fine_incr_MHz))
        fine_freq_MHz_list, fine_VSI_list, y_units_str, cont = self.run_frequency_sweep(fine_list_of_frequencies_MHz,
                                                                                        data_storage,
                                                                                        storage_location,
                                                                                        y_units_str)
        if not cont:
            return False

        # Update test results summary
        max_vsi = max(max(coarse_VSI_list), max(fine_VSI_list))

        if max_vsi in coarse_VSI_list:
            max_vsi_index = coarse_VSI_list.index(max_vsi)
            max_vsi_frequency = list_of_frequencies_MHz[max_vsi_index]
        else:
            max_vsi_index = fine_VSI_list.index(max_vsi)
            max_vsi_frequency = fine_list_of_frequencies_MHz[max_vsi_index]

        if include_test:
            self.test_data.update_results_summary_with_frequency_sweep(
                frequency_range=frequency_range,
                element=self.element,
                frequency_Hz=max_vsi_frequency,
                units_str=y_units_str,
                vsi=max_vsi
            )

        if 'Do not store'.upper() != data_storage.upper():
            self.__save_frequency_sweep(frequencies=fine_freq_MHz_list, vsi_values=fine_VSI_list,
                                        storage_location=storage_location, filename_stub='FineFrequencySweep',
                                        y_units_str=y_units_str)

        self.AWG.set_output(False)

    def run_frequency_sweep(self, list_of_frequencies_MHz,
                            data_storage, storage_location, y_units_str) -> Tuple[List[float], List[float], str, bool]:
        """
        Performs a sweep between two frequencies, capturing the oscilloscope waveform (or rms thereof)
        at each frequency. Saves each waveform to a file if specified
        Returns:
            a list of floats representing the frequencies in MHz
            a list of floats representing the VSI or the RMS voltage of the waveform
            a string specifying the units of the latter
            a boolean indicating whether to continue the script
        """
        list_of_VSIs = list()

        for i in range(len(list_of_frequencies_MHz)):
            # set frequency according to step (coarse/fine) and x increment
            self.AWG.set_frequency_hz(list_of_frequencies_MHz[i] * 1000000)
            # Find the vsi voltage at a given frequency

            if self.abort_immediately_variable:
                # Stop the current method and any parent methods that called it
                return [], [], "", False

            # populates times_s and voltages_v with set frequency
            if self.config["Analysis"]["capture_rms_only"]:
                vsi = self.Oscilloscope.get_rms()
            else:
                times_s, voltages_v = self.capture_scope(channel=self.oscilloscope_channel)
                if times_s == [] or voltages_v == []:
                    cont = self.sequence_pass_fail(action_type='Interrupt action',
                                                   error_detail='Oscilloscope capture failed')
                    if not cont:
                        return [], [], "", False

                if 'entire waveform'.upper() in data_storage.upper():
                    self.__save_hydrophone_waveform(axis='', waveform_number=i + 1, times_s=times_s,
                                                    voltages_v=voltages_v, storage_location=storage_location,
                                                    filename_stub="FrequencySweep", x_units_str='Time (s)',
                                                    y_units_str=y_units_str)

                vsi = self.find_vsi(times_s=times_s, voltages_v=voltages_v)

            list_of_VSIs.append(vsi)
            self.__refresh_profile_plot(list_of_frequencies_MHz[0:i], list_of_VSIs, "Frequency (Hz)")

        # frequencies will be on the x-axis
        return list_of_frequencies_MHz, list_of_VSIs, y_units_str, True

    def find_vsi(self, times_s, voltages_v):
        """
        Returns the voltage squared integral of an oscilloscope waveform
        """
        dx = 0
        for i in range(1, len(times_s)):
            dx = times_s[i] - times_s[i - 1]
            if dx != 0:
                break

        voltages_v_squared = np.square(voltages_v)

        if dx == 0:
            self.log(level='Error', message='Error in find_vsi. No delta x found, cannot integrate')
            return

        return integrate.simps(y=voltages_v_squared, dx=dx, axis=0)

    def measure_element_efficiency_rfb_multithreaded(self, var_dict):
        """Measure the efficiency of an element"""
        self.element = self.element_str_to_int(var_dict["Element"])
        self.set_tab_signal.emit(['RFB'])

        # Retrieve test parameters from the script and typecast them from strings
        # High frequency or Low frequency, convert to FrequencyRange enum
        frequency_range = FrequencyRange[var_dict["Frequency range"].lower().replace(" ", "_")]
        on_off_cycles = int(var_dict["RFB.#on/off cycles"])
        rfb_on_time = float(var_dict["RFB.On time (s)"])
        rfb_off_time = float(var_dict["RFB.Off time (s)"])
        threshold = float(var_dict["RFB.Threshold"])
        offset = float(var_dict["RFB.Offset"])
        set_frequency_options = var_dict["Set frequency options"]
        frequency_mhz = float(var_dict["Frequency (MHz)"])
        amplitude_mVpp = float(var_dict["Amplitude (mVpp)"])
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        target_position = var_dict["RFB target position"]
        target_angle = var_dict["RFB target angle"]
        efficiency_test = bool(var_dict["EfficiencyTest"])
        Pa_max = var_dict["Pa max (target, W)"]
        Pf_max = var_dict["Pf max (limit, W)"]
        reflection_limit = var_dict["Reflection limit (%)"]

        if storage_location == 'UA Results Directory' or data_directory == '':
            storage_location = ''
        else:
            storage_location = data_directory

        test_result = "DNF"
        # Show in the results summary that the test has begun by showing DNF
        self.test_data.set_pass_result(self.element, test_result)

        # Warns the user if the test time is too short to analyze properly
        settling_time = self.config["Analysis"]['settling_time_s']
        if rfb_on_time < settling_time * 2 or rfb_off_time < settling_time * 2:
            error_detail = "Warning: the on or off intervals are less than the sensor settling time specified in the " \
                           "config file. Either change it or load a different script"
            cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail=error_detail)

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
            self.set_tab_signal.emit(["RFB"])

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
        awg_var_dict["Frequency (MHz)"] = frequency_mhz
        awg_var_dict["Mode"] = "Continuous"
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
        # Begin multithreaded capture from the power meters and the balance and cycle the awg on and off
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
            self.log(f"test result for {self.element} has passed", self.system_info)
        else:
            self.log("self.rfb_data.get_pass_result() has returned an invalid result, aborting", self.warn)
            self.user_info_signal.emit("self.rfb_data.get_pass_result() has returned an invalid result, aborting")
            return self.abort_after_step()

        self.retry_clicked_variable = False

        if efficiency_test:
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

        self.file_saver.extract_file_data(rfb_logger=self.rfb_logger, rfb_data=self.rfb_data,
                                          system_info=self.system_info,
                                          element=self.element, frequency_mhz=frequency_mhz, threshold=threshold,
                                          offset=offset, frequency_range=frequency_range,
                                          storage_location=storage_location)

        self.test_data.log_script(["", "End", "", ""])

    def __begin_rfb_logger_thread(self, rfb_data: RFBData):
        self.rfb_logger = RFBDataLogger(rfb_data, self.Balance, self.Forward_Power_Meter, self.Reflected_Power_Meter,
                                        config=self.config)
        self.AWG.output_signal.connect(self.rfb_logger.update_awg_on)
        self.rfb_logger.finished.connect(self.rfb_logger.deleteLater)
        self.rfb_logger.start(priority=QThread.HighPriority)

    def __wrap_up_rfb_logger(self):
        """
        This method calls the balance's logger's quit function to close
        the logger thread. Sleeps to .1 seconds to prevent issues
        """
        self.rfb_logger.quit()
        t.sleep(0.1)

    def write_cal_data_to_ua_dialog(self, calibration_data):
        """
        calibration_data should be a 2d list: 1st col: cal data array, 2nd col: low freq, 3rd col: high freq
        , relays this data to the main window to open a GUI dialog to save calibration data.
        """
        self.show_write_cal_data_dialog_signal.emit(calibration_data)

    def wrap_up(self) -> None:
        """
        This method disconnects all devices from the program when called,
        and sets the stay alive flag to false.
        """
        for device in self.devices:
            device.wrap_up()
        self.stay_alive = False

    def log(self, message, level="info"):
        """
        Relays to the log_msg method in useful_methods.py, simply pass the message to be logged and
        a string representing the log level ("info," "debug," "error," or "warning")
        """
        from inspect import getframeinfo, stack
        log_msg(self, root_logger=root_logger, message=message, level=level,
                line_number=getframeinfo(stack()[1][0]).lineno)

    def refresh_rfb_tab(self) -> bool:
        """
        Helper function which retrieves data from the rfb_logger and tells the rfb tab to update
        returns a boolean indicating whether to continue the script
        """
        if self.abort_immediately_variable:
            # Stop the current method and any parent methods that called it
            return False

        rfb_cooldown_s = .05
        if t.time() - self.last_rfb_update_time > rfb_cooldown_s:
            self.rfb_data = self.rfb_logger.rfb_data
            self.update_rfb_tab_signal.emit()
            self.last_rfb_update_time = t.time()

        if self.app is not None:
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
                    "invalid setting for Sequence pass/fail : interrupt action in config file; "
                    "defaulting to prompt user",
                    self.warn)
                self.prompt_for_retry(error_detail)
        return True

    def prompt_for_retry(self, error_detail: str) -> bool:
        self.abort_clicked_variable = False
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

        self.retry_clicked_variable = True

        try:
            max_retries = self.config[k1]['Retries']
        except KeyError:
            self.log("no entry for Sequence pass/fail:Retries in config, defaulting to 5 retries", self.warn)
            max_retries = 5

        if self.retry_count < max_retries:
            self.retry_count = self.retry_count + 1
            return
        else:
            self.log(f"retry limit reached for {error_detail}, aborting script", self.warn)
            self.abort_after_step()

    def command_scan(self, command: str):
        """Activated by the scan setup tab when start scan is clicked. Extracts parameters and initiates a 1D scan"""
        # self.test_data.set_blank_values()
        self.enable_ui_signal.emit(False)
        self.set_tab_signal.emit(["Scan", "1D Scan"])
        self.file_saver = FileSaver(self.config)
        self.test_data.serial_number = "Unknown"  # todo
        self.file_saver.create_folders(self.test_data)
        command_ray = command.split("_")
        axis = str(command_ray[1])
        pts = int(command_ray[2])
        increment = float(command_ray[3])
        ref_pos = command_ray[4]

        element_x_coordinate = self.element_x_coordinates[self.element]
        element_r_coordinate = self.element_r_coordinates[self.element]
        if "Hydrophone" in ref_pos:
            self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -180], enable_ui=False)
            if axis == 'X':
                ref_pos = element_x_coordinate
            else:
                ref_pos = -180
        elif "RFB" in ref_pos:
            self.Motors.go_to_position(['X', 'R'], [element_x_coordinate, element_r_coordinate], enable_ui=False)
            if axis == 'X':
                ref_pos = element_x_coordinate
            else:
                ref_pos = element_r_coordinate
        elif "Down" in ref_pos:
            self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -90], enable_ui=False)
            if axis == 'X':
                ref_pos = element_x_coordinate
            else:
                ref_pos = -90

        end_pos = command_ray[5]
        go_to_peak = 'peak'.upper() in end_pos.upper()
        comments = command_ray[6]
        filename_stub = command_ray[7]
        data_directory = command_ray[8]

        if data_directory == "UA Results Directory":
            data_directory = ""

        acquisition_type = command_ray[9]
        source_channel = self.channel_str_to_int(command_ray[10])
        averages = int(command_ray[11])
        element = int(command_ray[12])
        data_storage = command_ray[13]
        serial_number = command_ray[14]

        # self.test_data.set_blank_values()
        self.enable_ui_signal.emit(False)
        self.set_tab_signal.emit(["Scan", "1D Scan"])
        self.test_data.serial_number = str(serial_number)
        self.file_saver = FileSaver(self.config)
        self.file_saver.create_folders(self.test_data)
        self.test_data.test_comment = comments

        self.scan_axis(element, axis, pts, increment, ref_pos, data_storage, go_to_peak,
                       data_directory, False, source_channel, acquisition_type, averages, filename_stub)
        self.enable_ui_signal.emit(True)


class AbortException(Exception):
    pass


class RetryException(Exception):
    pass
