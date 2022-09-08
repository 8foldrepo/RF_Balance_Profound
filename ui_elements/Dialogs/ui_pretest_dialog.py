"""
This class controls the logic of the pretest dialog box, a task that is usually ran in the beginning
of a test. The dialog merely contains some input fields the user would need to fill in.
"""
import os
from datetime import datetime
from pprint import pprint
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from Utilities.useful_methods import is_number, check_directory, is_integer
from Widget_Library import dialog_pretest
from data_structures.test_data import TestData
from definitions import ROOT_DIR
from ui_elements.Dialogs.my_qdialog import MyQDialog

class PretestDialog(MyQDialog, dialog_pretest.Ui_test_data_capture):
    """
    This class extends MyQDialog and takes UI attributes from dialog_pretest.ui/py from the Widget_Library
    """
    # signal from MainWindow to manager; operator, serial no., comment. Bool is whether to begin script
    pretest_metadata_signal = QtCore.pyqtSignal(TestData, bool)
    abort_signal = pyqtSignal()

    def __init__(self, serial_no, schema, access_level, begin_script=True, parent=None, config=None):
        super().__init__(parent=parent, config=config)
        self.setupUi(self)
        self.configure_signals()
        self.test_data = TestData()
        self.test_data.schema = schema
        self.begin_script = begin_script  # Whether to tell manager to begin script when this dialog is dismissed
        # add formatted date
        now = datetime.now()
        date_formatted = now.strftime("%Y.%m.%d-%H.%M")

        # Get the current date, save it to the metadata dictionary, and show it in the UI
        self.ua_serial_no_inputline.setText(serial_no)
        self.schema = schema
        self.lookup_clicked()
        self.date_output.setText(date_formatted)

        if access_level.upper() == 'OPERATOR':
            self.override_checkbox.setEnabled(False)

        self.test_operator_inputline.setFocus()

    def configure_signals(self) -> None:
        """
        connects the OK, cancel, lookup, and override buttons/checkbox
        to class methods for additional coding operations
        """
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.lookup_button.clicked.connect(self.lookup_clicked)
        self.override_checkbox.clicked.connect(self.override_checkbox_clicked)

    def override_checkbox_clicked(self) -> None:
        """
        If override_checkbox is clicked, the user can manually input the
        low/high frequency, and hardware code fields; and vice versa
        """
        if self.override_checkbox.isChecked():
            self.lf_MHz_field.setEnabled(True)
            self.hf_MHz_field.setEnabled(True)
            self.hardware_code_field.setEnabled(True)
        else:
            self.lf_MHz_field.setEnabled(False)
            self.hf_MHz_field.setEnabled(False)
            self.hardware_code_field.setEnabled(False)

    def lookup_clicked(self) -> None:
        """
        If the user inputted a serial number, the program will look through a "database" of serial numbers to
        automatically retrieve and fill the hardware code, as well as the low and high frequency values for the device
        """
        serial_no = self.ua_serial_no_inputline.text().upper()
        self.lf_MHz_field.setText("")
        self.hf_MHz_field.setText("")
        self.hardware_code_field.setText("")
        ua_sn_path = self.config["Paths"]["UA Serial numbers file"]
        if ':' not in ua_sn_path:
            path = str(ROOT_DIR) + ua_sn_path
        else:
            path = ua_sn_path

        with open(path) as f:
            line = f.readline()
            while line:
                line = f.readline()
                if len(serial_no) == 6 and serial_no in line:
                    chunks = line.replace(" ", "").split("|")
                    frequencies = chunks[2].split(",")
                    hardware_code = chunks[3]

                    self.lf_MHz_field.setText(frequencies[0])
                    self.hf_MHz_field.setText(frequencies[1])
                    self.hardware_code_field.setText(hardware_code)
                    break


        if self.lf_MHz_field.text() == "":
            self.lf_MHz_field.setText("Not found")
        if self.hf_MHz_field.text() == "":
            self.hf_MHz_field.setText("Not found")
        if self.hardware_code_field.text() == "":
            self.hardware_code_field.setText("0")

    def ok_clicked(self) -> None:
        """
        This method validates the required information put into the prompt fields when the user clicks ok, if there's
        a problem with the given info, the program will notify the user and will give them a chance to fix it
        """
        if self.ua_serial_no_inputline.text() == '' or self.test_operator_inputline.text() == '':
            self.feedback_label.setText("Fill all required fields")
            return

        if not is_number(self.lf_MHz_field.text()) or not is_number(self.hf_MHz_field.text()):
            self.feedback_label.setText("Frequencies must be numeric")
            return

        if not is_integer(self.hardware_code_field.text()):
            self.feedback_label.setText("Hardware code must be an integer")
            return

        self.test_data.test_comment = self.comment_inputbox.toPlainText()
        self.test_data.serial_number = self.ua_serial_no_inputline.text()
        self.test_data.operator_name = self.test_operator_inputline.text()
        self.test_data.low_frequency_MHz = float(self.lf_MHz_field.text())
        self.test_data.high_frequency_MHz = float(self.hf_MHz_field.text())
        self.test_data.hardware_code = self.hardware_code_field.text()
        self.test_data.test_date_time = self.date_output.text()
        self.test_data.schema = self.schema
        self.pretest_metadata_signal.emit(self.test_data, self.begin_script)
        self.dialog_resolved = True

        self.close()

    def cancel_clicked(self) -> None:
        """Executes 'self.close()'; closes the prompt window"""
        self.close()


def print_info(info_dict: dict):
    """
    Prints contents of pretest metadata for debugging

    :param info_dict: the metadata is stored in a dictionary, pass it to view the contents in pprint format
    """
    print("metadata:\n")
    pprint(info_dict)


if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets, QtCore
    from datetime import date

    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")

    form = PretestDialog(config=None, access_level='Operator', serial_no='', schema='')
    today = date.today()
    formatted_date = today.strftime("%m/%d/%Y")
    form.date_output.setText(formatted_date)
    form.pretest_metadata_signal.connect(print_info)
    form.show()

    app.exec_()
