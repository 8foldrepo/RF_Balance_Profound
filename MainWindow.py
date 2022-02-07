import os
import sys
import webbrowser
import yaml

from Utilities.load_config import ROOT_LOGGER_NAME

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from Utilities.useful_methods import *
from Widget_Library import window_wet_test
from manager import  Manager
from Utilities.load_config import load_configuration
import logging

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

        self.manager = Manager(parent=None, config=self.config)
        self.thread_list.append(self.manager)

        for thread in self.thread_list:
            thread.start(priority = 4)

        self.configure_signals()

        self.style_ui()
        self.activateWindow()

    def style_ui(self):
        self.setWindowIcon(QIcon('8foldlogo.ico'))

    @pyqtSlot()
    def complete(self):
        self.logger_signal.emit("Manager routine terminated, resetting manager routine.")

    def configure_signals(self):
        self.command_signal.connect(self.manager.exec_command)
        self.load_button.clicked.connect(self.load_script)
        self.run_button.clicked.connect(lambda: self.command_signal.emit("RUN"))
        self.manager.script_name_signal.connect(self.script_name_field.setText)
        self.manager.created_by_signal.connect(self.created_by_field.setText)
        self.manager.created_on_signal.connect(self.created_on_field.setText)
        self.manager.description_signal.connect(self.script_description_field.setText)
        self.manager.num_tasks_signal.connect(self.set_num_tasks)
        self.manager.step_number_signal.connect(self.calc_progress)

    def popup(self, s):
        popup = QMessageBox()
        popup.setWindowTitle(" ")
        popup.setText(s)
        popup.exec()
        self.cont_signal.emit()

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

    @pyqtSlot(str)
    def emit_command_signal(self, command):
        self.command_signal.emit(command)

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
    def load_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "Script files (*.wtf *.txt)"
        )
        self.command_signal.emit('LOAD ' + path)

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
            self.command_signal.emit("close")
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    I = MainWindow()
    app.setStyle("fusion")
    I.show()
    sys.exit(app.exec_())
