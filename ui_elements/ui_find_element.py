from Widget_Library.widget_find_element import Ui_FIND_ELEMENT_WIDGET
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog


class FindElement(QWidget, Ui_FIND_ELEMENT_WIDGET):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.OSCOPE_DATA_DIRECTORY_BUTTON.clicked.connect(self.filebrowser)
        element_selection = self.ELEMENT_SELECTION_FIELD.currentText()
        print(element_selection)
        self.ELEMENT_SELECTION_FIELD.currentTextChanged.connect(self.monitor)

    def filebrowser(self):
        filename = QFileDialog.getOpenFileName(self, 'Select File', 'Desktop')
        self.OSCOPE_DATA_DIRECTORY_FIELD.setText(filename[0])

    def monitor(self):
        element_selection = self.ELEMENT_SELECTION_FIELD.currentText()
        print(element_selection)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FindElement()
    ui.show()
    sys.exit(app.exec_())
