import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6 import QtGui

from statemachines.interface_state import interfaceState
from statemachines.gantry_state import gantryState

from frontend.view_gantry import GantryControlView
from frontend.controller_gantry import gantryControl


class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.interface_state = interfaceState()
        self.gantry_state = gantryState()

        if getattr(sys,"frozen",False):
            # The application has been bundled as an executable
            self.MAIN_DIRECTORY = sys._MEIPASS
        else:
            # The application is running from terminal
            self.MAIN_DIRECTORY = os.path.dirname(__file__)
        
        self.interface_state.set_PARENT_DIRECTORY(self.MAIN_DIRECTORY)

        # Harness Stream of messages from backend/frontend 
        # SIGNALS CONNECTED TO RELEVANT TABS FURTHER DOWN AFTER TABS ARE INITIALIZED
        self.stdout_stream = textEmitter()
        self.broadcaster = broadcaster()
        self.stdout_stream.textWritten.connect(self.broadcaster.textWritten.emit)
        sys.stdout = self.stdout_stream

        # Main window
        self.setWindowTitle("Metrology Gantry")
        #self.icon = QtGui.QIcon(os.path.join(self.MAIN_DIRECTORY,'assets','logo.ico'))
        #self.setWindowIcon(self.icon)
        self.resize(1600,875)
        wrapper = QWidget()
        w_layout = QHBoxLayout(wrapper)
        w_layout.setContentsMargins(0,0,0,0)

        # Initialize tabs
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        w_layout.addWidget(self.tabs)

         # CRITICAL, MUST BE SET FOR ANYTHING TO BE DISPLAYED
        self.setCentralWidget(wrapper)

        # Load Tabs
        self.gantry_view = GantryControlView()
        self.gantry_control = gantryControl(self.gantry_view,self.gantry_state,self.interface_state)
        self.tabs.addTab(self.gantry_view,"Gantry Control")

        # Connect message stream to tabs that need to see stdout and stderr messages
        self.broadcaster.textWritten.connect(self.gantry_view.appendToOutput)


class broadcaster(QObject):
    textWritten = pyqtSignal(str)

class textEmitter(QObject):
    textWritten = pyqtSignal(str)
    def write(self, text):
        if text:
            self.textWritten.emit(str(text))
    def flush(self):
        pass


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = mainWindow()
    BASE_DIR = window.MAIN_DIRECTORY
    window.show()
    # load style sheet
    with open(os.path.join(BASE_DIR,"assets","style.qss"),"r") as f:
        style = f.read()
        application.setStyleSheet(style)

    sys.exit(application.exec())
