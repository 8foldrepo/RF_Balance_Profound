from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import QThread, QMutex, QWaitCondition, pyqtSignal, pyqtSlot
import sys
import time

"""

This example demonstrates one way to cause events in the UI thread to trigger medium-long-running methods
in the manager thread. This example demonstrates that when slots in the manager thread are triggered from the UI thread
the slot itself actually runs in the UI thread, but by forcing UI updates with QApplication.processEvents() the UI 
does not freeze.

For better or for worse, this example allows the button to be clicked multiple times, which will cause multiples
of the task to run in parallel. Clicking the button rapidly will eventually cause the application to freeze.
Since the possibility of a crash is to be avoided at all costs, disable all non-essential buttons in the UI class
before initiating the task to prevent repeated input, and emit a signal to re-enable the ui from the backend class
once the operation is complete. Study the usage of the set_ui_enabled method in MainWindow and the 
enable_ui_signal in Manager for practical examples.
"""


class simpleMainWindow(QMainWindow):
    """Simplified representation of the mainwindow class"""

    begin_small_job_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        QThread.currentThread().setObjectName("ui_thread")

        # Add a single button to the UI for demonstration purposes
        self.button = QPushButton("Begin small job")
        self.setCentralWidget(self.button)

        # Create the manager QThread and initiate its run loop
        self.manager = simpleManager()
        self.manager.start(priority=QThread.HighPriority)

        # Connect the signal emitted upon the button being clicked to the button_clicked method
        self.button.clicked.connect(self.button_clicked)

        # Connect
        self.begin_small_job_signal.connect(self.manager.small_job)

    @pyqtSlot()
    def button_clicked(self):
        self.begin_small_job_signal.emit()

class simpleManager(QThread):
    """Simplified representation of the manager class"""

    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()  # This retrieves the current application and allows for forced UI updates
        self.stay_alive = True
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.command = ''

    def run(self):
        """Initiates the thread's run loop, to be run every 50 milliseconds."""
        QThread.currentThread().setObjectName("manager_thread")
        self.mutex.lock()

        while self.stay_alive:
            self.condition.wait(self.mutex, 50)  # This loop will run every 50 milliseconds

            #  Here manager thread loop is running for demonstration purposes but is not actually doing anything because
            #  The slot is being triggered directly by the UI thread. If this was the only technique used,
            #  There would be no justification for a separate QThread at all.

            #  For any heavy lifting or scripting tasks, refer to the trigger_big_

            pass
        pass

    @pyqtSlot()
    def small_job(self):
        """Representation of a long-running task that would cause the application to freeze if run in the UI thread"""
        print(f"Running small job in: {QThread.currentThread().objectName()}")

        start_time = time.time()
        while time.time()-start_time < 20:
            time.sleep(.1)
            self.app.processEvents()

        print("Done :)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = simpleMainWindow()
    window.show()
    app.exec()
