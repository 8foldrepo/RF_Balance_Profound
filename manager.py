import distutils.util
import logging
import re
import sys
import time as t
import traceback
from collections import OrderedDict
from statistics import mean
from typing import List, Tuple, Union
import numpy as np
import pyvisa
from PyQt5 import QtCore
from PyQt5.QtCore import QMutex, QThread, QWaitCondition, pyqtSlot
from PyQt5.QtWidgets import QApplication, QComboBox
from numpy import ndarray
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
from Utilities.test_data_helper_methods import generate_calibration_data
from Utilities.useful_methods import log_msg, get_element_distances, find_int
from data_structures.rfb_data import RFBData
from data_structures.test_data import TestData

from data_structures.variable_containers import FileMetadata, SerialNumbers, WaterLevel, FrequencyRange
from definitions import ROOT_DIR

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger("wtf_log")
with open(ROOT_DIR + "\logs\wtf.log", 'w') as f:
    pass
file_handler = logging.FileHandler(ROOT_DIR + "\logs\wtf.log", mode="w")
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

    # These lists will store all information about the script being run. Looped steps appear multiple times with their
    # Element numbers updated accordingly.
    task_names: Union[List[str], None]  # a list of strings containing the task names (and repetition number)
    # list containing the task number of each script action
    task_execution_order: Union[List[Union[List[int], int]], None]
    task_arguments: Union[List[dict], None]  # a list containing the arguments for each script action

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
    system_info_signal = QtCore.pyqtSignal(SerialNumbers)

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
    set_abort_buttons_enabled_signal = QtCore.pyqtSignal(bool)

    assumed_element_x_coords: List[float]
    assumed_element_r_coords: List[float]
    measured_element_x_coords: List[Union[float, None]]
    measured_element_r_coords: List[Union[float, None]]

    def __init__(self, system_info, parent, config: dict, access_level='Operator'):
        """Initializes various critical variables for this class, as well as setting thread locking mechanisms."""
        super().__init__(parent=parent)
        self.question_box_finished = None
        self.script_has_description = False
        self.script_description = None
        self.access_level = access_level
        self.error_message = None
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

        # Get the currently running application (force UI updates using self.app.processEvents)
        self.app = QApplication.instance()
        self.test_data = TestData()
        self.file_saver = FileSaver(config=self.config)

        # Populate variables for assumed and measured element positions. If they have not been measured yet the
        # measured list will contain assumed values
        self.assumed_element_x_coords = get_element_distances(
            element_1_index=self.config["WTF_PositionParameters"]["X-Element1"],
            element_pitch=self.config["WTF_PositionParameters"]["X-Element pitch (mm)"],
        )
        self.measured_element_x_coords = list(self.assumed_element_x_coords)
        # put a none at position zero because there is no element zero
        self.assumed_element_r_coords = [None]
        # fill in default theta home coordinates
        for _ in range(10):
            self.assumed_element_r_coords.append(self.config["WTF_PositionParameters"]["ThetaHomeCoord"])
        self.measured_element_r_coords = [None] * 11

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
        self.enable_ui_signal.emit(True)
        self.set_abort_buttons_enabled_signal.emit(False)  # disable abort buttons/fields
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
            from Hardware.galil_motor_controller import GalilMotorController
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
                self.user_prompt_signal.emit(f"{device.device_key} Could not connect\n\n{feedback}", True)
                try:
                    self.wait_for_cont()
                except RetryException:
                    i -= 1
                except AbortException:
                    self.app.exit(-1)
            i += 1

        if self.Oscilloscope.connected:
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
        info = SerialNumbers()
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
                    self.set_abort_buttons_enabled_signal.emit(True)  # enable abort buttons
                    if self.task_names is None:
                        self.abort_after_step()
                        self.enable_ui_signal.emit(True)
                    else:
                        self.advance_script()
                else:
                    self.update_sensors()

            # Show script complete dialog whenever a script finishes
            if not self.currently_scripting and self.was_scripting:
                self.enable_ui_signal.emit(True)
                self.set_abort_buttons_enabled_signal.emit(False)  # disable abort buttons
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
        self.enable_ui_signal.emit(False)
        self.set_abort_buttons_enabled_signal.emit(True)  # enables main window abort buttons during test
        self.was_scripting = True
        self.abort_immediately_variable = False

    def update_sensors(self) -> None:
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

    def capture_scope(self, channel: int = 1, plot: bool = True) -> Tuple[list, list]:
        """
        captures time and voltage data from the oscilloscope hardware, stores them into two separate lists and returns
        them to the calling function. Defaults to channel 1 on the oscilloscope and sets the plot flag to true

        :param channel: The channel you want the oscilloscope to capture from
        :param plot: Whether you want the readings to be plotted
        :return: time and voltage lists, if error encountered, lists will be empty
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

    def plot_scope(self, time: List[float], voltage: List[float]) -> None:
        """
        takes the time and voltage data (lists) from the oscilloscope and sends a signal to main window to plot them

        :param time: the points of the x-axis (time) that were taken during capture to be plotted
        :param voltage: the y-values (voltage) of the x-axis points (time) that were taken during capture to be plotted
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

        # compares local class average value with one stored in oscilloscope class
        if self.oscilloscope_averages != self.Oscilloscope.averages:
            # if not matching, update oscilloscope's class variable with manager's variable to synchronize
            self.Oscilloscope.set_averaging(self.oscilloscope_averages)

        # Only capture if the scan tab is selected
        if not self.parent.scan_tab_widget.plot_ready:
            return
        if self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex()) != 'Scan':
            return

        time, voltage = self.capture_scope(channel=self.oscilloscope_channel)

        self.plot_scope(time, voltage)
        self.start_time = t.time()

    @pyqtSlot(str)
    def load_script(self, path: str) -> None:
        """
        takes the script file and parses the info within it into various lists and dictionaries so the program can
        run the script, requires a path argument to the script

        :param path: Windows directory path of the script (.WTF) file
        """
        self.abort_immediately(log=False)  # we don't want the save prompt for this use of abort

        # Send name of script to UI
        split_path = path.split("/")  # splits the directory into a list with the '/' as a delimiter
        self.test_data.script_name = split_path[len(split_path) - 1]  # file name is in the last position of the list
        self.script_name_signal.emit(self.test_data.script_name)  # send script name to main window thread

        tasks = []  # the upper layer of our task list
        self.task_execution_order = []
        element_names_for_loop = []  # contains the list of elements subject to task in loops, empties for the next loop
        task_number_for_loop = []  # contains the task numbers contained in the loop, empties for the next loop
        loop_index_tracker = 0  # keeps track of the order of loops
        adding_elements_to_loop = False
        building_loop = False
        task_variables = OrderedDict()  # the list of variables for the individual task
        task_number = -2  # keeps track of the task number for indexing
        self.script_has_description = False
        self.set_tab_signal.emit(["Edit Script"])
        script_file = open(path, "r")  # open in reading more, we're not altering anything
        for current_line in script_file:
            ray = current_line.split(" = ")

            # Populate script metadata to UI using signals
            # See if the first element in the ray matches one of the top level metadata attributes
            # if so, emit the signal and pass the value to the main window class
            if "# OF TASKS" in ray[0].upper():
                self.num_tasks_signal.emit(int(ray[1].replace('"', "")))
            elif "CREATEDON" in ray[0].upper():
                self.created_on_signal.emit(ray[1].replace('"', ""))
            if "CREATEDBY" in ray[0].upper():
                self.created_by_signal.emit(ray[1].replace('"', ""))
            elif "DESCRIPTION" in ray[0].upper():
                self.script_has_description = True
                self.script_description = ray[1].replace('"', "")
                self.description_signal.emit(self.script_description)

            if current_line == '\n':
                if task_variables:  # prevents adding empty variable lists to main tasks list
                    tasks.append(OrderedDict(task_variables))
                    task_variables.clear()  # empties out variable list for task since we're ready to move onto next set
                if adding_elements_to_loop:  # if we're done with a 'Loop over elements' task block
                    adding_elements_to_loop = False
                continue
            elif '[' in current_line:  # if the line we're on is a task line: [TaskX]
                task_number += 1
                if "Task" in current_line and not building_loop:
                    self.task_execution_order.append(task_number)
            else:  # if the line we're on is neither a blank line nor a task header line
                attribute_name = ray[0].strip()
                value = ray[1].strip().replace('"', "")
                # if we're in a loop, the element value should be 'current'
                if attribute_name == 'Element' and value != 'Current' and building_loop:
                    self.question_box_finished = False
                    self.yes_clicked_variable = False
                    self.no_clicked_variable = False
                    # offer the user a chance to fix it
                    self.user_question_signal.emit(
                        f"The script has a static 'Element' value for task '{task_variables['Task type']}' when it "
                        f"should be 'Current' since it's in a loop. Temporarily change it to 'Current'?")
                    # wait until the user makes a decision or inappropriately closes the dialog
                    cont = self.cont_if_answer_clicked()
                    if cont:
                        if self.yes_clicked_variable:
                            # correct the previously incorrect value (local data only, does not change file)
                            value = 'Current'
                            task_variables[attribute_name] = value
                        else:
                            task_variables[attribute_name] = value
                else:  # We're not in loop, don't need to check if "Element" value is "Current"
                    task_variables[attribute_name] = value

                if "Loop over elements" in value:
                    building_loop = True
                    adding_elements_to_loop = True
                if adding_elements_to_loop and "Element" in attribute_name:
                    element_name_to_split = attribute_name.split(" ")
                    # retrieve the second word of the left side, that's the element name
                    element_name = element_name_to_split[1]
                    if value.upper() == 'TRUE':
                        element_names_for_loop.append(int(element_name))  # add element to the loop

                if "End loop" in value:
                    building_loop = False

                    # in our loops list, append a tuple where the first value represents the elements to be subject
                    # to the loop and the second value is the task numbers to be applied to the targeted elements
                    self.loops.append(list([list(element_names_for_loop), list(task_number_for_loop)]))

                    element_names_for_loop.clear()  # clear these lists in case we run across another loop building task
                    task_number_for_loop.clear()
                    self.task_execution_order.pop()  # end loop isn't a task we want in our task execution order

                    # appends a 3 item list in taskExecOrder, the first part being the task number
                    # the second item being the element number and the third is the loop number
                    # the loops list is not cleared for each loop, so only take data from the last entry
                    for i in range(len(self.loops[len(self.loops) - 1][0])):
                        for j in range(len(self.loops[len(self.loops) - 1][1])):
                            self.task_execution_order.append(
                                [self.loops[len(self.loops) - 1][1][j], self.loops[len(self.loops) - 1][0][i],
                                 loop_index_tracker])
                    loop_index_tracker += 1  # increment the loop index since we're done with a loop

                # prevents adding duplicate task numbers to loop list and making sure we're not adding the "add
                # elements to loop" to our task numbers for the loop
                if (building_loop and not adding_elements_to_loop) and (task_number not in task_number_for_loop):
                    task_number_for_loop.append(task_number)
        script_file.close()

        if task_variables:  # if task variable list isn't empty (which happens with empty scripts)
            tasks.append(OrderedDict(task_variables))  # append it to the over-arching tasks list
            task_variables.clear()  # empties out variable list, now we can add another script if needed

        for i in range(len(self.task_execution_order)):
            if not isinstance(self.task_execution_order[i], list):  # if the task step does not have element
                self.task_execution_order[i] = [self.task_execution_order[i], None]  # set the element to "None"

        self.task_names = list()
        for i in range(len(self.task_execution_order)):
            # INFO: tasks and task_execution_order are offset by 1
            if "Task type" in tasks[self.task_execution_order[i][0] + 1].keys():  # prevent key index exception
                # copy task name value from list and put it into task names list
                self.task_names.append(tasks[self.task_execution_order[i][0] + 1]["Task type"])

        self.task_arguments = list()

        for i in range(len(self.task_execution_order)):
            # INFO: task_arguments and tasks lists are offset by 1
            # copy all task variables from upper-level tasks list to more specific task_arguments list
            self.task_arguments.append(tasks[self.task_execution_order[i][0] + 1])

        if not self.script_has_description:
            self.script_description = ''

        if self.script_description is None or self.script_description == '':
            self.script_has_description = False
            self.description_signal.emit('')
        else:
            self.description_signal.emit(self.script_description)

        # send the over-arching and all-encompassing task list to the main window for visualization
        self.script_info_signal.emit(tasks)
        self.num_tasks_signal.emit(len(self.task_names))  # as well as the number of tasks in the script

        # checks if there are no tasks, with and without header
        if len(tasks) == 0 or (len(tasks) == 1 and '# of Tasks' in tasks[0]):
            self.user_info_signal.emit(
                "You cannot run a script that has no tasks, please select a script that has tasks.")
            self.abort_immediately()

            # notify the main window no script has been loaded, so it may disable/enable appropriate buttons
            self.no_script_loaded_signal.emit()
            self.set_tab_signal.emit(["Welcome"])
        else:  # if the script is not empty
            self.set_tab_signal.emit(["Edit Script"])

    @pyqtSlot()
    def advance_script(self) -> None:
        """Updates script step and executes the next step if applicable, and implements abort, continue, and retry"""
        try:
            if self.task_names is None:  # we need a task name, otherwise the script cannot continue
                self.abort_immediately()
                self.enable_ui_signal.emit(True)  # re-enable various buttons in the main window
                return

            if self.retry_clicked_variable is True:
                self.step_index -= 1  # retry the step via decrementing the step index

                # sets the retry variable to false so the retry function may happen again
                self.retry_clicked_variable = False

            self.step_index += 1  # advance to the next step if the previous has been completed

            if self.step_index > len(self.task_names):  # if scripting is done
                self.currently_scripting = False
                self.set_abort_buttons_enabled_signal.emit(False)  # Disable abort buttons in main window
                return

            # below: if a script with valid, non-empty contents has been loaded, and we're in the middle of script
            # advancement
            if self.task_arguments is not None and self.task_names is not None and self.task_execution_order is not \
                    None and 0 <= self.step_index < len(self.task_names):
                inside_iteration = False  # we don't know if we're inside an iteration yet
                iteration_number = None

                # elements that are a part of a loop will have a third sub element notating which loop it's from
                if len(self.task_execution_order[self.step_index]) == 3:
                    self.test_data.log_script(
                        [f"Iteration {self.task_execution_order[self.step_index][1]} of "
                         f"{len(self.loops[self.task_execution_order[self.step_index][2]][0])}", "", "", "", ]
                    )  # mark iteration count for loop in log file
                    inside_iteration = True  # we are inside a loop, enable this flag

                    # take the iteration number from the task_exec_order list
                    iteration_number = self.task_execution_order[self.step_index][1]

                self.run_script_step()  # call helper method to execute the current task
                if inside_iteration:  # if we're inside a loop iteration
                    self.test_data.log_script([f"Iteration {iteration_number} complete", '', '', ''])

            if not self.currently_scripting:
                self.enable_ui_signal.emit(True)  # toggle appropriate buttons in main window and its tabs
                self.set_abort_buttons_enabled_signal.emit(False)  # disable abort buttons

        # Catch all errors while advancing the script and handle them by showing the user a dialog with the traceback
        except Exception:
            self.abort_immediately()
            self.error_message = traceback.format_exc()  # load the traceback into a string
            self.log(message=traceback.format_exc(), level="error")  # log the traceback into the logger with red text
            self.critical_error_flag = True
            self.set_tab_signal.emit(["Results"])

    def run_script_step(self) -> None:
        """
        Helper method for advance_script(); Executes script step with given step index in taskNames/taskArgs
        """

        # if task entry is malformed
        if self.task_arguments is None or self.task_names is None or self.task_execution_order is None:
            self.abort_after_step()
            self.enable_ui_signal.emit(True)  # re-enable various main window buttons since we are no longer scripting
            return

        task_name = self.task_names[self.step_index]
        task_arguments = self.task_arguments[self.step_index]

        # send task number & index to the main window
        self.task_number_signal.emit(self.task_execution_order[self.step_index][0])
        self.task_index_signal.emit(self.step_index)

        # if the element in the list isn't None
        if self.task_execution_order[self.step_index][1] is not None:
            # set the element to be operated on to the one in self.taskExecOrder
            task_arguments['Element'] = self.task_execution_order[self.step_index][1]

        # switch case for various task types, launches appropriate method and passes arguments
        if "MEASURE ELEMENT EFFICIENCY (RFB)" in task_name.upper():
            self.measure_element_efficiency_rfb(task_arguments)
        elif "PRE-TEST INITIALISATION" in task_name.upper():  # all checks will be case-insensitive
            self.pretest_initialization()
        elif "FIND ELEMENT" in task_name.upper():
            self.find_element(task_arguments)
        elif "SAVE RESULTS" in task_name.upper():
            self.save_results(task_arguments)
        elif "PROMPT USER FOR ACTION" in task_name.upper():
            self.prompt_user_for_action(task_arguments)
        elif "HOME SYSTEM" in task_name.upper():
            self.home_system(task_arguments)
        elif "OSCILLOSCOPE CHANNELS" in task_name.upper():
            self.configure_oscilloscope_channels(task_arguments)
        elif "OSCILLOSCOPE TIMEBASE" in task_name.upper():
            self.configure_oscilloscope_timebase(task_arguments)
        elif "FUNCTION GENERATOR" in task_name.upper():
            self.configure_function_generator(task_arguments)
        elif "AUTOSET TIMEBASE" in task_name.upper():
            self.autoset_timebase()
        elif "MOVE SYSTEM" in task_name.upper():
            self.move_system(task_arguments)
        elif "SELECT CHANNEL" in task_name.upper() or "SELECT UA CHANNEL" in task_name.upper():
            self.select_ua_channel(task_arguments)
        elif 'FREQUENCY SWEEP' in task_name.upper():
            self.frequency_sweep(task_arguments)
        else:
            self.log(f"{task_name} is not a valid task task_name in the script, aborting immediately", "error")
            self.critical_error_flag = True
            # string will be shown to user in the script_complete method
            self.error_message = f"{task_name} is not a valid task task_name in the script, aborting immediately"
            self.abort_immediately()

        self.task_index_signal.emit(self.step_index + 1)  # inform main window step is done

        # below helps explain loop and list logic
        # if len(self.taskExecOrder[self.step_index]) == 3:
        #     print(f"looped element {self.taskExecOrder[self.step_index][0]} is in iteration {self.taskExecOrder
        #     [self.step_index][1]} from loop {self.loops[self.taskExecOrder[self.step_index][2]]}")

    @pyqtSlot()
    def abort_after_step(self, log: bool = True) -> None:
        """
        Aborts script when current step is done running

        :param log: whether to log the abort after step event to the console
        """

        if self.retry_clicked_variable:
            return
        if log:
            self.log(level='warning', message="Aborting script after step")
        # Reset script control variables
        self.currently_scripting = False
        self.enable_ui_signal.emit(True)
        self.set_abort_buttons_enabled_signal.emit(False)  # disable abort buttons
        self.step_index = -1
        self.abort_immediately_variable = False
        self.task_number_signal.emit(0)  # tell the main window we're in the 0th task number/index
        self.task_index_signal.emit(0)

    @pyqtSlot()
    def abort_immediately(self, log: bool = True) -> None:
        """
        Aborts script as soon as the current step checks abort_immediately var and returns or the step finishes.
        Any long-running step should check abort_immediately_var frequently and return false if the var is true

        :param log: Whether to signify an abort immediately event took place in the console
        """
        if log:
            self.log(level='warning', message="Aborting script")
        # Reset script control variables
        self.Motors.stop_motion()
        self.currently_scripting = False
        self.enable_ui_signal.emit(True)
        self.set_abort_buttons_enabled_signal.emit(False)  # disable abort buttons for no scripting
        self.step_index = -1
        self.abort_immediately_variable = True
        self.task_number_signal.emit(0)
        self.task_index_signal.emit(0)

    def cont_if_cont_clicked(self) -> bool:
        """
        Waits and returns true if the user presses continue. Returns false if the user clicks abort or retry.
        Call this method after showing a dialog, and return if the result is false.

        :return: True if user clicked continue, false otherwise
        """
        try:  # abort and retry are handled as exceptions
            self.wait_for_cont()  # calls helper method to wait for user's input
            return True  # return true if neither abort nor retry are clicked (handled below)
        except AbortException:  # if the user clicked the abort button or closed the prompt inappropriately
            self.test_data.log_script(["", "User prompt", "FAIL", "Closed by user"])
            if self.abort_immediately_variable:
                self.abort_immediately()
                return False
            else:
                self.abort_after_step()
                return False
        except RetryException:  # if the user has clicked retry
            self.test_data.log_script(["", "User prompt", "Retry step", ""])
            self.log(level='info', message="Retrying step")
            self.retry_clicked_variable = True
            return False

    def wait_for_cont(self) -> bool:
        """
        Sets continue variable to False and waits for it to be true, raising exceptions if the user
        wants to abort or retry. Always handle these exceptions.

        :return: True if user clicked continue, false if otherwise
        """
        self.continue_clicked_variable = False  # initialize all decision flags to false
        self.retry_clicked_variable = False
        self.abort_clicked_variable = False

        while not self.continue_clicked_variable:
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

    def cont_if_answer_clicked(self) -> bool:
        """
        Waits and returns true if the user presses continue. Returns false if the user clicks close window button.
        Call this method after showing a dialog, and return if the result is false.

        :return: True if user clicked an answer, false if user aborted
        """
        try:
            self.wait_for_answer()
            return True
        except AbortException:  # if user inappropriately closed question box
            self.test_data.log_script(["", "User prompt", "FAIL", "Closed by user"])  # log the event
            if self.abort_immediately_variable:
                self.abort_immediately()
                return False
            else:
                self.abort_after_step()
                return False

    def wait_for_answer(self) -> bool:
        """
        Sets answer variables to false and waits for user to make selection

        :return: True if user clicked yes, false if clicked no
        """
        while not self.question_box_finished:
            if self.yes_clicked_variable:
                return True
            if self.no_clicked_variable:
                return False

    @pyqtSlot()
    def continue_clicked(self) -> None:
        """Adjusts the response flags to reflect continue"""
        self.continue_clicked_variable = True
        self.abort_clicked_variable = False
        self.abort_immediately_variable = False

    @pyqtSlot()
    def retry_clicked(self) -> None:
        """sets retry_clicked_variable to true"""
        self.retry_clicked_variable = True

    @pyqtSlot()
    def abort_clicked(self) -> None:
        """sets abort_clicked_variable to true"""
        self.abort_clicked_variable = True

    @pyqtSlot()
    def yes_clicked(self) -> None:
        """adjusts answer flags to 'yes'"""
        self.yes_clicked_variable = True
        self.no_clicked_variable = False
        self.question_box_finished = True

    @pyqtSlot()
    def no_clicked(self) -> None:
        """adjusts answer flags to 'no'"""
        self.no_clicked_variable = True
        self.yes_clicked_variable = False
        self.question_box_finished = True

    def script_complete(self, finished: bool = False) -> bool:
        """
        Run when the script finishes its final step. Shows a dialog with pass/fail results and enables the UI

        :param finished: Whether the overall device passed or failed the efficiency test given the pass/fail constraints
        :returns: true if method reaches the end successfully
        """
        # Fetch pass list and description list from testdata
        pass_list = list([None] * 11)
        description_list = list([None] * 11)

        if finished:
            device_result = 'PASS'
        else:
            device_result = 'DNF'

        for i in range(10):  # for all 10 UA actuators
            pass_list[i] = self.test_data.results_summary[i][15]
            if pass_list[i].upper() == 'FAIL':  # if any of the actuators failed
                device_result = 'FAIL'  # the whole device fails
            description_list[i] = self.test_data.results_summary[i][16]

        # Add ua write result to output
        if self.test_data.skip_write_to_ua or self.test_data.write_result is None:  # if user opted not to write to UA
            pass_list[10] = "N/A"  # write N/A instead of fail
        elif self.test_data.write_result:
            pass_list[10] = "PASS"
        else:
            pass_list[10] = "FAIL"

        self.test_data.set_pass_result(11, device_result)  # add the overall device result to the results_summary

        # give main window the pass list and description list, signifying test is finished
        self.script_complete_signal.emit(pass_list, description_list)
        if self.critical_error_flag:
            self.critical_error_signal.emit(self.error_message)
        self.critical_error_flag = False  # set and the next two variables back to false so if user repeats test,
        # same mechanism will work
        self.error_message = ""
        self.currently_scripting = False
        self.enable_ui_signal.emit(True)
        self.set_abort_buttons_enabled_signal.emit(False)  # not scripting, disable abort buttons
        self.enable_ui_signal.emit(True)

        self.test_data.log_script(["Script complete", "", "", ""])
        if self.config['Debugging']['print_detailed_verbose']:
            self.log(message=repr(self.test_data), level='debug')
        self.set_tab_signal.emit(["Results"])  # change the main window tab to the results tab automatically
        return True

    def pretest_initialization(self) -> bool:
        """
        Home the UA, perform hardware checks, and prompt the user until they pass,
        takes in a variable dict as a parameter

        :returns: boolean representing if the method finished successfully
        """

        # add first 4 lines of script log

        # this is the first line
        self.test_data.log_script([f"{self.test_data.serial_number}-{self.test_data.test_date_time}", '', '', ''])
        self.test_data.log_script(["Running script: ", self.test_data.script_name, '', '', ''])
        self.test_data.log_script(["Pretest_initialization", '', '', ''])
        self.test_data.log_script(['', "Prompt username+UA serial", 'OK', ''])

        # Check if WTF-IB is connected and add that to the script log
        if self.test_data.serial_number != "":  # if the serial number of the UA is not empty
            self.test_data.log_script(["", "Get UA Serial", "Connected", "OK"])
        else:
            self.test_data.log_script(["", "Get UA Serial", "Connected", "FAIL"])

            # Give user opportunity to retry or continue (if access level grants it)
            cont = self.sequence_pass_fail(error_detail="Get UA Serial in pretest initialisation failed",
                                           action_type="Interrupt action")
            if not cont:  # if the user does not want to continue over this issue
                return False
            self.retry_clicked_variable = False  # set this back to false in case another interrupt issue arises

        # Show dialogs until pump is on and the water sensor reads level
        while True:
            if self.abort_immediately_variable:
                return False
            if not self.IO_Board.get_ua_pump_reading():  # if the pump is not running
                self.user_prompt_pump_not_running_signal.emit(pump_status)  # launch dialog box signifying this issue
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return False
            else:  # if we can get a reading from the UA
                self.test_data.log_script(["", "Check/prompt UA Pump", "OK", ""])  # mark it in the log file
                break

        # todo: have ua inserted to certain x position like in the ScriptResults.log

        # attempt to home all axes with user prompt
        home_successful = self.home_system(var_dict={"Axis to home": "All Axes"}, show_prompt=True)

        if home_successful:
            self.test_data.log_script(['', "Home all", f"OK; X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}", ''])
        else:
            self.test_data.log_script(['', "Home all", f"FAIL; X={self.Motors.coords_mm[0]}; "
                                                       f"Theta={self.Motors.coords_mm[1]}", ''])
            cont = self.sequence_pass_fail(action_type='Interrupt action',
                                           error_detail='Home all has failed in pretest initialisation')
            if not cont:
                return False
            if self.abort_immediately_variable:
                return False

        # show where the UA was inserted to in the log file
        self.test_data.log_script(['', 'Insert UA', f"UA Inserted to X={self.Motors.coords_mm[0]}"])

        if self.thermocouple.connected:
            self.test_data.log_script(["", "CheckThermocouple", "OK", ""])  # log it in the log file
        else:
            self.test_data.log_script(["", "CheckThermocouple", "FAIL", ""])  # log it in the log file

            # give user a chance to retry, abort, or continue
            cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail='Thermocouple failed check')
            if not cont:
                return False

        # Configure function generator
        func_var_dict = dict()
        try:
            # take AWG amplitude from config file
            func_var_dict["Amplitude (mVpp)"] = self.config[self.AWG.device_key]["amplitude_V"] * 1000
        except KeyError:
            self.log(level='warning',
                     message='"amplitude_V" not found for the function generator in the config file, defaulting to '
                             '200 mV')
            func_var_dict["Amplitude (mVpp)"] = 200
        func_var_dict["Frequency (MHz)"] = self.test_data.low_frequency_MHz
        func_var_dict["Mode"] = "Toneburst"
        func_var_dict["Enable output"] = True
        try:
            func_var_dict["#Cycles"] = self.config[self.AWG.device_key]['burst_cycles']
        except IndexError:
            self.log(level='warning',
                     message='"burst_cycles" not found for function generator in config file, defaulting to 4000')
            func_var_dict["#Cycles"] = 4000
        func_var_dict["Set frequency options"] = "From config cluster"
        self.configure_function_generator(func_var_dict)  # send the above values to the AWG to apply settings

        if self.abort_immediately_variable:
            return False

        self.user_prompt_signal.emit("Please ensure that the power amplifier is on", False)  # task can't be automated
        cont = self.cont_if_cont_clicked()
        if not cont:
            return False

        self.test_data.log_script(["", "Prompt PowerAmp", "OK", ""])

        if self.file_saver.directories_created:  # check if the saving directories were successfully created
            self.test_data.log_script(["", "CreateDataDirectories", "OK", ""])  # write result to the log script
        else:
            self.test_data.log_script(["", "CreateDataDirectories", f"FAIL", ""])

        try:  # checking the self.log() functionality
            self.log("Checking ability to log")
            self.test_data.log_script(["", "Create h/w log", "OK", ""])
        except Exception as e:
            self.test_data.log_script(["", "Create h/w log", f"FAIL {e}", ""])

        self.test_data.log_script(["", "Initialize results FGV", "OK", ""])
        self.test_data.log_script(["", "duplicate main script", "OK", ""])

        if self.abort_immediately_variable:
            return False

        successful = self.Motors.go_to_position(['X'],[self.config['WTF_PositionParameters']['X-TankInsertionPoint']])
        if not successful:
            self.log(level='Error', message='Failed to insert UA in pretest initialization')

        water_level = self.IO_Board.get_water_level()

        if water_level == WaterLevel.below_level or water_level == WaterLevel.level:
            self.user_prompt_signal_water_too_low_signal.emit()
            cont = self.cont_if_cont_clicked()
            if not cont:
                return False
            self.IO_Board.bring_tank_to_level()  # if user clicked continue, send the fill tank command
        elif water_level == WaterLevel.above_level:
            self.user_prompt_signal_water_too_high_signal.emit()
            cont = self.cont_if_cont_clicked()
            if not cont:
                return False
            self.IO_Board.bring_tank_to_level()
        else:
            self.test_data.log_script(["", "Check/prompt water level", "OK", ""])

        return True

    @pyqtSlot(TestData, bool)
    def test_metadata_slot(self, test_data: TestData, run_script: bool = False) -> None:
        """
        Receive test metadata from the MainWindow, and begin the script.

        :param test_data: connects PretestDialog's user-inputted test_data and manager's test_data variables
        :param run_script: if true, calls the run_script helper method at the end of this method
        """

        # reset test data to default values
        self.test_data.set_blank_values()

        # reset their representation in the UI
        self.test_data.show_results_summary.emit(self.test_data.results_summary)
        self.test_data.show_script_log.emit(self.test_data.script_log)

        # synchronize manager's test_data variable w/ PretestDialog's
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
                                         "Copy default.yaml if local.yaml does not exist. Or re-run this application "
                                         "with administrator privileges.", False)
            return self.abort_after_step()

        if run_script:
            self.run_script()

    def element_str_to_int(self, element_str: str) -> int:
        """
        Looks for an integer in the string, otherwise returns the current element

        :param element_str: the element string to extract the number from
        :returns: the element number extracted from the string; previous element number of attribute error raised
        """
        try:
            self.element = find_int(element_str)
        except AttributeError:
            self.log(f"Element number not given, using previous element: {self.element}")
        return self.element

    def channel_str_to_int(self, channel_str: str) -> int:
        """
        Looks for an integer in the string, otherwise returns the current channel

        :param channel_str: string representation of the oscilloscope channel
        :returns: integer representation of the oscilloscope channel
        """
        try:
            self.element = int(re.search(r"\d+", str(channel_str)).group())
        except AttributeError:
            self.log(f"Element number not given, using previous element: {self.oscilloscope_channel}")
        return self.element

    def find_element(self, var_dict: dict) -> bool:
        """
        Find UA element with given number by scanning for a maximum VSI or RMS
        returns a boolean indicating whether to continue the script

        :param var_dict: dictionary of arguments pertaining to the find element task
        :returns: boolean value of whether method ran successfully or not
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
        if "Autoset Timebase" in var_dict.keys():
            autoset_timebase = var_dict["Autoset Timebase"]
        else:
            autoset_timebase = var_dict["Auto set timebase"]
        capture_cycles = float(var_dict["#Cycles.Capture"])
        delay_cycles = float(var_dict["#Cycles.Delay"])

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

        assumed_x_coordinate = self.assumed_element_x_coords[self.element]
        assumed_r_coordinate = self.assumed_element_r_coords[self.element]
        self.log(
            f"Finding element {self.element}, near coordinate x = {assumed_x_coordinate}, r = {assumed_r_coordinate}")

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
            self.abort_after_step()
            return False
        self.configure_function_generator(awg_var_dict)

        self.test_data.log_script(["", "Config UA and FGen", "FGen output enabled", ""])

        if autoset_timebase:
            self.autoset_timebase(capture_cycles, delay_cycles)

        self.Motors.go_to_position(['R'], [-180], enable_ui=False)

        cont = self.scan_axis(self.element, axis='X', num_points=x_points, increment=x_increment_mm,
                              ref_position=assumed_x_coordinate,
                              go_to_peak=True, data_storage=data_storage, update_element_position=element_position_test,
                              acquisition_type=acquisition_type,
                              averages=averages, storage_location=storage_location)
        if not cont:
            return False

        self.home_system({'Axis to home': 'Theta'},theta_pre_home_move=False)

        cont = self.scan_axis(self.element, axis='Theta', num_points=theta_points,
                              increment=theta_increment_degrees,
                              ref_position=self.config["WTF_PositionParameters"]["ThetaHydrophoneCoord"],
                              go_to_peak=False, update_element_position=beam_angle_test, data_storage=data_storage,
                              acquisition_type=acquisition_type,
                              averages=averages, storage_location=storage_location)
        if not cont:
            return False

        self.AWG.set_output(False)
        self.test_data.log_script(['', 'Disable UA and FGen', 'Disabled FGen output', ''])
        self.test_data.log_script(['', 'End', 'OK', ''])

        if self.element <= 1 or abs(self.measured_element_r_coords[self.element] -
                                    mean(self.measured_element_r_coords[1:self.element])) > max_angle_variation_degrees:
            self.log(level='warning', message=f'Maximum theta coordinate of '
                                              f'{"%.2f" % self.measured_element_r_coords[self.element]} '
                                              f'deviates from -90 more than the allowed maximum of '
                                              f'{max_angle_variation_degrees}')
        return True

    # Reference position is the center of the scan range

    def scan_axis(self, element: int, axis: str, num_points: int, increment: float, ref_position: float,
                  data_storage: str, go_to_peak: bool, storage_location: str, update_element_position: bool,
                  scope_channel:int = 1, acquisition_type: str = 'N Averaged Waveform',
                  averages: int = 1, filename_stub: str ="FindElement") -> bool:
        """

        :returns: A boolean indicating whether to continue the script
        """

        self.element = element
        self.select_ua_channel(var_dict={"Element": self.element})

        self.oscilloscope_channel = scope_channel

        if axis == 'X':
            axis_letter = 'X'
        elif axis == 'Theta' or axis == 'R':
            axis_letter = 'R'
        else:
            self.user_prompt_signal.emit("Invalid axis parameter, aborting", False)
            self.abort_after_step()
            return False
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

                if 'entire waveform'.upper() in data_storage.upper() or 'all'.upper() in data_storage.upper():
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
                self.measured_element_x_coords[self.element] = max_position
            else:
                max_position += 90
                self.measured_element_r_coords[self.element] = max_position
                # Refresh the angle average in self.test_data
                self.test_data.calculate_angle_average(self.measured_element_r_coords)

        self.test_data.set_max_position(axis, self.element, max_position)

        status_str = f'Start {axis} {"%.2f" % self.measured_element_x_coords[self.element]} mm; Incr {axis} ' \
                     f'{increment} {pos_units_str}; #Points {num_points}; Peak {axis} = ' \
                     f'{"%.2f" % max_position} {pos_units_str};'

        if go_to_peak:
            status = self.Motors.go_to_position([axis_letter], [max_position], enable_ui=False)
            if status:
                status_str += f" moved to {axis} = {max_position} {pos_units_str}"
            else:
                status_str += f"move to {axis} = {max_position} {pos_units_str} failed"

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

    def __refresh_profile_plot(self, x_data: List[float], y_data: list, y_label: str) -> bool:
        """
        Helper function which refreshes the profile plot tab but not too often to bog down the thread

        :returns: True if method ran successfully, False otherwise
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

    def __save_hydrophone_waveform(self, axis: str, waveform_number: int, times_s: list, voltages_v: list,
                                   storage_location: str, filename_stub: str, x_units_str: str, y_units_str: str):
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

    def __save_scan_profile(self, axis: str, positions: List[float], vsi_values: list, storage_location: str,
                            filename_stub: str, x_units_str: str, y_units_str: str):
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

    def __save_frequency_sweep(self, frequencies: List[float], vsi_values: List[float], storage_location: str,
                               filename_stub: str, y_units_str: str):
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

        self.test_data.calculate_angle_average(self.measured_element_r_coords)

        if prompt_for_calibration_write:  # displays the "write to UA" dialog box if this variable is true
            self.yes_clicked_variable = False
            self.no_clicked_variable = False
            self.question_box_finished = False
            self.user_prompt_signal.emit("Do you want to write calibration data to UA?", False)

            cont = self.cont_if_answer_clicked()  # sets cont variable to true if user clicked continue
            if not cont:  # if user did not click continue, return
                return
            if self.yes_clicked_variable:
                calibration_data = generate_calibration_data(self.test_data)
                self.UAInterface.write_data(calibration_data)

        elif write_ua_calibration:
            calibration_data = generate_calibration_data(self.test_data)
            self.UAInterface.write_data(calibration_data)
        else:
            self.test_data.skip_write_to_ua = True

        # Save results summary to results folder
        if save_summary_file:  # ask for this in the abort methods
            self.file_saver.save_test_results_summary_and_log(test_data=self.test_data)

    def prompt_user_for_action(self, var_dict: dict) -> bool:
        """
        Waits for the user select continue, abort or retry via sending a signal
        to the main window. It extracts the Prompt type and message from the passed
        dict

        :param var_dict: dict must include 'Prompt type', should also have 'Prompt message' but has KeyError protection
        :returns: True if method ran successfully, False otherwise
        """
        prompt_type = var_dict["Prompt type"]
        if "Other".upper() in prompt_type.upper():
            try:
                prompt_type = var_dict["Prompt message"]
            except KeyError:
                prompt_type = "Blank Prompt"

            self.user_prompt_signal.emit(prompt_type, False)  # connected to show_user_prompt() in main window
        else:
            self.user_prompt_signal.emit(prompt_type, False)

        cont = self.cont_if_cont_clicked()  # waits for the user to click continue
        if not cont:  # if the user did not click continue, return
            return False
        return True

    def configure_function_generator(self, var_dict: dict) -> bool:
        """
        Set function generator to various desired settings, such as
        the mVpp, frequency, etc. from the passed variable dictionary.

        :param var_dict:
            must include 'Amplitude (mVpp)', 'Mode', 'Enable output', 'Set frequency options'. If
            frequency_options is 'From config cluster', dict must also include 'Frequency (MHz)'
        :returns: True if method runs successfully, False otherwise.
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
            self.abort_immediately()
            return False

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
        return True

    def configure_oscilloscope_channels(self, var_dict: dict) -> bool:
        """
        Extracts channel enabling flags, gains and offsets for both channels
        of oscilloscope, writes vertical scale and offset to oscilloscope

        :param var_dict:
            Must include 'Channel 1 Enabled', 'Channel 2 Enabled', 'Gain 1', 'Gain 2', 'Offset 1' and
            'Offset 2'
        :return: True if method completes without errors; false otherwise
        """
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
        return True

    def configure_oscilloscope_timebase(self, var_dict: dict) -> bool:
        """
        Sets the oscilloscope time delay and scale

        :param var_dict: extracts timebase and delay from passed variable dictionary for oscilloscope
        :returns: True if method completed without any errors
        """
        timebase_us = float(var_dict["Timebase"])
        delay_us = float(var_dict["Delay"])
        self.Oscilloscope.set_horizontal_scale_sec(timebase_us / 1000000)
        self.Oscilloscope.set_horizontal_offset_sec(delay_us / 1000000)
        if self.config['Debugging']['print_detailed_verbose']:
            self.log(message=f'oscilloscope horizontal scale sec set to: {timebase_us / 1000000}', level='debug')
            self.log(message=f'oscilloscope horizontal offset sec set to: {delay_us / 1000000}', level='debug')
        return True

    def autoset_timebase(self, capture_cycles: Union[float, None] = None,
                         delay_cycles: Union[float, None] = None) -> bool:
        """
        Sets the oscilloscope timebase according to the config file, or if capture cycles and delay cycles are
        provided, sets takes the default time offset, adds a delay according to delay cycles and the AWG frequency,
        and sets the time axis range according to capture_cycles

        :param capture_cycles: the number of cycles for the oscilloscope to capture; adjusts range
        :param delay_cycles: adds on to the standard offset on config for oscilloscope
        :returns: True if method runs without exceptions; false otherwise
        """

        try:
            if capture_cycles is None or delay_cycles is None:
                self.Oscilloscope.set_oscilloscope_timebase_to_default()
                return True

            capture_range_s = capture_cycles * 1 / self.AWG.get_frequency_hz()
            self.Oscilloscope.set_horizontal_range_sec(capture_range_s)

            standard_offset_s = self.config['Oscilloscope_timebase']['Time offset (us)'] * 10 ** -6
            additional_delay_s = delay_cycles * 1 / self.AWG.get_frequency_hz()
            self.Oscilloscope.set_horizontal_offset_sec(standard_offset_s + additional_delay_s)

            return True
        except Exception as e:
            self.log(message=f'autoset_timebase() in manager ran into exception: {e}', level='error')
            return False

    def home_system(self, var_dict: dict, show_prompt=False, theta_pre_home_move:bool =True) -> bool:
        """
        :param theta_pre_home_move: enables a theta movement to move the UA out of the active region of the home switch
        :return: whether to continue the script
        """
        axis_to_home = var_dict["Axis to home"]

        successful_go_home = False
        if axis_to_home == "All Axes":
            cont = self.retract_ua_warning()  # launch the retracting UA in the x direction warning box
            if not cont:
                return False
            successful_go_home = self.Motors.go_home(enable_ui=False, theta_pre_home_move=theta_pre_home_move)
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
            successful_go_home = self.Motors.go_home_1d("X", enable_ui=False, theta_pre_home_move=False)
            if successful_go_home and show_prompt:
                self.user_info_signal.emit(f'Homing successful, X moved to {self.Motors.coords_mm[0]}')
                cont = self.cont_if_cont_clicked()
                if not cont:
                    return False
            self.test_data.log_script(["", f"Home  X", f"Home X", f'Successful:{successful_go_home}'])
        elif axis_to_home == "Theta":
            successful_go_home = self.Motors.go_home_1d("R", enable_ui=False, theta_pre_home_move=theta_pre_home_move)
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
                self.abort_immediately()
                return False
        return True

    def move_system(self, var_dict: dict, average_angle=True) -> bool:
        """
        If move type is "Go To", the system will move to specific x and theta coordinates. If the move type is
        "Move to element", the system will move that element's measured x position (or assumed x if it has not been
        measured). The R coordinate will depend on the "Target" key, which can be "RFB", "Down", or "Hydrophone".
        Down and Hydrophone move Theta to -90 and -180 degrees respectively. RFB moves the theta coordinate to either
        the measured theta position from find element, or the average of all measured theta positions.
        (any elements that have not had theta measured will default to -90)
        """
        move_type = var_dict["Move Type"]

        if "Go To".upper() in move_type.upper():
            target_x_position = float(var_dict["X POS"])
            move_x = bool(var_dict["Move X"])
            target_theta_position = float(var_dict["Theta POS"])
            move_theta = bool(var_dict["Move Theta"])
            axes_to_be_moved = []
            target_coordinates = []
            if move_x:
                axes_to_be_moved.append("X")
                target_coordinates.append(target_x_position)
            if move_theta:
                axes_to_be_moved.append("R")
                target_coordinates.append(target_theta_position)
            self.Motors.go_to_position(axes=axes_to_be_moved, coordinates_mm=target_coordinates, enable_ui=False)
        else:
            self.element = self.element_str_to_int(var_dict["Element"])
            target = var_dict["Target"]

            if self.measured_element_x_coords[self.element] is not None:
                element_x_coordinate = self.measured_element_x_coords[self.element]
            else:
                element_x_coordinate = self.assumed_element_x_coords[self.element]

            if self.measured_element_r_coords[self.element] is not None:
                element_r_coordinate = self.measured_element_r_coords[self.element]
            else:
                element_r_coordinate = self.assumed_element_r_coords[self.element]

            success = True
            # todo: make sure these names match theirs
            # todo: make sure these home coordinates work as expected
            if "Hydrophone" in target:
                success = self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -180], enable_ui=False)
            elif "RFB" in target:
                if average_angle:
                    self.test_data.calculate_angle_average(self.measured_element_r_coords)
                    success = self.Motors.go_to_position(['X', 'R'],
                                                         [element_x_coordinate, self.test_data.angle_average],
                                                         enable_ui=False)
                else:
                    success = self.Motors.go_to_position(['X', 'R'], [element_x_coordinate,
                                                                      element_r_coordinate], enable_ui=False)
            elif "Down" in target:
                success = self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -90], enable_ui=False)

            x_coord_str = "%.2f" % element_x_coordinate
            r_coord_str = "%.1f" % element_r_coordinate

            if not success:
                self.log(f"Move to {self.element}, at coordinate x={x_coord_str}, r={r_coord_str} failed")
                cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail='Move System failed')
                return cont
            else:
                self.log(f"Moved to {self.element}, at coordinate x={x_coord_str}, r={r_coord_str}")

            self.test_data.log_script(["", "Move to element", f"moved to X={x_coord_str}, Th={r_coord_str}", ''])
        return True

    def select_ua_channel(self, var_dict: dict) -> bool:
        """
        Activate the relay channel in the UA's IO board and move to a specified element

        :param var_dict: Should contain at least 'Element' or 'Channel' key
        :returns: whether method finished successfully
        """
        if "Element" in var_dict.keys():
            self.element = self.element_str_to_int(var_dict["Element"])
        elif "Channel" in var_dict.keys():
            self.element = self.element_str_to_int(var_dict["Channel"])
        else:
            self.log(message="No element nor channel defined in variable dict for task 'select ua channel.",
                     level='warn')
            cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail='Select UA channel failed')
            return cont

        self.IO_Board.activate_relay_channel(channel_number=self.element)
        return True

    def frequency_sweep(self, var_dict: dict) -> bool:
        self.set_tab_signal.emit(['Scan'])

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
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        # todo: add peak VSI test (min or max?) to UA pass/fail and results summary
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
        func_var_dict["#Cycles"] = burst_count  # QUESTION: Rename to burst_cycles in the future?
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

        print(f"Max vsi frequency: {max_vsi_frequency}")
        print(f"VSI: {max_vsi}")

        if include_test:
            self.test_data.update_results_summary_with_frequency_sweep(
                frequency_range=frequency_range,
                element=self.element,
                frequency_mHz=max_vsi_frequency,
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

                if 'entire waveform'.upper() in data_storage.upper() or 'all'.upper() in data_storage.upper():
                    self.__save_hydrophone_waveform(axis='', waveform_number=i + 1, times_s=times_s,
                                                    voltages_v=voltages_v, storage_location=storage_location,
                                                    filename_stub="FrequencySweep", x_units_str='Time (s)',
                                                    y_units_str=y_units_str)

                vsi = self.find_vsi(times_s=times_s, voltages_v=voltages_v)

            list_of_VSIs.append(vsi)
            self.__refresh_profile_plot(list_of_frequencies_MHz[0:i], list_of_VSIs, "Frequency (Hz)")

        # frequencies will be on the x-axis
        return list_of_frequencies_MHz, list_of_VSIs, y_units_str, True

    def find_vsi(self, times_s: list, voltages_v: list) -> Union[None, float, ndarray]:
        """
        Returns the voltage squared integral of an oscilloscope waveform

        :param times_s: the horizontal time axis readings to be integrated
        :param voltages_v: the vertical voltage axis readings to be integrated

        :return: The voltage squared integral of an oscilloscope waveform
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

    def measure_element_efficiency_rfb(self, var_dict: Union[dict, OrderedDict]) -> Union[None, bool]:
        """
        This method cycles the ultrasound output from the ultrasound applicator on and off for specified intervals
        while continuously capturing data from the forward power meter, reflected power meter, and radiation force
        balance. The readings are captured from all 3 sensors at the same time using 4 additional threads directed by
        using a RFBDataLogger object. The refresh_rfb_tab helper method scrapes data from the RFBDataLogger and sends
        it as a signal to be displayed in the RFBTab of the UI. Finally, this method analyzes the data (stored in a
        RFBData object) and sends it to the FileSaver to be saved.

        :param var_dict: The variable ordered dictionary this method will use, passed from the script file
        :return: a boolean indicating whether to continue the script
        """
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
        storage_location = str(var_dict["Storage location"])
        data_directory = var_dict["Data directory"]
        target_position = var_dict["RFB target position"]  # QUESTION: do we need this and the variable below?
        target_angle = var_dict["RFB target angle"]
        efficiency_test = bool(var_dict["EfficiencyTest"])
        Pa_max = var_dict["Pa max (target, W)"]  # acoustic power
        Pf_max = var_dict["Pf max (limit, W)"]  # forward power
        reflection_limit = var_dict["Reflection limit (%)"]  # used to determine pass/fail of device

        if storage_location == 'UA Results Directory' or data_directory == '':
            storage_location = ''
        else:
            storage_location = data_directory

        test_result = "DNF"  # Show in the results summary that the test has begun by initializing to 'DNF'
        self.test_data.set_pass_result(self.element, test_result)  # helper method does that

        settling_time = self.config["Analysis"]['settling_time_s']

        # if test time is too short to analyze properly
        if rfb_on_time < settling_time * 2 or rfb_off_time < settling_time * 2:
            error_detail = "Warning: the on or off intervals are less than the sensor settling time specified in the " \
                           "config file. Either change it or load a different script"  # warn the user

            # allow the user to decide next course of action
            cont = self.sequence_pass_fail(action_type='Interrupt action', error_detail=error_detail)

            if not cont:  # if the user does not want to continue
                return False  # exit this method

        # Initialize RFB data structure via passing the class/method variables to RFBData constructor
        self.rfb_data = RFBData(element=self.element, water_temperature_c=self.thermocouple.get_reading(),
                                frequency_range=frequency_range, pf_max=Pf_max, pa_max=Pa_max,
                                ref_limit=reflection_limit, config=self.config)

        self.element_number_signal.emit(str(self.element))  # update the main window's current element variable
        if self.element == 1:
            self.set_tab_signal.emit(["RFB"])

        # todo: overwrite this with an insert at the end to check if the step finished successfully
        self.test_data.log_script(["Measure element efficiency (RFB)", "OK", "", ""])

        # Hardware checks
        try:
            # at this point in the script, the checks have been performed already
            # in pretest_initialization so no need to wrap in if statements
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
            self.user_prompt_signal.emit("Invalid set_frequency_options parameter, aborting", False)
            self.abort_after_step()
            return False
        self.configure_function_generator(awg_var_dict)

        # Configure other hardware
        self.Balance.zero_balance_instantly()

        self.test_data.log_script(["", "Start RFB Acquisition", "Started RFB Action", ""])

        # Run test
        # Begin multi-threaded capture from the power meters and the balance and cycle the awg on and off
        self.__begin_rfb_logger_thread(rfb_data=self.rfb_data)

        start_time = t.time()
        current_cycle = 1

        # Extra off cycle at beginning
        self.log(f"Turning off AWG T = {'%.2f' % (t.time() - start_time)}")
        self.AWG.set_output(False)
        # for the duration of rfb off time
        while t.time() - start_time < rfb_off_time:
            cont = self.__refresh_rfb_tab()
            if not cont:  # exits if abort flag is true or __refresh_rfb_tab fails
                return False

        while current_cycle <= on_off_cycles:  # beginning of our cycle loop
            cycle_start_time = t.time()

            self.log(f"Turning on AWG T = {'%.2f' % (t.time() - start_time)}")
            self.AWG.set_output(True)  # turn on awg
            while t.time() - cycle_start_time < rfb_on_time:  # for the duration of rfb on time
                cont = self.__refresh_rfb_tab()
                if not cont:
                    return False

            # Turn off AWG
            self.log(f"Turning off AWG T = {'%.2f' % (t.time() - start_time)}")
            self.AWG.set_output(False)
            # for the duration of rfb off time
            while t.time() - cycle_start_time < rfb_on_time + rfb_off_time:
                cont = self.__refresh_rfb_tab()
                if not cont:
                    return False

            current_cycle += 1

        # rfb_logger has been monitoring and recording test data behind the scenes
        self.__wrap_up_rfb_logger()

        self.test_data.log_script(["", "Run on/off sequence", "RFB Acquisition complete", ""])
        self.test_data.log_script(["", "Stop RFB Acquisition", "RFB Stopped, data saved", ""])

        # make all the data lists in rfb_data the same size as the shortest one to prevent length inequality
        self.rfb_data.trim_data()
        self.rfb_data.end_of_test_data_analysis()  # process internal rfb_data information

        data_is_valid, feedback = self.rfb_data.data_is_valid()

        if not data_is_valid:
            cont = self.sequence_pass_fail(action_type='Interrupt action',
                                           error_detail=f'Element_{self.element:02} {feedback}')
            if not cont:
                return False

        test_result, comment = self.rfb_data.get_pass_result()

        # prompt user if test failed
        if test_result.upper() == 'FAIL':
            # give user chance to retry, continue, or abort
            cont = self.sequence_pass_fail(action_type='Pass fail action',
                                           error_detail=f'Element_{self.element:02} Failed efficiency test')
            if not cont:
                return False
        elif test_result.upper() == 'DNF':  # if test did not finish or never started
            # give user chance to retry, continue, or abort
            cont = self.sequence_pass_fail(action_type='Interrupt action',
                                           error_detail=f'Element_{self.element:02} Failed efficiency test')
            if not cont:
                return False
        elif test_result.upper() == 'PASS':
            self.log(message=f"test result for {self.element} has passed", level='info')  # log it
        else:  # if the test_result is an invalid value
            self.log("self.rfb_data.get_pass_result() has returned an invalid result, aborting", self.warn)
            # inform the user of this issue
            self.user_info_signal.emit("self.rfb_data.get_pass_result() has returned an invalid result, aborting")
            self.abort_after_step()
            return False

        self.retry_clicked_variable = False  # needed in case we encounter a retry possibility again

        if efficiency_test:
            self.test_data.update_results_summary_with_efficiency_results(
                frequency_range=frequency_range,
                element=self.element,
                frequency_hz=self.AWG.state["frequency_Hz"],
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
        if self.config['Debugging']['print_detailed_verbose']:
            self.log(message=repr(self.rfb_data), level='debug')

        return True  # at this point in the code, the test finished without errors

    # noinspection PyUnresolvedReferences
    def __begin_rfb_logger_thread(self, rfb_data: RFBData) -> None:
        """
        Separate the RFB logger thread, that way manager thread is more freed up, and only has to worry about turn
        on and off AWG in certain intervals. RFB logger qthread has slots for receiving data from all the sensors,
        improves performance and reliability. Logger can be responsive to the sensor threads and the logger thread
        keeps reading synchronized.

        :param rfb_data: Contains testing information regarding RFB element efficiency, which the RFBDataLogger class
        requires
        """

        # declare rfb logger object using RFBDataLogger class, passing RFB variable data and hardware objects
        self.rfb_logger = RFBDataLogger(rfb_data, self.Balance, self.Forward_Power_Meter, self.Reflected_Power_Meter,
                                        config=self.config)
        self.AWG.output_signal.connect(self.rfb_logger.update_awg_on)  # lets rfb_logger know when AWG has new data
        self.rfb_logger.finished.connect(self.rfb_logger.deleteLater)
        self.rfb_logger.start(priority=QThread.HighPriority)

    def __wrap_up_rfb_logger(self) -> None:
        """
        This method calls the balance's logger's quit function to close
        the logger thread. Sleeps to .1 seconds to prevent issues
        """
        self.rfb_logger.quit()
        t.sleep(0.1)  # thread sleep prevents bug problems

    def write_cal_data_to_ua_dialog(self, calibration_data: list) -> None:
        """
        relays this data to the main window to open a GUI dialog to save calibration data.

        :param calibration_data: should be a 2d list: 1st col: cal data array, 2nd col: low freq, 3rd col: high freq
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

    def log(self, message: str, level: str = "info") -> None:
        """
        Relays to the log_msg method in useful_methods.py, simply pass the message to be logged and
        a string representing the log level ("info," "debug," "error," or "warning")

        :param message: message to log
        :param level: level of importance for the message
        """
        from inspect import getframeinfo, stack
        log_msg(self, root_logger=root_logger, message=message, level=level,
                line_number=getframeinfo(stack()[1][0]).lineno)

    def __refresh_rfb_tab(self) -> bool:
        """
        Helper function which retrieves data from the rfb_logger and tells the rfb tab to update

        :returns: a boolean indicating whether to continue the script
        """
        if self.abort_immediately_variable:
            # Stop the current method and any parent methods that called it
            return False

        rfb_cooldown_s = .05
        if t.time() - self.last_rfb_update_time > rfb_cooldown_s:  # if cooldown period has elapsed
            self.rfb_data = self.rfb_logger.rfb_data  # update local clas rfb_data with rfb_logger's rfb_data
            self.update_rfb_tab_signal.emit()  # connected to update_rfb_tab() in ui_rfb.py
            self.last_rfb_update_time = t.time()

        if self.app is not None:
            self.app.processEvents()
        return True

    @pyqtSlot(str)
    def exec_command(self, command: str) -> None:
        """
        Takes a command from main window or its tab and executes it in the run() method

        :param command: The string command; can be CLOSE, CONNECT, CAPTURE, STEP, ABORT, or SCAN
        """
        self.command = command
        self.condition.wakeAll()

    def sequence_pass_fail(self, action_type: str, error_detail: str) -> bool:
        """
        when calling, the following is recommended:

        cont = sequence_pass_fail(...)

        if not cont:
            return

        :param action_type: should be either "Interrupt action" or "Pass fail action"
        :param error_detail: should describe what went wrong.
        :returns: a boolean indicating whether to continue the script
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
            self.retry_count += 1
            return
        else:
            self.log(f"retry limit reached for {error_detail}, aborting script", self.warn)
            self.abort_after_step()

    def command_scan(self, command: str) -> bool:
        """
        Activated by the scan setup tab when start scan is clicked. Extracts parameters and initiates a 1D scan.
        The Manager's measured_element_x_coords and measured_element_r_coords variables will be updated, but the
        assumed_element_x_coords and assumed_element_r_coords will stay the same
        """
        # self.test_data.set_blank_values()
        self.enable_ui_signal.emit(False)
        self.set_abort_buttons_enabled_signal.emit(True)
        self.set_tab_signal.emit(["Scan", "1D Scan"])
        self.file_saver = FileSaver(self.config)
        self.test_data.serial_number = "Unknown"  # todo
        self.file_saver.create_folders(self.test_data)
        command_ray = command.split("_")
        axis = str(command_ray[1])
        pts = int(command_ray[2])
        increment = float(command_ray[3])
        ref_pos = command_ray[4]

        element_x_coordinate = self.assumed_element_x_coords[self.element]
        element_r_coordinate = self.assumed_element_r_coords[self.element]
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

        cont = self.scan_axis(element, axis, pts, increment, ref_pos, data_storage, go_to_peak,
                              data_directory, True, source_channel, acquisition_type, averages, filename_stub)
        if not cont:
            self.enable_ui_signal.emit(True)
            self.set_abort_buttons_enabled_signal.emit(False)
            return False

        self.enable_ui_signal.emit(True)
        self.set_abort_buttons_enabled_signal.emit(False)
        return True


class AbortException(Exception):
    pass


class RetryException(Exception):
    pass
