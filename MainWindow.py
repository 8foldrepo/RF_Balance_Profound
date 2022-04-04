import copy
from configparser import ConfigParser

import os
import smtplib
import sys
import webbrowser
import yaml
import csv
import typing
from ui_elements.ui_password_dialog import PasswordDialog

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)
import os
from definitions import ROOT_DIR
balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

from ui_elements.ui_pretest_dialog import PretestDialog
from ui_elements.ui_user_prompt import WTFUserPrompt
from ui_elements.ui_retracting_ua_warning import UARetractDialog
from ui_elements.ui_write_cal_to_ua import WriteCalDataToUA
from ui_elements.ui_user_prompt_pump_not_running import WTFUserPromptPumpNotRunning
from ui_elements.ui_user_prompt_water_too_low import WTFUserPromptWaterTooLow

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor, QBrush
from Utilities.useful_methods import *
from Widget_Library import window_wet_test
from manager import Manager
from Utilities.load_config import load_configuration
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging

log_formatter = logging.Formatter(LOGGER_FORMAT)

import os
from Utilities.useful_methods import log_msg
from definitions import ROOT_DIR

balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class MainWindow(QMainWindow, window_wet_test.Ui_MainWindow):
    """
    this class oversees the user interface of the application. It contains a layout of
    widgets, each with their own functions. It relays the signals from the widgets to each other,
    as well as relaying signals from the UI widgets to the manager routine and vise versa.

    Attributes:
        manager: Manager() object which runs in a separate thread and carries out scripts and hardware instructions.

    Signals:
        load_script_signal(str): tell the manager to load the script with a given path
    Slots:
        complete: this method is run when the manager object is terminated.
    """

    command_signal = QtCore.pyqtSignal(str)

    root_logger = logging.getLogger(ROOT_LOGGER_NAME)
    plot_ready = QtCore.pyqtSignal(str)
    num_tasks = 0
    # Tracks whether the thread is doing something
    ready = True

    def __init__(self):
        # Load default.yaml file to self.config as a python dictionary
        super(MainWindow, self).__init__()
        self.threading = False

        self.setupUi(self)
        self.app = QApplication.instance()

        self.thread_list = list()
        self.config = load_configuration()
        self.system_config.set_config(self.config)

        self.manager = Manager(parent=self, config=self.config)
        self.plot_ready = True
        self.thread_list.append(self.manager)
        self.tree_items = None
        self.arg_dicts = None
        self.configure_signals()
        self.manager.connect_hardware()
        self.manager.start(priority=4)

        self.style_ui()
        self.activateWindow()

        self.position_tab.set_manager(self.manager)
        self.position_tab.set_motors(self.manager.Motors)
        self.position_tab.set_config(self.config)
        self.position_tab.configure_signals()

        self.rfb.set_manager(self.manager)
        self.rfb.set_config(self.config)
        self.rfb.set_balance(self.manager.Balance)

        self.results_tab.set_config(self.config)
        self.results_tab.set_manager(self.manager)

        self.ua_calibration_tab.set_config(self.config)
        self.ua_calibration_tab.set_manager(self.manager)
        self.ua_calibration_tab.set_ua_interface(self.manager.UAInterface)

        self.scan_tab_widget.set_config(self.config)
        self.scan_tab_widget.set_manager(self.manager)

    def style_ui(self):
        self.setWindowIcon(QIcon('8foldlogo.ico'))


        #Format treewidget
        self.script_step_view.setColumnCount(2)
        self.script_step_view.setHeaderLabels(["Task", "Arguments"])
        self.script_step_view.header().resizeSection(0, 220)

        #Set defaults for indicators
        self.script_status_indicator.setStyleSheet("background-color: grey")
        self.script_status_indicator.setText("NO SCRIPT")

        self.system_indicator.setText("IDLE")
        self.system_indicator.setStyleSheet("background-color: grey")

        self.moving_indicator.setStyleSheet("background-color:grey")
        self.moving_indicator.setText("STATIONARY")

        self.ua_pump_indicator.setStyleSheet("background-color: grey")
        self.ua_pump_indicator.setText("UA PUMP OFF")

        self.ua_on_indicator.setStyleSheet("background-color: grey")
        self.ua_on_indicator.setText("UA OFF")

    def disable_buttons(self):
        self.x_pos_button.setEnabled(False)
        self.x_neg_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.go_x_button.setEnabled(False)
        self.load_button.setEnabled(False)
        self.go_element_button.setEnabled(False)
        self.insert_button.setEnabled(False)
        self.retract_ua_button.setEnabled(False)
        self.go_x_button.setEnabled(False)
        self.show_config_button.setEnabled(False)
        self.save_config_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.manual_home_button.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.theta_pos_button.setEnabled(False)
        self.theta_neg_button.setEnabled(False)
        self.retract_button.setEnabled(False)
        self.reset_zero_button.setEnabled(False)
        self.go_theta_button.setEnabled(False)
        self.insert_button.setEnabled(False)

    # Display the task names and arguments from the script parser with a QTreeView
    def visualize_script(self, arg_dicts: list):
        print(arg_dicts)
        #Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.script_step_view.clear()
        self.arg_dicts = arg_dicts

        task_dict = {}
        for i in range(len(self.arg_dicts)):
            if not '# of Tasks' in self.arg_dicts[i].keys():
                arg_list = list()
                for key in self.arg_dicts[i]:
                    if not key == "Task type":
                        arg_list.append([key,self.arg_dicts[i][key]])

                task_dict[self.arg_dicts[i]["Task type"]] = arg_list

        self.tree_items = []
        for key, values in task_dict.items():
            item = QTreeWidgetItem([key])
            for value in values:
                child = QTreeWidgetItem(value)
                item.addChild(child)

            self.tree_items.append(item)

        self.script_step_view.insertTopLevelItems(0, self.tree_items)

    def update_script_visual_element_number(self, element_number):
        if 'Element' in element_number:
            return
        #Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        rootItem = self.script_step_view.invisibleRootItem()
        for i in range(rootItem.childCount()):
            task = rootItem.child(i)
            for j in range(task.childCount()):
                var = task.child(j)
                var_name = var.text(0)
                var_value = var.text(1)
                #If the variable is an element number that is looped
                if var_name == 'Element' and ('Current' in var_value or not 'Element' in var_value):
                    var.setText(1,f'Current: {self.live_element_field.text()}')

    @pyqtSlot(int)
    def expand_step(self, step_index):  # current_step should match "Task type" from above
        if self.tree_items is not None:
            for item in self.tree_items:
                item.setExpanded(False)
                white_background = QColor(255, 255, 255)
                brush_for_background = QBrush(white_background)
                item.setBackground(0, brush_for_background)
            if 0<= step_index < len(self.tree_items):
                self.tree_items[step_index].setExpanded(True)
                blue_background = QColor(95,180,230)
                brush_for_background = QBrush(blue_background)
                self.tree_items[step_index].setBackground(0,brush_for_background)

    def prompt_for_password(self):
        dlg = PasswordDialog(parent=self, config=self.config)
        dlg.access_level_signal.connect(self.password_result)
        dlg.exec()

    @pyqtSlot(str)
    def password_result(self, access_level):
        if access_level == 'Engineer':

            self.tabWidget.removeTab(7)
        elif access_level == 'Operator':
            # Remove position tab, add more stuff like this later
            self.tabWidget.removeTab(6)
            self.tabWidget.removeTab(6)
        elif access_level == 'Administrator':
            self.tabWidget.removeTab(6)
        else:
            sys.exit()

    def configure_signals(self):
        self.command_signal.connect(self.manager.exec_command)
        self.load_button.clicked.connect(self.load_script)
        self.run_button.clicked.connect(lambda: self.command_signal.emit("RUN"))
        self.abort_button.clicked.connect(self.manager.abort)

        # Script metadata signals
        self.manager.script_name_signal.connect(self.script_name_field.setText)
        self.manager.created_by_signal.connect(self.created_by_field.setText)
        self.manager.created_on_signal.connect(self.created_on_field.setText)
        self.manager.description_signal.connect(self.script_description_field.setText)
        self.manager.num_tasks_signal.connect(self.set_num_tasks)
        self.manager.step_number_signal.connect(self.calc_progress)
        self.manager.expand_step_signal.connect(self.expand_step)

        #When manager loads a script, visualize it in the left pane as well as loading it into the script editor
        self.manager.script_info_signal.connect(self.visualize_script)
        self.manager.script_info_signal.connect(self.script_editor.visualize_script)
        self.manager.script_info_signal.connect(self.update_script_indicator)

        self.manager.element_number_signal.connect(self.live_element_field.setText)
        self.manager.element_number_signal.connect(self.update_script_visual_element_number)

        # Hardware control signals
        self.command_signal.connect(self.manager.exec_command)  # deplicate of line 262
        self.insert_button.clicked.connect(self.insert_button_clicked)

        #enable/disable buttons signals
        self.position_tab.set_buttons_enabled_signal.connect(self.set_buttons_enabled)

        # Hardware info signals
        self.manager.Balance.connected_signal.connect(self.rfb_indicator.setChecked)
        self.manager.AWG.connected_signal.connect(self.fgen_indicator.setChecked)
        self.manager.thermocouple.connected_signal.connect(self.tcouple_indicator.setChecked)
        self.manager.Oscilloscope.connected_signal.connect(self.scope_indicator.setChecked)
        self.manager.UAInterface.connected_signal.connect(self.wtfib_indicator.setChecked)
        self.manager.IO_Board.connected_signal.connect(self.dio_indicator.setChecked)
        self.manager.thermocouple.reading_signal.connect(self.update_temp_reading)
        self.manager.plot_signal.connect(self.plot)
        self.manager.profile_plot_signal.connect(self.update_profile_plot)
        self.manager.Motors.connected_signal.connect(self.motion_indicator.setChecked)
        self.manager.Forward_Power_Meter.connected_signal.connect(self.power_meter_indicator.setChecked)
        self.manager.UAInterface.cal_data_signal.connect(self.ua_calibration_tab.populate_table)

        # Manager communication signals
        self.manager.pretest_dialog_signal.connect(self.show_pretest_dialog)
        self.manager.user_prompt_signal.connect(self.show_user_prompt)
        self.manager.user_prompt_pump_not_running_signal.connect(self.show_user_prompt_pump_not_running)
        self.manager.user_prompt_signal_water_too_low_signal.connect(self.show_user_prompt_water_too_low)
        self.manager.write_cal_data_to_ua_signal.connect(self.show_write_cal_data_prompt)
        self.manager.retracting_ua_warning_signal.connect(self.show_ua_retract_warn_prompt)

        self.manager.IO_Board.pump_reading_signal.connect(self.update_pump_indicator)
        self.manager.IO_Board.water_level_reading_signal.connect(self.update_water_level_indicator)
        self.manager.Motors.moving_signal.connect(self.update_motors_moving_indicator)
        self.manager.AWG.output_signal.connect(self.update_ua_indicator)

    @pyqtSlot(bool)
    def update_ua_indicator(self, on):
        if on:
            self.ua_on_indicator.setStyleSheet("background-color:green")
            self.ua_on_indicator.setText("UA ON")
        else:
            self.ua_on_indicator.setStyleSheet("background-color:grey")
            self.ua_on_indicator.setText("UA OFF")

    @pyqtSlot(str)
    def update_system_status(self, status):
        self.system_indicator.setText(status)
        if status != 'IDLE':
            self.system_indicator.setStyleSheet("background-color: yellow")

    @pyqtSlot(list)
    def update_script_indicator(self, script_info):
        self.script_status_indicator.setStyleSheet("background-color:green")
        self.script_status_indicator.setText("SCRIPT LOADED")

    @pyqtSlot(bool)
    def update_motors_moving_indicator(self, moving):
        if moving:
            self.moving_indicator.setStyleSheet("background-color:green")
            self.moving_indicator.setText("MOVING")
        else:
            self.moving_indicator.setStyleSheet("background-color:grey")
            self.moving_indicator.setText("STATIONARY")


    @pyqtSlot(str)
    def update_water_level_indicator(self, water_level):
        print(f"inside update water lvl indicator method; water_level = {water_level}")
        if water_level == "below_level":
            self.tank_level_indicator.setStyleSheet("background-color:red")
            self.tank_level_indicator.setText("TANK LOW")
        elif water_level == "above_level":
            self.tank_level_indicator.setStyleSheet("background-color:red")
            self.tank_level_indicator.setText("TANK HIGH")
        elif water_level == "level":
            self.tank_level_indicator.setStyleSheet("background-color:green")
            self.tank_level_indicator.setText("TANK LEVEL")

    @pyqtSlot(bool)
    def update_pump_indicator(self, is_on):
        if is_on:
            self.ua_pump_indicator.setStyleSheet("background-color: green")
            self.ua_pump_indicator.setText("UA PUMP ON")
        else:
            self.ua_pump_indicator.setStyleSheet("background-color: grey")
            self.ua_pump_indicator.setText("UA PUMP OFF")

    """Command the motors to go to the insertion point"""
    @pyqtSlot()
    def insert_button_clicked(self):
        self.command_signal.emit(f"Motor Go {self.config['WTF_PositionParameters']['X-TankInsertionPoint']}")

    @pyqtSlot()
    def update_x_speed(self):
        self.command_signal.emit(f"MOTOR SCAN SPEED X {self.lin_incr_double_sb.value()}")

    @pyqtSlot()
    def update_r_speed(self):
        self.command_signal.emit(f"MOTOR SCAN SPEED R {self.ang_inc_double_sb.value()}")

    @pyqtSlot(float)
    def update_temp_reading(self, temp):
        self.temp_field.setText(str(temp))

    @pyqtSlot(object, object, float)
    def plot(self, x, y, refresh_rate):
        self.scan_tab_widget.plot(x, y, refresh_rate)

    @pyqtSlot(list, list)
    def update_profile_plot(self, x, y):
        self.scan_tab_widget.update_profile_plot(x, y)

    def load_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "Script files (*.wtf *.txt)"
        )
        self.command_signal.emit('LOAD ' + path)

    @pyqtSlot(int)
    def set_num_tasks(self, num_tasks):
        self.num_tasks = num_tasks

    @pyqtSlot(int)
    def calc_progress(self, step_number):
        if self.ready == False:
            return
        self.ready = False
        if not self.num_tasks == 0:
            self.progressBar.setValue(int((step_number + 1) / self.num_tasks * 100))
        self.ready = True

    def popup(self, s):
        popup = QMessageBox()
        popup.setWindowTitle(" ")
        popup.setText(s)
        popup.exec()
        self.cont_signal.emit()

    def setupUi(self, MainWindow):
        super().setupUi(self)

        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open scan data",
            self,
        )
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.load_script)
        file_menu.addAction(open_file_action)

        print_action = QAction(
            QIcon(os.path.join("images", "printer.png")), "Print notes", self
        )
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)

        # adding Help on menu bar and open a specific file saved as "Help"
        file_menu = self.menuBar().addMenu("&Help")

        Show_Help_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open Help",
            self,
        )
        Show_Help_action.setStatusTip("Open Help")
        Show_Help_action.triggered.connect(self.Show_Help)
        file_menu.addAction(Show_Help_action)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    # Open help document
    def Show_Help(self):
        webbrowser.open("Help.txt")

    # Menu bar Actions
    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save file", "", "Text documents (*.txt)"
        )

        if not path:
            # If dialog is cancelled, will return ''
            return

        self._save_to_path(path)

    def _save_to_path(self, path):
        text = self.editor.toPlainText()
        try:
            with open(path, "w") as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path

            # Updating the Feedback window
            Progress = "Document Saved"
            self.feedback_Update.append(str(Progress))

    def file_print(self):
        from PyQt5.QtPrintSupport import QPrintDialog

        dlg = QPrintDialog()
        if dlg.exec_():
            self.NotesWidget.textEdit.print_(dlg.printer())

        # Updating the Feedback window
        Progress = "Notes Printed"
        self.log(str(Progress))

    def closeEvent(self, event):
        bQuit = False
        qReply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Do you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if qReply == QMessageBox.Yes:
            bQuit = True
            self.command_signal.emit("CLOSE")
            t.sleep(.1)
            self.manager.exit()
        if bQuit:
            event.accept()
        else:
            event.ignore()

    @pyqtSlot(str)
    def show_pretest_dialog(self, formatted_date):
        dlg = PretestDialog()
        dlg.date_output.setText(formatted_date)
        # below: calls method in manager that latches all input variables from dialog box to variables in manager class
        # when OK button is clicked
        dlg.pretest_signal.connect(self.manager.pretest_info_slot)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot()
    def show_user_prompt(self, message):
        dlg = WTFUserPrompt()
        dlg.user_prompt_output.setText(message)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.retry_signal.connect(self.manager.retry)
        dlg.continue_signal.connect(self.manager.cont)
        dlg.exec()

    @pyqtSlot()
    def show_ua_retract_warn_prompt(self):
        dlg = UARetractDialog()
        dlg.continue_signal.connect(self.manager.cont)
        dlg.cancel_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot()
    def show_write_cal_data_prompt(self, calibration_data):  # calibration data var is 2d list
        dlg = WriteCalDataToUA()
        dlg.schema.setText(calibration_data[0][0])
        dlg.serial_no.setText(calibration_data[0][1])
        dlg.prod_date.setText(calibration_data[0][2])
        dlg.hardware_code.setText(calibration_data[0][3])
        dlg.common_lo_freq.setText(calibration_data[0][4])
        dlg.common_hi_freq.setText(calibration_data[0][5])
        dlg.beam_align.setText(calibration_data[0][6])
        dlg.command.setText(calibration_data[0][7])
        dlg.status.setText(calibration_data[0][8])
        dlg.fw_version.setText(calibration_data[0][9])
        
        dlg.schema_lo.setText(calibration_data[1][0])
        dlg.serial_no_lo.setText(calibration_data[1][1])
        dlg.prod_date_lo.setText(calibration_data[1][2])
        dlg.hardware_code_lo.setText(calibration_data[1][3])
        dlg.common_lo_freq_lo.setText(calibration_data[1][4])
        dlg.common_hi_freq_lo.setText(calibration_data[1][5])
        dlg.beam_align_lo.setText(calibration_data[1][6])
        dlg.command_lo.setText(calibration_data[1][7])
        dlg.status_lo.setText(calibration_data[1][8])
        dlg.fw_version_lo.setText(calibration_data[1][9])
        
        dlg.schema_hi.setText(calibration_data[2][0])
        dlg.serial_no_hi.setText(calibration_data[2][1])
        dlg.prod_date_hi.setText(calibration_data[2][2])
        dlg.hardware_code_hi.setText(calibration_data[2][3])
        dlg.common_lo_freq_hi.setText(calibration_data[2][4])
        dlg.common_hi_freq_hi.setText(calibration_data[2][5])
        dlg.beam_align_hi.setText(calibration_data[2][6])
        dlg.command_hi.setText(calibration_data[2][7])
        dlg.status_hi.setText(calibration_data[2][8])
        dlg.fw_version_hi.setText(calibration_data[2][9])
        
        dlg.write_ua_signal.connect(self.manager.write_cal_data_to_ua_button)
        dlg.cancel_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot(str)
    def show_user_prompt_pump_not_running(self, pump_status):
        dlg = WTFUserPromptPumpNotRunning()
        dlg.label.setText(pump_status)
        # todo: have ua_pump_status switch react to pump_status var
        dlg.continue_signal.connect(self.manager.cont)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.set_pump_signal.connect(self.manager.IO_Board.set_pump_on)
        dlg.exec()

    @pyqtSlot(str)
    def show_user_prompt_water_too_low(self, water_level):
        if water_level == 'above_level':
            dlg = WTFUserPromptWaterTooLow(high=True)
        else:
            dlg = WTFUserPromptWaterTooLow(high=False)

        if water_level == 'above_level':
            dlg.label.setText("Above level")
        elif water_level == 'below_level':
            dlg.label.setText("Below level")
        elif water_level == 'level':
            dlg.label.setText("Water level is good")

        # todo: have ua_water_level switch react to water_level var
        dlg.continue_signal.connect(self.manager.cont)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        #Todo: make this ebable/disable all buttons of all tabs that could interfere with operations in progress
        self.position_tab.set_buttons_enabled(enabled)
        self.insert_button.setEnabled(enabled)
        self.retract_button.setEnabled(enabled)

    def log(self, message, level = 'info'):
        log_msg(self,self.root_logger, message= message,level=level)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    I = MainWindow()
    app.setStyle("fusion")
    I.show()
    sys.exit(app.exec_())
