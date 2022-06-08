from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import QThread, QMutex, QWaitCondition, pyqtSignal, pyqtSlot
import sys
import time

"""
This example demonstrates the recommended way to cause events in the UI thread to trigger long-running methods
in the manager thread. This example demonstrates that when slots in the manager thread are triggered from the UI thread
the slot itself actually runs in the UI thread. 

To avoid bogging down the UI thread, one must connect a signal called 
command_signal to the manager's exec_command slot. To initiate a task, emit a string using the command_signal that
contains the name of the operation as well as any necessary parameters.

In the manager's run method, there is an else/if tree which looks for these commands, parses them, and calls the
corresponding method in the manager class. Because the code stems from the manager's run method, it will run in the 
manager thread, and therefore it won't tie up the UI. Furthermore, even if the button is still enabled, and clicked
repeatedly, neither the manager or the UI thread will get bogged down and the application won't crash, since the
manager's run loop is on hold while running the long running task. This is a boon to program stability and reliability.

For a more complex example, see how the start_scan_button in ui_elements/tabs/ui_scan.py emits a command signal to 
manager.py, containing all the variables needed to begin a 1D scan in the background.
"""


class simpleMainWindow(QMainWindow):
    """Simplified representation of the mainwindow class"""
    command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        QThread.currentThread().setObjectName("ui_thread")

        # Add a single button to the UI for demonstration purposes
        self.button = QPushButton("Begin big job")
        self.setCentralWidget(self.button)

        # Create the manager QThread and initiate its run loop
        self.manager = simpleManager()
        self.manager.start(priority=QThread.HighPriority)

        # Connect the signal emitted upon the button being clicked to the button_clicked method
        self.button.clicked.connect(self.button_clicked)

        # Connect the MainWindow's command signal to the manager's exec_command method
        self.command_signal.connect(self.manager.exec_command)

    def button_clicked(self):
        """Tell the manager to run the big job the next time it core event loop runs"""
        self.command_signal.emit("BIG JOB")


class simpleManager(QThread):
    """Simplified representation of the manager class"""
    command: str

    def __init__(self):
        super().__init__()
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
            if self.command == "BIG JOB":
                print("Command noticed by the manager thread's run loop")
                self.big_job()
            # Add additional commands here
            # elif self.command == "SOMETHING ELSE":
            #     self.do_something_else()
            self.command = ''
        pass

    def big_job(self):
        """Representation of a long-running task that would cause the application to freeze if run in the UI thread"""
        print(f"Running big job in: {QThread.currentThread().objectName()}")
        time.sleep(20)
        print("Done :)")

    @pyqtSlot(str)
    def exec_command(self, command):
        """Slot which receives a command from the UI thread, to be executed in the next iteration of the run loop"""
        print(f"{command} command received. This slot is running in {QThread.currentThread().objectName()}")
        self.command = command
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = simpleMainWindow()
    window.show()
    app.exec()
