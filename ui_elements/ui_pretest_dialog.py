from PyQt5.QtWidgets import QDialog
from Widget_Library import dialog_pretest
from PyQt5.QtCore import pyqtSignal
from ui_elements.my_qdialog import MyQDialog
from definitions import ROOT_DIR
from Utilities.useful_methods import is_number

class PretestDialog(MyQDialog, dialog_pretest.Ui_test_data_capture):
    pretest_metadata_signal = pyqtSignal(dict)  # signal from MainWindow to manager; operator, serial no., comment
    abort_signal = pyqtSignal()

    def __init__(self, parent=None, config=None):
        super().__init__(parent=parent, config=config)
        self.setupUi(self)
        self.configure_signals()
        self.metadata_dict = dict()

    def configure_signals(self):
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.lookup_button.clicked.connect(self.lookup_clicked)
        self.override_checkbox.clicked.connect(self.override_checkbox_clicked)

    def override_checkbox_clicked(self):
        if self.override_checkbox.isChecked():
            self.lf_MHz_field.setEnabled(True)
            self.hf_MHz_field.setEnabled(True)
            self.hardware_code_field.setEnabled(True)
        else:
            self.lf_MHz_field.setEnabled(False)
            self.hf_MHz_field.setEnabled(False)
            self.hardware_code_field.setEnabled(False)

    def lookup_clicked(self):
        serial_no = self.ua_serial_no_inputline.text().upper()
        self.lf_MHz_field.setText('')
        self.hf_MHz_field.setText('')
        self.hardware_code_field.setText('')

        with open(str(ROOT_DIR) + "\\Program_Data\\UA serial number and frequency data.txt") as f:
            line = f.readline()
            while line:
                line = f.readline()
                if len(serial_no) == 6 and serial_no in line:
                    chunks = line.replace(' ', '').split('|')
                    freqs = chunks[2].split(',')
                    hardware_code = chunks[3]

                    self.lf_MHz_field.setText(freqs[0])
                    self.hf_MHz_field.setText(freqs[1])
                    self.hardware_code_field.setText(hardware_code)
                    break

        if self.lf_MHz_field.text() == '':
            self.lf_MHz_field.setText("Not found")
        if self.hf_MHz_field.text() == '':
            self.hf_MHz_field.setText("Not found")
        if self.hardware_code_field.text() == '':
            self.hardware_code_field.setText("Not found")


    def ok_clicked(self):
        if self.ua_serial_no_inputline.text() == '' or self.test_operator_inputline.text() == '':
            self.feedback_label.setText("Fill all required fields")
            return

        if not is_number(self.lf_MHz_field.text()) or not is_number(self.hf_MHz_field.text()):
            self.feedback_label.setText("Frequencies must be numeric")
            return

        self.metadata_dict['test_comment'] = self.comment_inputbox.toPlainText()
        self.metadata_dict['serial_number'] = self.ua_serial_no_inputline.text()
        self.metadata_dict['operator_name'] = self.test_operator_inputline.text()
        self.metadata_dict['low_frequency_MHz'] = float(self.lf_MHz_field.text())
        self.metadata_dict['high_frequency_MHz'] = float(self.hf_MHz_field.text())
        self.metadata_dict['hardware_code'] = self.hardware_code_field.text()

        self.pretest_metadata_signal.emit(self.metadata_dict)
        self.close()

    def cancel_clicked(self):
        self.abort_signal.emit()
        self.close()

def print_info(dict):
    print(f"metadate {dict}")

if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    from datetime import date

    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")

    form = PretestDialog(config=None)
    today = date.today()
    formatted_date = today.strftime("%m/%d/%Y")
    form.date_output.setText(formatted_date)
    form.pretest_metadata_signal.connect(print_info)
    form.show()

    app.exec_()
