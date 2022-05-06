import distutils.util
import inspect
import logging
import os
import re
import sys
import time as t
from collections import OrderedDict
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
from Utilities.rfb_data_logger import RFBDataLogger
from Utilities.FileSaver import FileSaver
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import log_msg, get_element_distances, get_awg_on_values, generate_calibration_data
from Utilities.variable_containers import TestData, FileMetadata, SystemInfo
from definitions import ROOT_DIR, WaterLevel

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger("wtf_log")
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode="w")
file_handler.setFormatter(log_formatter)
wtf_logger.addHandler(file_handler)
wtf_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

pump_status = ""
tank_status = ""


# todo: continue adding prebuilt methods for all of the actions in script editor


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
    logging.Logger

    # Used for polling sensors while software is idle
    sensor_refresh_interval_s: float
    last_sensor_update_time: float

    # Dialog signals
    user_prompt_signal = pyqtSignal(str)  # str is message for user to read
    user_prompt_pump_not_running_signal = pyqtSignal(str)  # str is pump status
    user_prompt_signal_water_too_low_signal = pyqtSignal()  # str is water level
    user_prompt_signal_water_too_high_signal = pyqtSignal()
    write_cal_data_to_ua_signal = pyqtSignal(
        list
    )  # list is 2d array of calibration data
    retracting_ua_warning_signal = pyqtSignal()
    script_complete_signal = pyqtSignal(
        list, list
    )  # Contains a pass/fail/dnf list of strings and a list of descriptions

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

    rfb_args = dict()  # contains info for rfb tab
    update_rfb_tab_signal = pyqtSignal()
    # contains

    # sets the current tab text of the main window (must match a tab name of the main window
    set_tab_signal = pyqtSignal(str)

    Motors = None

    def __init__(self, system_info, config: dict, parent=None):
        super().__init__(parent=parent)
        # Default to operator access
        self.access_level = "Operator"
        self.rfb_logger = None
        QThread.currentThread().setObjectName("manager_thread")
        # decreasing these improves the refresh rate of the sensors, at the cost of responsiveness
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
        self.freq_highlimit_hz = None
        self.freq_lowlimit_hz = None
        self.parent = parent
        self.stay_alive = True

        # Stores latest command to be executed in the event loop
        self.cmd = ""

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

        # Tracks whether a script is currently being executed
        self.was_scripting = False # Flag to tell if a script has just stopped
        self.scripting = False
        # Flags for the wait_for_cont method, when a dialog is waiting for user action
        self.continue_var = True
        self.retry_var = False
        self.abort_var = False

        # Keeps track of script step in progress
        # step_index = -1 and if no script is being run.
        # step_index = -1 t is also the way to check if the script
        # has been aborted
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
            self.IO_Board = DIOBoard(config=self.config,simulate_sensors=self.config["Debugging"]["simulate_sensors"])

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
        i = 0
        while i < len(self.devices):
            device = self.devices[i]
            connected, feedback = device.connect_hardware()
            if not connected:
                self.user_prompt_signal.emit(
                    f"{device.device_key} Could not connect\n\n{feedback}"
                )
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

    def update_system_info(self):
        """
        Retrieve system info from devices, pass them to the system info tab, which overwrites systeminfo.ini
        with the info it finds
        """
        # todo: prevent script from running if cannot get serial_number of oscilloscope, fgen, etc
        info = SystemInfo()
        info.oscilloscope_sn = self.Oscilloscope.get_serial_number()
        info.awg_sn = self.AWG.get_serial_number()
        info.forward_power_sn = self.Forward_Power_Meter.get_serial_number()
        info.reflected_power_sn = self.Reflected_Power_Meter.get_serial_number()
        info.thermocouple_sn = self.thermocouple.get_serial_number()
        info.rf_balance_sn = self.Balance.get_serial_number()
        self.system_info_signal.emit(info)

    @pyqtSlot()
    def disconnect_hardware(self):
        """Safely disconnect all devices"""
        self.enable_ui_signal.emit(False)
        self.abort()
        for device in self.devices:
            device.disconnect_hardware()

    def run(self) -> None:
        """
        Core event loop of the manager thread. For any other methods to be executed in the manager thread
        They must be called from this method.
        """
        self.mutex.lock()
        self.start_time = t.time()

        self.stay_alive = True

        while self.stay_alive is True:
            wait_bool = self.condition.wait(self.mutex, 50)

            if self.stay_alive is False:
                break

            self.cmd = self.cmd.upper()
            cmd_ray = self.cmd.split(" ")
            if cmd_ray[0] == "CLOSE":
                self.wrap_up()
            elif cmd_ray[0] == "CONNECT":
                self.connect_hardware()
            elif cmd_ray[0] == "CAPTURE":
                self.capture_osc_and_plot()
            elif cmd_ray[0] == "STEP":
                self.advance_script()
            elif cmd_ray[0] == "ABORT":
                self.abort()
            # What to do when there is no command
            else:
                # If a script has just ended, show script_complete dialog
                if self.scripting:
                    if self.taskNames is None:
                        self.abort()
                    else:
                        self.advance_script()
                else:
                    if self.Oscilloscope.connected and self.config["Debugging"]["oscilloscope_realtime_capture"]:
                        self.capture_osc_and_plot()
                    else:
                        pass
                    self.update_sensors()
                    if self.thermocouple.connected:
                        self.thermocouple.get_reading()

            # Show script complete dialog whenever a script finishes
            if not self.scripting and self.was_scripting:
                self.script_complete()
            self.was_scripting = self.scripting

            self.cmd = ""
        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    @pyqtSlot()
    def run_script(self):
        if self.scripting:
            self.abort()
        log_msg(self, root_logger, level="info", message="Running script")
        self.scripting = True

    def update_sensors(self):
        # Return if the user is not looking at positional feedback
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
        try:
            time, voltage = self.Oscilloscope.capture(channel=channel)
            if plot:
                self.plot_scope(time, voltage)
            return time, voltage
        except pyvisa.errors.InvalidSession:
            self.log(
                level="error", message="Could not capture, oscilloscope resource closed"
            )
        return [], []

    def plot_scope(self, time, voltage):
        time_elapsed = t.time() - self.start_time
        if time_elapsed == 0:
            return

        refresh_rate = round(1 / time_elapsed, 1)
        self.plot_signal.emit(time, voltage, refresh_rate)

    # noinspection PyUnresolvedReferences
    def capture_osc_and_plot(self):
        # Do these things if a script is not being run

        if self.oscilloscope_averages != self.Oscilloscope.averages:
            self.Oscilloscope.SetAveraging(self.oscilloscope_averages)

        # Only capture if the scan tab is selected
        if not self.parent.scan_tab_widget.plot_ready:
            return
        if self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex()) != "Scan":
            return

        time, voltage = self.capture_scope(channel=self.oscilloscope_channel)

        self.plot_scope(time, voltage)
        self.start_time = t.time()

    # noinspection PyUnresolvedReferences
    def load_script(self, path):
        self.abort(log=False)

        self.script = open(path, "r")

        # Send name of script to UI
        split_path = path.split("/")
        self.test_data.script_name = split_path[len(split_path) - 1]
        self.script_name_signal.emit(self.test_data.script_name)

        tasks = []  # the upper layer of our variable list
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

            currentLine = currentLine + 1
            if line == "\n":
                if (
                        taskVars
                ):  # ensures task variable list isn't empty; prevents adding empty sub lists to main list
                    tasks.append(OrderedDict(taskVars))
                    taskVars.clear()  # empties out variable list for task since we're ready to move to the next set
                if (
                        addingElementsToLoop
                ):  # detects if we're done with the element name block for the loop in script
                    addingElementsToLoop = (
                        False  # we're done with the block so set the flag to false
                    )
                continue  # move forward one line
            elif "[" in line:  # if the line we're on is a task line
                taskNo = (
                        taskNo + 1
                )  # increments the task number counter since we've moved to the next task
                if "Task" in line and not buildingLoop:
                    self.taskExecOrder.append(
                        taskNo
                    )  # adding task number to the execution list
            else:  # above ensures we're not parsing a task header nor blank line
                x0 = ray[0].strip()  # remove trailing/leading spaces
                x1 = (
                    ray[1].strip().replace('"', "")
                )  # does above but also removes quotation marks
                taskVars[
                    x0
                ] = x1  # add the temporary variable pair to the task's variable list

                if "# of Tasks" in x0:
                    numberOfTasks = x1

                if (
                        "Loop over elements" in x1
                ):  # detects if we've encountered a loop builder task
                    buildingLoop = (
                        True  # set a flag that we're building a loop for the script
                    )
                    addingElementsToLoop = True  # set a flag that we're adding element names from script for loop

                # if we're on a line that adds an element name for the loop
                if addingElementsToLoop and "Element" in x0:
                    # split the left side of the variable assigner by space
                    elementNamePre = x0.split(" ")
                    # retrieve the second word of the left side, that's the element name
                    elementName = elementNamePre[1]
                    elementNamesForLoop.append(int(elementName))

                if (
                        "End loop" in x1
                ):  # script will have "End loop" in right side of task type to end loop block
                    buildingLoop = False  # set the building loop flag to false since the loop block is done
                    self.loops.append(
                        list([list(elementNamesForLoop), list(taskNoForLoop)])
                    )
                    elementNamesForLoop.clear()
                    taskNoForLoop.clear()
                    self.taskExecOrder.pop()

                    # appends a 2 item list in taskExecOrder, the first part being the element within the loops
                    # sublist and the second item being the iteration number for that item in its loop
                    for i in range(len(self.loops[len(self.loops) - 1][0])):
                        for j in range(len(self.loops[len(self.loops) - 1][1])):
                            self.taskExecOrder.append(
                                [
                                    self.loops[len(self.loops) - 1][1][j],
                                    i + 1,
                                    loop_index_tracker,
                                ]
                            )
                    loop_index_tracker = loop_index_tracker + 1

                # if we're building a loop & are not in the name adding phase
                if buildingLoop and not addingElementsToLoop:

                    # ensure the task no. isn't already in the task list for the loop
                    if taskNo not in taskNoForLoop:
                        taskNoForLoop.append(
                            taskNo
                        )  # add the current task no. to the list of tasks we need to run in loop
        f.close()

        if (
                taskVars
        ):  # ensures task variable list isn't empty; prevents adding empty sub lists to main list
            tasks.append(OrderedDict(taskVars))
            taskVars.clear()  # empties out variable list for task since we're ready to move to the next set

        for i in range(len(self.taskExecOrder)):
            if not isinstance(self.taskExecOrder[i], list):
                taskNoRemember = self.taskExecOrder[i]
                toReplace = [taskNoRemember, None]
                self.taskExecOrder[i] = toReplace

        self.taskNames = list()
        for i in range(len(self.taskExecOrder)):
            if "Task type" in tasks[self.taskExecOrder[i][0] + 1].keys():
                self.taskNames.append(tasks[self.taskExecOrder[i][0] + 1]["Task type"])

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
            self.retry_var = False  # sets the retry variable to false so the retry function can happen again

        # advance to the next step if the previous has been completed
        self.step_index = self.step_index + 1

        # if a script is being executed, and the step index is valid, and the previous step is complete,
        # run the next script step

        if self.step_index > len(self.taskNames):
            self.scripting = False
            return

        if (
                self.taskArgs is not None
                and self.taskNames is not None
                and self.taskExecOrder is not None
        ):
            if 0 <= self.step_index < len(self.taskNames):
                inside_iteration = False
                iteration_number = None

                if (
                        len(self.taskExecOrder[self.step_index]) == 3
                ):  # elements that are a part of a loop will have a third sub element
                    # notating which loop it's from
                    self.test_data.log_script(
                        [f"Iteration {self.taskExecOrder[self.step_index][1]} of "
                        f"{len(self.loops[self.taskExecOrder[self.step_index][2]][0])}","","","",]
                    )
                    inside_iteration = True
                    iteration_number = self.taskExecOrder[self.step_index][1]

                self.run_script_step()
                if inside_iteration:
                    self.test_data.log_script(
                        [f"Iteration {iteration_number} complete", "", "", ""]
                    )
                    inside_iteration = False

        if not self.scripting:
            self.enable_ui_signal.emit(True)

    """Executes script step with given step index in taskNames/taskArgs"""

    def run_script_step(self):
        if (
                self.taskArgs is None
                or self.taskNames is None
                or self.taskExecOrder is None
        ):
            self.abort()
            return

        name = self.taskNames[
            self.step_index
        ]  # sets name (str) to current iteration in taskNames list
        args = self.taskArgs[
            self.step_index
        ]  # sets args (list) to current iteration in taskArgs list

        self.task_number_signal.emit(self.taskExecOrder[self.step_index][0])
        self.task_index_signal.emit(self.step_index)

        if (
                self.taskExecOrder[self.step_index][1] is not None
        ):  # if the element in the self.taskExecOrder isn't None
            # below: set the element to be operated on to the one in self.taskExecOrder
            args["Element"] = self.taskExecOrder[self.step_index][1]

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
        elif"Function Generator".upper() in name.upper():
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
    def abort(self, log=True):
        """Aborts script when current step is done running"""
        if log:
            self.log("Aborting script")
        # Reset script control variables
        self.scripting = False
        self.step_index = -1
        self.continue_var = True
        self.abort_var = True
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
            self.wait_for_cont()
            return True
        except AbortException as e:
            self.test_data.log_script(["", "Prompt PowerAmp", "FAIL", "Closed by user"])
            return False
        except RetryException:
            self.step_index = self.step_index - 2

            return False

    """
    Sets continue variable to False and waits for it to be true, raising exceptions if the user 
    wants to abort or retry. Always handle these exceptions.
    """

    def wait_for_cont(self):
        self.continue_var = False
        self.retry_var = False
        self.abort_var = False

        while not self.continue_var:
            # check if script has been aborted
            if self.retry_var:
                self.retry_var = False
                # Always handle this exception
                raise RetryException
            if self.abort_var:
                self.abort_var = False
                # Always handle this exception
                raise AbortException

    """Continues execution of script"""

    @pyqtSlot()
    def cont(self):
        self.continue_var = True

    """Retries current step"""

    @pyqtSlot()
    def retry(self):
        self.retry_var = True

    def write_cal_data_to_ua_button(self):
        # Todo: make this method write calibration data to UA
        pass

    def script_complete(self):
        """Run when the script finishes its final step. Shows a dialog with pass/fail results and enables the UI"""
        # Fetch pass list and description list from testdata
        pass_list = list([None] * 11)
        description_list = list([None] * 11)
        for i in range(10):
            pass_list[i] = self.test_data.results_summary[i][15]
            description_list[i] = self.test_data.results_summary[i][16]

        # Add ua write result to output
        if self.test_data.write_result:
            pass_list[10] = "PASS"
        else:
            pass_list[10] = "FAIL"

        description_list[10] = ""

        self.script_complete_signal.emit(pass_list, description_list)
        self.scripting = False
        self.enable_ui_signal.emit(True)

        self.test_data.log_script(["Script complete", "", "", ""])

    def pretest_initialization(self, var_dict):
        """Collects metadata from user and prompts user until water level is ok"""
        # add first 4 lines of scriptlog
        self.test_data.log_script(
            [
                f"{self.test_data.serial_number}-{self.test_data.test_date_time}",
                "",
                "",
                "",
            ]
        )  # this is the first line
        self.test_data.log_script(
            ["Running script: ", self.test_data.script_name, "", "", ""]
        )
        self.test_data.log_script(["Pretest_initialization", "", "", ""])
        self.test_data.log_script(["", "Prompt username+UA serial", "OK", ""])

        # Check if wtfib is connected and add that to the scriptlog
        if self.UAInterface.read_result:
            self.test_data.log_script(["", "Get UA Serial", "Connected", "OK"])
        else:
            self.test_data.log_script(["", "Get UA Serial", "Connected", "FAIL"])
            if self.config["Debugging"]["end_script_on_errors"] and not self.access_level == "Operator":
                return self.abort()

        # Show dialogs until pump is on and the water sensor reads level
        while True:
            if not self.IO_Board.get_ua_pump_reading():  # if the pump is not running
                # launch the dialog box signifying this issue
                self.user_prompt_pump_not_running_signal.emit(pump_status)
                cont = self.cont_if_cont_clicked()

            else:
                self.test_data.log_script(["", "Check/prompt UA Pump", "OK", ""])
                break

        # todo: have ua inserted to certain x position like in the ScriptResults.log
        try:
            self.home_system(var_dict={"Axis to home": "All Axes"})
            self.test_data.log_script(
                [
                    "",
                    "Home all",
                    f"OK; X={self.Motors.coords_mm[0]}; "
                    f"Theta={self.Motors.coords_mm[1]}",
                    "",
                ]
            )
        except Exception as e:
            self.test_data.log_script(["", "Home all", f"FAIL: {e}", ""])
            if self.config["Debugging"]["end_script_on_errors"] and not self.access_level == "Operator":
                return self.abort()

        try:
            self.test_data.log_script(
                ["", "Insert UA", f"UA Inserted to X={self.Motors.coords_mm[0]}"]
            )
        except Exception as e:
            self.test_data.log_script(["", "Insert UA", f"FAIL {e}"])
            if self.config["Debugging"]["end_script_on_errors"]  and not self.access_level == "Operator":
                return self.abort()

        if self.thermocouple.connected:
            self.test_data.log_script(["", "CheckThermocouple", "OK", ""])
        else:
            self.test_data.log_script(["", "CheckThermocouple", "FAIL", ""])
            if self.config["Debugging"]["end_script_on_errors"]  and not self.access_level == "Operator":
                return self.abort()
            # have the script aborted or wait for thermocouple?

        burst_mode, unused = self.AWG.GetBurst()

        # Configure function generator
        func_var_dict = dict()
        func_var_dict["Amplitude (mVpp)"] = (
                self.config[self.AWG.device_key]["amplitude_V"] * 1000
        )
        func_var_dict["Frequency (MHz)"] = self.test_data.low_frequency_MHz
        func_var_dict["Mode"] = "Toneburst"
        func_var_dict["Enable output"] = True
        func_var_dict["#Cycles"] = self.config[self.AWG.device_key]["burst_cycles"]
        func_var_dict[
            "Set frequency options"
        ] = "From config cluster"  # Todo: what does this mean?
        self.configure_function_generator(func_var_dict)

        # Prompt user to turn on power amp
        while True:
            self.user_prompt_signal.emit("Please ensure that the power amplifier is on")

            cont = self.cont_if_cont_clicked()

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

        # todo: initialize results FGV here
        try:
            self.test_data.log_script(["", "Initialize results FGV", "OK", ""])
        except Exception as e:
            self.test_data.log_script(["", "Initialize results FGV", f"FAIL {e}", ""])

        # todo: duplicate main script?
        try:
            self.test_data.log_script(["", "duplicate main script", "OK", ""])
        except Exception as e:
            self.test_data.log_script(["", "Duplicate main script", f"FAIL {e}", ""])

        while True:
            water_level = self.IO_Board.get_water_level()

            if water_level == WaterLevel.below_level:  # if the water level is not level
                # launch the dialog box signifying this issue
                self.user_prompt_signal_water_too_low_signal.emit()
                cont = self.cont_if_cont_clicked()

                self.IO_Board.fill_tank()
            elif (
                    water_level == WaterLevel.above_level
            ):  # if the water level is not level
                # launch the dialog box signifying this issue
                self.user_prompt_signal_water_too_high_signal.emit()
                cont = self.cont_if_cont_clicked()

                self.IO_Board.fill_tank()
            else:
                self.test_data.log_script(["", "Check/prompt water level", "OK", ""])
                break

    """Retrieve metadata from mainwindow and trigger the script to run"""

    @pyqtSlot(TestData)
    def begin_script_slot(self, test_data: TestData):
        """Receive test metadata from the MainWindow, and begin a script."""

        # reset test data to default values
        self.test_data.set_blank_values()

        self.test_data.test_comment = test_data.test_comment
        self.test_data.serial_number = test_data.serial_number
        self.test_data.operator_name = test_data.operator_name
        self.test_data.low_frequency_MHz = test_data.low_frequency_MHz
        self.test_data.high_frequency_MHz = test_data.high_frequency_MHz
        self.test_data.hardware_code = test_data.hardware_code
        self.test_data.test_date_time = test_data.test_date_time
        self.file_saver.create_folders(test_data=self.test_data)
        self.run_script()

    def element_str_to_int(self, element_str):
        try:
            self.element = int(re.search(r"\d+", str(element_str)).group())
        except:
            self.log(
                f"Element number not given, using previous element: {self.element}"
            )
        return self.element

    def find_element(self, var_dict):
        self.log(
            f"find_element method called in manager.py, called by {inspect.getouterframes(inspect.currentframe(), 2)[1][3]}")
        """Find UA element with given number"""
        self.element = self.element_str_to_int(var_dict["Element"])
        x_increment_MM = float(var_dict["X Incr. (mm)"])
        XPts = int(var_dict["X #Pts."])
        thetaIncrDeg = float(var_dict["Theta Incr. (deg)"])
        thetaPts = int(var_dict["Theta #Pts."])
        scope_channel = int(var_dict["Scope channel"][8:])
        acquisition_type = var_dict["Acquisition type"]
        averages = int(re.search(r"\d+", str(var_dict["Averages"])).group())
        data_storage = var_dict["Data storage"]
        storage_location = var_dict["Storage location"]
        data_directory = var_dict["Data directory"]
        maxPosErrMM = float(var_dict["Max. position error (+/- mm)"])
        elemPosTest = bool(var_dict["ElementPositionTest"])

        # If on the first element, set the tab to the scan tab
        if self.element == 1:
            self.set_tab_signal.emit("Scan")

        self.test_data.log_script(['Find element "n"', "OK", "", ""])

        try:  # at this point in the script, the checks have been performed already in pretest_initialization so no
            # need to wrap in if statements
            self.test_data.log_script(
                [
                    "",
                    "PreChecks",
                    f"Tank fill status {self.IO_Board.get_water_level()}, UA pump status "
                    f"{self.IO_Board.get_ua_pump_reading()}",
                    "",
                ]
            )
        except Exception as e:
            self.test_data.log_script(["", "PreChecks", f"FAIL {e}", ""])

        # Update UI visual to reflect the element we are on
        self.element_number_signal.emit(str(self.element))

        element_x_coordinate = self.element_x_coordinates[self.element]
        element_r_coordinate = self.element_r_coordinates[self.element]
        print(
            f"Finding element {self.element}, near coordinate x = {element_x_coordinate}, r = {element_r_coordinate}"
        )

        # Configure hardware
        self.select_ua_channel(var_dict={"Element": self.element})
        frequency_Hz = self.test_data.low_frequency_MHz * 1000000
        self.AWG.SetFrequency_Hz(frequency_Hz)
        self.AWG.SetOutput(True)
        self.test_data.log_script(["", "Config UA and FGen", "FGen output enabled", ""])

        # todo: populate var_dict and make sure method is implemented
        autoset_var_dict = dict()
        self.autoset_timebase(autoset_var_dict)  # script log updated in this method

        self.scan_axis(
            axis="X",
            num_points=XPts,
            increment=x_increment_MM,
            ref_position=element_x_coordinate,
            go_to_peak=True,
            data_storage=data_storage,
            acquisition_type=acquisition_type,
            averages=averages,
        )

        self.home_system({"Axis to home": "Theta"})
        self.scan_axis(
            axis="Theta",
            num_points=thetaPts,
            increment=thetaIncrDeg,
            ref_position=self.config["WTF_PositionParameters"]["ThetaHydrophoneCoord"],
            go_to_peak=False,
            data_storage=data_storage,
            acquisition_type=acquisition_type,
            averages=averages,
        )

        # Todo: check
        self.home_system({"Axis to home": "Theta"})

        self.AWG.SetOutput(False)
        self.test_data.log_script(
            ["", "Disable UA and FGen", "Disabled FGen output", ""]
        )
        self.test_data.log_script(["", "End", "OK", ""])

    # Referemce position is the center of the scan range

    def scan_axis(
            self,
            axis,
            num_points,
            increment,
            ref_position,
            data_storage,
            go_to_peak,
            scope_channel=1,
            acquisition_type="N Averaged Waveform",
            averages=1,
    ):
        if axis == "X":
            axis_letter = "X"
        elif axis == "Theta":
            axis_letter = "R"
        else:
            raise Exception
        if self.Motors.rotational_ray[self.Motors.ax_letters.index(axis_letter)]:
            units_str = "deg"
            axis_label = "Angle (deg)"
        else:
            units_str = "mm"
            axis_label = "Distance (mm)"

        if acquisition_type.upper() == "N Averaged Waveform".upper():
            self.Oscilloscope.SetAveraging(averages)
        else:
            self.Oscilloscope.SetAveraging(1)

        # Loop over x through a given range, move to the position where maximal RMS voltage was measured
        positions = list()
        vsi_values = list()

        # sweep from the expected element position minus the max error to the expected element position plus max error
        position = -1 * (num_points * increment) / 2 + ref_position

        # begin with arbitrarily low values
        max_vsi = -1 * sys.float_info.max
        max_position = -1 * sys.float_info.max
        for i in range(num_points):
            self.Motors.go_to_position([axis_letter], [position])
            position = position + increment

            times_s, voltages_v = self.capture_scope(channel=scope_channel)

            if "Store entire waveform".upper() in data_storage.upper():
                self.save_hydrophone_waveform(
                    axis=axis,
                    waveform_number=i + 1,
                    times_s=times_s,
                    voltages_v=voltages_v,
                )

            vsi = self.find_vsi(times_s=times_s, voltages_v=voltages_v)

            if vsi > max_vsi:
                max_vsi = vsi
                max_position = position

            positions.append(position)
            vsi_values.append(vsi)
            self.profile_plot_signal.emit(positions, vsi_values, axis_label)

        self.test_data.log_script(
            [
                "",
                "Move to element",
                f"Moved to X={'%.2f' % self.Motors.coords_mm[0]}, "
                f"Th={'%.2f' % self.Motors.coords_mm[1]}",
                "",
            ]
        )

        self.log(f"Maximum of {max_vsi} @ {axis} = {max_position} {units_str}")

        if axis == "X":
            self.element_x_coordinates[self.element] = max_position
        else:
            self.element_r_coordinates[self.element] = max_position

        self.test_data.set_max_position(axis, self.element, max_position)

        status_str = (
            f'Start {axis} {"%.2f" % self.element_x_coordinates[self.element]} mm; Incr {axis} '
            f"{increment} {units_str}; #Points {num_points}; Peak {axis} = "
            f'{"%.2f" % max_position} '
            f"mm;"
        )

        if go_to_peak:
            status = self.Motors.go_to_position([axis_letter], [max_position])
            status_str = status_str + f" moved to {axis} = {max_position} {units_str}"

        self.test_data.log_script(["", f"Scan{axis} Find Peak {axis}:", status_str, ""])

        if not "Do not store".upper() == data_storage.upper():
            self.save_scan_profile(
                positions=positions, vsi_values=vsi_values, axis=axis
            )

    """Saves an oscilloscope trace using the file handler"""

    def save_hydrophone_waveform(self, axis, waveform_number, times_s, voltages_v):
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

        self.file_saver.store_waveform(
            metadata=metadata, times=times_s, voltages=voltages_v
        )

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

        self.file_saver.save_find_element_profile(
            metadata=metadata, positions=positions, vsi_values=vsi_values
        )

    def save_efficiency_test_data(
            self, f_time_s, f_power_w, r_time_s, r_power_w, a_time_s, a_power_w
    ):
        """Saves a voltage squared integral vs distance"""
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

        self.file_saver.store_measure_rfb_waveform_csv(
            metadata,
            forward_power=[f_time_s, f_power_w],
            reflected_power=[r_time_s, r_power_w],
            acoustic_power=[a_time_s, a_power_w],
        )

    def save_results(
            self, var_dict
    ):  # calibration_data is the data gathered by the UA test
        """Save scan results to a file"""
        save_summary_file = bool(
            distutils.util.strtobool(var_dict["Save summary file"])
        )
        write_uac_calibration = bool(
            distutils.util.strtobool(var_dict["Write UA Calibration"])
        )
        prompt_for_calibration_write = bool(
            distutils.util.strtobool(var_dict["PromptForCalWrite"])
        )

        # Todo: test
        if (
                prompt_for_calibration_write
        ):  # displays the "write to UA" dialog box if this variable is true
            self.user_prompt_signal.emit("Write calibration data to UA")
            cont = self.cont_if_cont_clicked()

        # Todo: populate calibration data from test data in useful_methods
        calibration_data = generate_calibration_data(self.test_data)
        self.UAInterface.write_data(calibration_data)

        self.test_data.software_version = self.config["Software_Version"]
        self.test_data.calc_angle_average()

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

            self.user_prompt_signal.emit(prompt_type)
        else:
            self.user_prompt_signal.emit(prompt_type)

        cont = self.cont_if_cont_clicked()

    def configure_function_generator(self, var_dict):
        """Set function generator to desired settings"""
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

        self.test_data.log_script(["", "Config FGen", f"{mVpp}mVpp;{fMHz}MHz,{mode}"])

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
            self.Oscilloscope.setVertScale_V(g1_mV_div / 1000, 1)
            self.Oscilloscope.setVertOffset_V(1, o1_mV / 1000)
        if c2_enabled:
            self.Oscilloscope.setVertScale_V(g2_mV_div / 1000, 2)
            self.Oscilloscope.setVertOffset_V(2, o2_mV / 1000)

    def configure_oscilloscope_timebase(self, var_dict):
        # todo: test
        timebase_us = float(var_dict["Timebase"])
        delay_us = float(var_dict["Delay"])
        self.Oscilloscope.setHorzScale_sec(timebase_us / 1000000)
        self.Oscilloscope.setHorzOffset_sec(delay_us / 1000000)

    def autoset_timebase(self, var_dict):
        self.Oscilloscope.autoset_timebase()

    def home_system(self, var_dict):
        """Return axis to zero coordinate"""
        # TODO: have this be called in pretest_initialization and have it add to script log
        axis_to_home = var_dict["Axis to home"]

        if axis_to_home == "All Axes":
            self.Motors.go_home()
            self.test_data.log_script(
                [
                    "",
                    "Home all",
                    f"X={self.Motors.coords_mm[0]}; "
                    f"Theta={self.Motors.coords_mm[1]}",
                    "",
                ]
            )
        elif axis_to_home == "X":
            self.retracting_ua_warning_signal.emit()  # launch the retracting UA in the x direction warning box
            self.Motors.go_home_1d("X")
            cont = self.cont_if_cont_clicked()

            self.test_data.log_script(["", f"Home  X", f"Home X", ""])
        elif axis_to_home == "Theta":
            self.Motors.go_home_1d("R")
            self.test_data.log_script(["", f"Home Theta", f"Home Theta", ""])
        else:
            self.test_data.log_script(
                ["", f"Home {axis_to_home}", "FAIL", "axis unrecognized"]
            )



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
            element_r_coordinate = self.element_x_coordinates[self.element]

            # todo: make sure these names match theirs
            # todo: make sure these home coordinates work as expected
            if "Hydrophone" in target:
                self.Motors.go_to_position(["X", "R"], [element_x_coordinate, 0])
            elif "RFB" in target:
                self.Motors.go_to_position(
                    ["X", "R"], [element_x_coordinate, element_r_coordinate]
                )
            elif "Down" in target:
                self.Motors.go_to_position(["X", "R"], [element_x_coordinate, -90])

            x_coord_str = "%.2f" % element_x_coordinate
            r_coord_str = "%.1f" % element_r_coordinate
            self.log(
                f"Moved to {self.element}, at coordinate x={x_coord_str}, r={r_coord_str}"
            )

            self.test_data.log_script(
                [
                    "",
                    "Move to element",
                    f"moved to X={x_coord_str}, Th={r_coord_str}",
                    "",
                ]
            )

    # todo: test
    def select_ua_channel(self, var_dict):
        """Activate the relay for and move to a specified element"""
        self.element = self.element_str_to_int(var_dict["Element"])
        self.IO_Board.activate_relay_channel(channel_number=self.element)

    def frequency_sweep(self, var_dict):
        """Sweep through a range of frequencies and plot the voltage squared integral"""
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

        coarse_freq_MHz_list, coarse_VSI_list = self.run_frequency_sweep(
            start_freq_MHz,
            end_freq_MHz,
            coarse_incr_MHz,
            burst_count,
            channel=scope_channel,
        )

        # todo: enable this in a way that makes sense and add it to the output file
        # fine_freq_MHz_list, fine_VSI_list = self.run_frequency_sweep(start_freq_MHz,end_freq_MHz,fine_incr_MHz,
        #                                                             burst_count, scope_channel = scope_channel)

        if data_storage == "Store entire waveform":
            # todo: move to file_saver object
            if storage_location == "UA results directory":
                path = (
                        self.config["Paths"]["UA results root directory"]
                        + "\\"
                        + self.test_data.serial_number
                        + "-"
                        + self.test_data.test_date_time
                        + "-frequency_sweep_data.csv"
                )  # retrieve path
            else:
                path = (
                        data_directory
                        + "\\"
                        + self.test_data.serial_number
                        + "-"
                        + self.test_data.test_date_time
                        + "-frequency_sweep_data.csv"
                )  # retrieve path

            # todo: implement
            self.file_saver.save_frequency_sweep()

            if not os.path.exists(os.path.dirname(path)):
                self.log("creating results path...")
                os.makedirs(os.path.dirname(path))

            f = open(path, "w")

            f.write("Frequency (MHz), Voltage squared integral")
            for i in range(len(coarse_freq_MHz_list)):
                f.write(f"{coarse_freq_MHz_list[i]},{coarse_VSI_list[i]}")

    def run_frequency_sweep(
            self, lower_limit_MHz, upper_limitMHz, freq_step, bursts, channel=1
    ):
        list_of_VSIs = list()
        list_of_frequencies_MHz = list()

        for x in np.arange(lower_limit_MHz, upper_limitMHz, freq_step):
            self.AWG.SetFrequency_Hz(
                x * 1000000
            )  # set frequency accoding to step (coarse/fine) and x incremenet
            # add the frequency to the list
            # Find the average vsi voltage at a given frequency
            vsi_sum = 0
            for i in range(bursts):
                times_s, voltages_v = self.capture_scope(
                    channel=1
                )  # populates times_s and voltages_v with set frequency
                vsi = self.find_vsi(times_s, voltages_v)
                vsi_sum = vsi_sum + vsi
            vsi_avg = vsi_sum / bursts

            list_of_frequencies_MHz.append(x)
            list_of_VSIs.append(vsi_avg)

        assert len(list_of_VSIs) == len(list_of_frequencies_MHz)

        self.profile_plot_signal.emit(
            list_of_frequencies_MHz, list_of_VSIs, "Frequency (Hz)"
        )

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
            self.log(
                level="Error",
                message="Error in find_vsi. No delta x found, cannot integrate",
            )
            return

        return integrate.simps(y=voltages_v_squared, dx=dx, axis=0)

    def measure_element_efficiency_rfb_multithreaded(self, var_dict):
        """Measure the efficiency of an element"""
        self.element = self.element_str_to_int(var_dict["Element"])
        frequency_range = var_dict["Frequency range"]  # High frequency or Low frequency
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
        efficiency_test = var_dict["EfficiencyTest"]
        Pa_max = var_dict["Pa max (target, W)"]
        Pf_max = var_dict["Pf max (limit, W)"]
        reflection_limit = var_dict["Reflection limit (%)"]

        # If on the first element, set the tab to the rfb tab
        if self.element == 1:
            self.set_tab_signal.emit("RFB")

        # todo: replace this with an insert at the end to check if the step finished successfully
        self.test_data.log_script(["Measure element efficiency (RFB)", "OK", "", ""])

        try:
            # Todo: add those checks anyway just because the script may vary
            # at this point in the script, the checks have been performed already in pretest_initialization so no
            # need to wrap in if statements
            self.test_data.log_script(
                [
                    "",
                    "PreChecks",
                    f"Tank fill status {self.IO_Board.get_water_level()}, UA pump status "
                    f"{self.IO_Board.get_ua_pump_reading()}",
                    "",
                ]
            )
        except Exception as e:
            self.test_data.log_script(["", "PreChecks", f"FAIL {e}", ""])

        # Todo: implement zeroing such that balance reading subtracts the averaging reading when the balance is off
        try:
            self.element = int(re.search(r"\d+", str(var_dict["Element"])).group())
        except:
            self.log(f"Element number not given, using current element: {self.element}")

        self.element_number_signal.emit(str(self.element))

        self.select_ua_channel(var_dict={"Element": self.element})
        self.move_system(
            var_dict={
                "Element": self.element,
                "Move Type": "Move to element",
                "Target": "RFB",
            }
        )

        self.test_data.log_script(
            ["", "Set frequency range", f'"{frequency_range}" range set', ""]
        )

        if frequency_range == "High frequency":
            frequency_Hz = self.test_data.high_frequency_MHz * 1000000
        elif frequency_range == "Low frequency":
            frequency_Hz = self.test_data.low_frequency_MHz * 1000000
        else:
            self.log("Improper frequency set, defaulting to low frequency")
            frequency_Hz = self.parent.ua_calibration_tab.Low_Frequency_MHz * 1000000

        self.AWG.SetFrequency_Hz(frequency_Hz)
        self.test_data.log_script(
            ["", "Configure FGen+PwrMeters", f"Frequency set to {frequency_Hz / 1000000} MHz", "", ])

        # self.Balance.zero_balance_instantly()  # todo: see if we need this

        forward_powers_w = list()
        forward_powers_time_s = list()
        reflected_powers_w = list()
        reflected_powers_time_s = list()
        acoustic_powers_w = list()
        acoustic_powers_time_s = list()

        awg_on = list()

        startTime = t.time()
        current_cycle = 1

        self.test_data.log_script(["", "Start RFB Acquisition", "Started RFB Action", ""])

        # Run test
        self.__begin_rfb_logger_thread()
        while current_cycle <= on_off_cycles:
            cycle_start_time = t.time()
            # Turn on AWG
            self.log("Turning off AWG")
            self.AWG.SetOutput(False)
            while (
                    t.time() - cycle_start_time < rfb_on_time
            ):  # for the duration of rfb on time
                self.rfb_args = self.rfb_logger.rfb_args
                self.update_rfb_tab_signal.emit()
                self.app.processEvents()
            #  turn on awg
            self.log("Turning on AWG")
            self.AWG.SetOutput(True)
            while (
                    t.time() - cycle_start_time < rfb_on_time + rfb_off_time
            ):  # for the duration of rfb on time
                self.rfb_args = self.rfb_logger.rfb_args
                self.update_rfb_tab_signal.emit()
                self.app.processEvents()
            current_cycle = (
                    current_cycle + 1
            )  # we just passed a cycle at this point in the code
        self.__wrap_up_rfb_logger()

        self.test_data.log_script(["", "Run on/off sequence", "RFB Acquisition complete", ""])
        self.test_data.log_script(["", "Stop RFB Acquisition", "RFB Stopped, data saved", ""])

        # List containing all readings while AWG was on
        acoustic_power_on_data = get_awg_on_values(acoustic_powers_w, awg_on)
        # Mean acoustic power while on
        acoustic_power_on_mean = sum(acoustic_power_on_data) / len(acoustic_power_on_data)

        # List containing all readings while AWG was on
        forward_power_on_data = get_awg_on_values(forward_powers_w, awg_on)
        # Mean acoustic power while on
        forward_power_on_mean = sum(forward_power_on_data) / len(forward_power_on_data)

        if forward_power_on_mean != 0:
            efficiency_percent = acoustic_power_on_mean / forward_power_on_mean
        else:
            efficiency_percent = 0

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

        self.test_data.update_results_summary_with_efficiency_results(
            frequency_range == "High frequency",
            self.element,
            frequency_Hz,
            efficiency_percent,
            reflected_power_percent,
            forward_power_max,
            water_temperature,
        )

        self.element_number_signal.emit(str(self.element))

        temp_var_for_next_command = var_dict["Pf max (limit, W)"]
        self.test_data.log_script(
            [
                "",
                "Pass/Fail test",
                f"Element_{self.element};Pf (W)={forward_power_on_mean};Pr (W)="
                f"{reflected_power_on_mean};Pa (W)={acoustic_power_on_mean};Efficiency (%)"
                f"={efficiency_percent};RF_Reflection (%)={reflected_power_percent};"
                f"Pf Max (W)={forward_power_max};WaterTemp (C)={water_temperature};"
                f"Test result=placeholder;Pf Max limit (W)={temp_var_for_next_command}",
                "",
            ]
        )

        # todo: pass correct arrays instead of forward power 3 times
        balance_readings_mg = [
            value * 1000 for value in self.rfb_logger.balance_readings_g
        ]
        # Time (s),Mass (mg),Acoustic Power (W), Pf(W), Pr(W)
        raw_data = [
            self.rfb_logger.times_s,
            balance_readings_mg,
            self.rfb_logger.acoustic_powers_w,
            self.rfb_logger.f_meter_readings_w,
            self.rfb_logger.r_meter_readings_w,
        ]
        power_on_w = [1.366937, 1.357604, 1.357465]  # begin test code
        power_off_w = [1.359971, 1.357153, 1.363679]
        cumulative_results = [
            [1.360669, 1.360268, 1.360468],
            [2.925537, 1.764390, 0.334969],
            [12.023259, 11.794621, 11.666714],
        ]
        absorption = ["Off", 1.000690]
        transducer_size = ["Off", 1.013496]
        focussing = ["Off", 1.000000]
        # absorb_trans_focus_times/transition_amp_times[0] = start on, [1] = end on, [2] = start off, [3] = end off
        absorb_trans_focus_times = [
            [9.784287, 30.010603, 50.511028],
            [11.048080, 31.280091, 51.729069],
            [20.055610, 40.457604, 60.772845],
            [21.230248, 41.546669, 62.039609],
        ]
        transition_amp_times = [
            [0.004380, 0.016061, 0.018981],
            [1.372454, 1.362233, 1.369534],
            [1.389974, 1.394355, 1.401655],
            [0.043802, 0.045262, 0.037961],
        ]  # end test data
        # todo: check that p_on_rand_unc is the one we want
        self.file_saver.store_measure_rfb_waveform_csv(
            element_number=self.element,
            ua_serial_number=self.test_data.serial_number,
            freq_mhz=frequency_MHz,
            diameter_mm=float(
                self.system_info["Hydrophone system"]["Hydrophone Diameter"]
                    .split(" ")[0]
                    .replace('"', "")
            ),
            propagation_distance_mm=15.000000,
            T_decC=water_temperature,
            UC_percent=float(self.rfb_args["p_on_rand_unc"]),
            power_ratio=1.000000,
            g_mpersecsqrd=9.810000,
            cal_fact=14600.571062,
            points=3,
            power_on_w=power_on_w,
            power_off_w=power_off_w,
            cumulative_results=cumulative_results,
            threshold=threshold,
            offset_s=offset,
            absorption=absorption,
            transducer_size=transducer_size,
            focussing=focussing,
            absorb_trans_focus_times=absorb_trans_focus_times,
            transition_amp_times=transition_amp_times,
            raw_data=raw_data,
        )

        self.test_data.log_script(["", "End", "", ""])

    def __begin_rfb_logger_thread(self):
        self.rfb_logger = RFBDataLogger(
            self.Balance, self.Forward_Power_Meter, self.Reflected_Power_Meter
        )
        self.AWG.output_signal.connect(self.rfb_logger.update_awg_on)
        self.rfb_logger.finished.connect(self.rfb_logger.deleteLater)
        self.rfb_logger.start(priority=QThread.HighPriority)

    def __wrap_up_rfb_logger(self):
        self.rfb_logger.quit()
        t.sleep(0.1)
        print(f"balance reading in manager.py: {self.Balance.get_reading()}")

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

    @pyqtSlot(str)
    def exec_command(self, command):
        self.cmd = command
        self.condition.wakeAll()


class AbortException(Exception):
    pass


class RetryException(Exception):
    pass
