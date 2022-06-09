from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser
from PyQt5.QtCore import QThread, QMutex, QWaitCondition, pyqtSignal, pyqtSlot
import sys
import time

"""
This example demonstrates the recommended way to update UI elements from a non-ui class.

Note that calling a method that draws to the UI (such as QTextBrowser.setText())
from the manager thread directly will likely cause a crash and is highly discouraged.

While drawing to the UI from another thread is a cardinal sin, calling any method in a UI class from a non-ui class
is advised against because it may have unpredictable results and it provides opportunities for current or future
programmers to mistakenly cause hard-to-track-down bugs. 

Instead, use signals and slots for all communication between the frontend and backend.
"""


class simpleMainWindow(QMainWindow):
    """Simplified representation of the mainwindow class"""
    command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        QThread.currentThread().setObjectName("ui_thread")

        # Add a single text output to the UI for demonstration purposes
        self.text_display = QTextBrowser()
        self.setCentralWidget(self.text_display)

        # Create the manager QThread and initiate its run loop
        self.manager = simpleManager()
        self.manager.start(priority=QThread.HighPriority)

        # Connect the manager's string to
        self.manager.elapsed_time_text_signal.connect(self.update_ui_text)

    @pyqtSlot(str)
    def update_ui_text(self, text: str):
        """Updates the text output in the UI. Note that this should not be called directly by a non-ui class"""
        self.text_display.setText(text)


class simpleManager(QThread):
    """Simplified representation of the manager class"""

    elapsed_time_text_signal = pyqtSignal(str)

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

        start_time = time.time()

        while self.stay_alive:
            self.condition.wait(self.mutex, 50)  # This loop will run every 50 milliseconds

            # Emit the elapsed time as a text signal to be received and displayed by a UI class
            self.elapsed_time_text_signal.emit(f"Elapsed time is {'%.2f' % (time.time() - start_time)} s")
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = simpleMainWindow()
    window.show()
    app.exec()
