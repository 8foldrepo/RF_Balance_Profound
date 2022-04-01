from Widget_Library.widget_find_element import Ui_FIND_ELEMENT_WIDGET
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog


class FindElement(QWidget, Ui_FIND_ELEMENT_WIDGET):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

# TODO: Add signals for field inputs.

    def filebrowser(self):
        self.OSCOPE_DATA_DIRECTORY_FIELD.setText(QFileDialog.getOpenFileName())

        self.OSCOPE_DATA_DIRECTORY_BUTTON.clicked.connect()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FindElement()
    ui.show()
    sys.exit(app.exec_())
