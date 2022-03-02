import os
import sys
import webbrowser
import yaml
import csv

from ui_elements.ui_password_dialog import PasswordDialog

from Utilities.load_config import ROOT_LOGGER_NAME

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor
from Utilities.useful_methods import *
from Widget_Library import window_wet_test
from manager import Manager
from Utilities.load_config import load_configuration

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)

import os
from definitions import ROOT_DIR
balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR,"./logs/wtf.log"), mode='w')
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
    #Tracks whether the thread is doing something
    ready = True

    def __init__(self):
        # Load default.yaml file to self.config as a python dictionary
        super(MainWindow, self).__init__()
        self.threading = False

        self.setupUi(self)

        self.thread_list = list()
        self.config = load_configuration()

        self.manager = Manager(parent=self, config=self.config)
        self.plot_ready = True
        self.thread_list.append(self.manager)



        self.configure_signals()
        self.manager.connect_hardware()
        self.manager.start(priority=4)

        self.style_ui()
        self.activateWindow()

    def style_ui(self):
        self.setWindowIcon(QIcon('8foldlogo.ico'))

    #Populate fields in config tab with settings from the config file
    def populate_config_ui(self):
        self.operator_pass_field.setText(self.config["User Accounts"]["Operator"])
        self.engineer_pass_field.setText(self.config["User Accounts"]["Engineer"])
        self.admin_pass_field.setText(self.config["User Accounts"]["Administrator"])

        self.x_homecoord.setValue(self.config["WTF_PositionParameters"]["XHomeCoord"])
        self.theta_homecoord.setValue(self.config["WTF_PositionParameters"]["ThetaHomeCoord"])
        self.x_insertionpoint.setValue(self.config["WTF_PositionParameters"]["X-TankInsertionPoint"])
        self.x_element1.setValue(self.config["WTF_PositionParameters"]["X-Element1"])
        self.x_elementpitch.setValue(self.config["WTF_PositionParameters"]["X-Element pitch (mm)"])
        self.theta_prehomemove.setValue(self.config["WTF_PositionParameters"]["ThetaPreHomeMove"])
        self.thetaloadenc.setChecked(self.config["WTF_PositionParameters"]["ThetaLoadEnc?"])
        self.centerhometheta.setChecked(self.config["WTF_PositionParameters"]["CentreHomeTheta?"])

        self.lf_lowlimit.setValue(self.config["FrequencyParameters"]["LF"]["LowFreqLimit(MHz)"])
        self.lf_highlimit.setValue(self.config["FrequencyParameters"]["LF"]["HighFreqLimit(MHz)"])
        self.lf_amplitude.setValue(self.config["FrequencyParameters"]["LF"]["Amplitude(mVpp)"])
        self.lf_burstcount.setValue(self.config["FrequencyParameters"]["LF"]["BurstCount"])
        self.hf_lowlimit.setValue(self.config["FrequencyParameters"]["HF"]["LowFreqLimit(MHz)"])
        self.hf_highlimit.setValue(self.config["FrequencyParameters"]["HF"]["HighFreqLimit(MHz)"])
        self.hf_amplitude.setValue(self.config["FrequencyParameters"]["HF"]["HF.Amplitude(mVpp)"])
        self.hf_burstcount.setValue(self.config["FrequencyParameters"]["HF"]["HF.BurstCount"])
        self.search_coarseincr.setValue(self.config["FrequencyParameters"]["Search"]["CoarseIncr(MHz)"])
        self.search_fineincr.setValue(self.config["FrequencyParameters"]["Search"]["FineIncr(MHz)"])

        self.retries.setValue(self.config["Sequence pass/fail"]["Retries"])
        self.pass_fail_action.setCurrentText(self.config["Sequence pass/fail"]["Pass fail action"])
        self.interrupt_action.setCurrentText(self.config["Sequence pass/fail"]["Interrupt action"])
        self.dialog_timeout.setValue(self.config["Sequence pass/fail"]["Dialog timeout (s)"])

        self.daq_devicename.setText(self.config["WTF_DIO"]["DAQ Device name"])
        self.water_timeout.setValue(self.config["WTF_DIO"]["Water level timeout (s)"])
        self.fill_mode.setCurrentText(self.config["WTF_DIO"]["Fill/Drain mode"])

        self.min_time_of_flight.setValue(self.config["Autoset timebase"]["Min time of flight (us)"])
        self.max_time_of_flight.setValue(self.config["Autoset timebase"]["Max time of flight (us)"])

        self.ua_results_directory.setText(self.config["Paths"]["UA results root directory"])
        self.ua_serial_numbers_path.setText(self.config["Paths"]["UA Serial numbers file"])

    #Save the settings input into the UI field to the local.yaml config file
    def save_config(self):
        self.config["User Accounts"]["Operator"] = self.operator_pass_field.text()
        self.config["User Accounts"]["Engineer"] = self.engineer_pass_field.text()
        self.config["User Accounts"]["Administrator"] = self.admin_pass_field.text()

        self.config["WTF_PositionParameters"]["XHomeCoord"] = self.x_homecoord.value()
        self.config["WTF_PositionParameters"]["ThetaHomeCoord"] = self.theta_homecoord.value()
        self.config["WTF_PositionParameters"]["X-TankInsertionPoint"] = self.x_insertionpoint.value()
        self.config["WTF_PositionParameters"]["X-Element1"] = self.x_element1.value()
        self.config["WTF_PositionParameters"]["X-Element pitch (mm)"] = self.x_elementpitch.value()
        self.config["WTF_PositionParameters"]["ThetaPreHomeMove"] = self.theta_prehomemove.value()
        self.config["WTF_PositionParameters"]["ThetaLoadEnc?"] = self.thetaloadenc.isChecked()
        self.config["WTF_PositionParameters"]["CentreHomeTheta?"] = self.centerhometheta.isChecked()

        self.config["FrequencyParameters"]["LF"]["LowFreqLimit(MHz)"] = self.lf_lowlimit.value()
        self.config["FrequencyParameters"]["LF"]["HighFreqLimit(MHz)"] = self.lf_highlimit.value()
        self.config["FrequencyParameters"]["LF"]["Amplitude(mVpp)"] = self.lf_amplitude.value()
        self.config["FrequencyParameters"]["LF"]["BurstCount"] = self.lf_burstcount.value()
        self.config["FrequencyParameters"]["HF"]["LowFreqLimit(MHz)"] = self.hf_lowlimit.value()
        self.config["FrequencyParameters"]["HF"]["HighFreqLimit(MHz)"] = self.hf_highlimit.value()
        self.config["FrequencyParameters"]["HF"]["HF.Amplitude(mVpp)"] = self.hf_amplitude.value()
        self.config["FrequencyParameters"]["HF"]["HF.BurstCount"] = self.hf_burstcount.value()
        self.config["FrequencyParameters"]["Search"]["CoarseIncr(MHz)"] = self.search_coarseincr.value()
        self.config["FrequencyParameters"]["Search"]["FineIncr(MHz)"] = self.search_fineincr.value()

        self.config["Sequence pass/fail"]["Retries"] = self.retries.value()
        self.config["Sequence pass/fail"]["Pass fail action"] = self.pass_fail_action.currentText()
        self.config["Sequence pass/fail"]["Interrupt action"] = self.interrupt_action.currentText()
        self.config["Sequence pass/fail"]["Dialog timeout (s)"] = self.dialog_timeout.value()

        self.config["WTF_DIO"]["DAQ Device name"] = self.daq_devicename.text()
        self.config["WTF_DIO"]["Water level timeout (s)"] = self.water_timeout.value()
        self.config["WTF_DIO"]["Fill/Drain mode"] = self.fill_mode.currentText()

        self.config["Autoset timebase"]["Min time of flight (us)"] = self.min_time_of_flight.value()
        self.config["Autoset timebase"]["Max time of flight (us)"] = self.max_time_of_flight.value()

        self.config["Paths"]["UA results root directory"] = self.ua_results_directory.text()
        self.config["Paths"]["UA Serial numbers file"] = self.ua_serial_numbers_path.text()

        with open('local.yaml', 'w') as f:
            yaml.dump(self.config, f)

    def show_config(self):
        webbrowser.open("local.yaml")

    #Display the task names and arguments from the script parser with a QTreeView
    def visualize_script(self, arg_dicts:list):
        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        for i in range(len(arg_dicts)):

            if not '# of Tasks' in arg_dicts[i].keys():
                task = QStandardItem(arg_dicts[i]["Task type"])

                for key in arg_dicts[i]:
                    if not key == "Task type":
                        arg = QStandardItem(key + ": " + str(arg_dicts[i][key]))
                        task.appendRow(arg)

                rootNode.appendRow(task)

        self.script_step_view.setModel(treeModel)
        self.script_step_view.expandAll()
        self.script_step_view.setHeaderHidden(True)

    def prompt_for_password(self):
        dlg = PasswordDialog(parent = self, config=self.config)
        dlg.access_level_signal.connect(self.password_result)
        dlg.exec()

    @pyqtSlot(str)
    def password_result(self, access_level):
        if access_level == 'Engineer':

            self.tabWidget.removeTab(7)
        elif access_level == 'Operator':
            #Remove position tab, add more stuff like this later
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

        self.save_config_button.clicked.connect(self.save_config)
        self.show_config_button.clicked.connect(self.show_config)

        #Script metadata signals
        self.manager.script_name_signal.connect(self.script_name_field.setText)
        self.manager.created_by_signal.connect(self.created_by_field.setText)
        self.manager.created_on_signal.connect(self.created_on_field.setText)
        self.manager.description_signal.connect(self.script_description_field.setText)
        self.manager.num_tasks_signal.connect(self.set_num_tasks)
        self.manager.step_number_signal.connect(self.calc_progress)
        self.manager.script_info_signal.connect(self.visualize_script)

        #Hardware control signals
        self.command_signal.connect(self.manager.exec_command)
        self.x_pos_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion X+"))
        self.x_pos_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
        self.x_neg_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion X-"))
        self.x_neg_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
        self.theta_pos_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion R+"))
        self.theta_pos_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
        self.theta_neg_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion R-"))
        self.theta_neg_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
        self.go_x_button.clicked.connect(lambda: self.command_signal.emit(f"Motor Go {self.go_x_sb.value()}"))
        self.go_theta_button.clicked.connect(lambda: self.command_signal.emit(f"Motor Go ,{self.go_theta_sb.value()}"))
        self.reset_zero_button.clicked.connect(lambda: self.command_signal.emit("Motor Origin Here"))
        self.manual_home_button.clicked.connect(self.manual_home_clicked)
        self.insert_button.clicked.connect(self.insert_button_clicked)
        self.retract_ua_button.clicked.connect(self.retract_button_clicked)
        self.insert_ua_button.clicked.connect(self.insert_button_clicked)
        self.retract_ua_button.clicked.connect(self.retract_button_clicked)
        self.go_element_button.clicked.connect(self.go_element_button_clicked)
        #Hardware info signals
        self.manager.Motors.x_pos_signal.connect(self.update_x_postion)
        self.manager.Motors.r_pos_signal.connect(self.update_r_postion)
        self.manager.Motors.connected_signal.connect(self.motion_indicator.setChecked)
        self.manager.Balance.connected_signal.connect(self.rfb_indicator.setChecked)
        self.manager.thermocouple.connected_signal.connect(self.tcouple_indicator.setChecked)
        self.manager.thermocouple.reading_signal.connect(self.update_temp_reading)
        self.manager.plot_signal.connect(self.plot)


    @pyqtSlot(float)
    def update_temp_reading(self, temp):
        self.temp_field.setText(str(temp))

    @pyqtSlot(object,object)
    def plot(self, x, y):
        self.plot_ready = False
        self.waveform_plot.plot(x,y, pen = 'k', clear = True)
        self.plot_ready = True

    """Command the motors to go to the insertion point"""
    @pyqtSlot()
    def insert_button_clicked(self):
        self.command_signal.emit(f"Motor Go {self.config['WTF_PositionParameters']['X-TankInsertionPoint']}")

    """Command the motors to retract until a sensor is reached"""
    @pyqtSlot()
    def retract_button_clicked(self):
        #TODO: fill in later with the code that uses the retraction sensor
        self.command_signal.emit(f"Motor Go {-50}")

    """Command the motors to blindly go to an element as defined by the element number times the offset from element 1"""
    @pyqtSlot()
    def go_element_button_clicked(self):
        element_1_pos = self.config['WTF_PositionParameters']['X-Element1']
        element_pitch = self.config['WTF_PositionParameters']['X-Element pitch (mm)']

        if is_number(self.go_element_combo.currentText()):
            offset = (int(self.go_element_combo.currentText()) - 1) * element_pitch
            target_position = element_1_pos + offset
            self.command_signal.emit(f"Motor Go {target_position}")
        else:
            #TODO: fill in later to handle "current" element condition
            return

    @pyqtSlot()
    def manual_home_clicked(self):
        if self.x_home_radio.isChecked():
            self.command_signal.emit("Motor go 0")
        elif self.theta_home_radio.isChecked():
            self.command_signal.emit("Motor go ,0")
        elif self.all_axes_radio.isChecked():
            self.command_signal.emit("Motor go 0,0")

    @pyqtSlot(float)
    def update_x_postion(self,mm):
        try:
            self.x_pos_lineedit.setText(str(mm))
        except KeyboardInterrupt:
            pass

    @pyqtSlot(float)
    def update_r_postion(self, mm):
        try:
            self.theta_pos_lineedit.setText(str(mm))
        except KeyboardInterrupt:
            pass

    def load_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "Script files (*.wtf *.txt)"
        )
        self.command_signal.emit('LOAD ' + path)

    @pyqtSlot(int)
    def set_num_tasks(self,num_tasks):
        self.num_tasks = num_tasks

    @pyqtSlot(int)
    def calc_progress(self, step_number):
        if self.ready == False:
            return
        self.ready = False
        self.progressBar.setValue((step_number+1)/self.num_tasks*100)
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
        self.logger_signal.emit(str(Progress))

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
        if bQuit:
            self.command_signal.emit("CLOSE")
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    I = MainWindow()
    app.setStyle("fusion")
    I.show()
    sys.exit(app.exec_())
