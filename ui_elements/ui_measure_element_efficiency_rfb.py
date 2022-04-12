from Widget_Library.measure_element_efficiency import Ui_Form_2
from PyQt5.QtWidgets import QWidget, QApplication


class LoopOverElements(QWidget, Ui_Form_2):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = LoopOverElements()
    ui.show()
    sys.exit(app.exec_())
