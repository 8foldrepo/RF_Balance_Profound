from Widget_Library.widget_save_results import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication


class SaveResults(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = SaveResults()
    ui.show()
    sys.exit(app.exec_())
