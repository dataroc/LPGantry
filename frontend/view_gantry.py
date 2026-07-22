"""
gantryControl_view.py

Primary GUI tab for controlling the metrology gantry.

Responsibilities
----------------
- Create all GUI widgets
- Emit user interaction signals
- Provide simple update methods for the controller

No gantry logic, communication, or file parsing belongs here.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QSizePolicy,
    QTextEdit
)


class GantryControlView(QWidget):
    """
    Primary control tab.

    The controller should connect to the signals exposed here.
    """

    # ------------------------------------------------------------------
    # Signals
    # ------------------------------------------------------------------

    connectGantry = pyqtSignal()
    jogChanged = pyqtSignal(int)
    jogRequested = pyqtSignal(str, float)
    # axis, direction
    # Example:
    # ("X", +1)
    # ("Y", -1)

    speedChanged = pyqtSignal(int)

    setHomeRequested = pyqtSignal()

    allStopRequested = pyqtSignal()

    # Future signals
    simulateRequested = pyqtSignal()
    runRequested = pyqtSignal()
    toolpathBrowseRequested = pyqtSignal()

    # ------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.pendingSpeed = 0
        self.setObjectName("gantryControlView")

        self.build_ui()
        self.connect_signals()
        

    # ==================================================================
    # UI Construction
    # ==================================================================

    def build_ui(self):

        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(10)

        ###############################################################
        # LEFT CONTROL PANEL
        ###############################################################

        leftPanel = QFrame()
        leftPanel.setObjectName("leftControlPanel")
        leftPanel.setMinimumWidth(240)

        leftLayout = QVBoxLayout(leftPanel)
        leftLayout.setSpacing(15)

        # -------------------------------------------------------------
        # Jog Controls and Connection
        # -------------------------------------------------------------

        

       

        # Connect
        self.connectionStatus = QLabel("Not Connected")
        self.connectionStatus.setObjectName("connectionStatus")
        self.connectGantryButton = QPushButton("Connect to Gantry")
        self.connectGantryButton.setObjectName("Connect")

        leftLayout.addWidget(self.connectionStatus)
        leftLayout.addWidget(self.connectGantryButton)

        jogLabel = QLabel("Jog Controls")
        jogLabel.setObjectName("sectionHeader")

        leftLayout.addWidget(jogLabel)
        jogGrid = QGridLayout()
        jogSliderGrid = QGridLayout()

        # Jog Increment Slider
        self.jogSliderLabel = QLabel("Jog Increment")
        self.jogSliderLabel.setObjectName("jogSliderLabel")
        self.jogSlider = QSlider(Qt.Orientation.Horizontal)
        self.jogSlider.setObjectName("jogSlider")

        self.jogSlider.setMinimum(1)
        self.jogSlider.setMaximum(400)
        self.jogSlider.setValue(50)

        self.jogValueLabel = QLabel("50 mm")
        self.jogValueLabel.setObjectName("valueLabel")
        self.jogValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        jogSliderGrid.addWidget(self.jogSlider,0,0)
        jogSliderGrid.addWidget(self.jogValueLabel,0,1)
        jogSliderGrid.setColumnStretch(0, 3)
        jogSliderGrid.setColumnStretch(1, 1)

        # X

        self.xMinusButton = QPushButton("X -")
        self.xMinusButton.setObjectName("MinusButton")

        self.xPlusButton = QPushButton("X +")
        self.xPlusButton.setObjectName("PlusButton")

        # Y

        self.yMinusButton = QPushButton("Y -")
        self.yMinusButton.setObjectName("MinusButton")

        self.yPlusButton = QPushButton("Y +")
        self.yPlusButton.setObjectName("PlusButton")

        # Z

        self.zMinusButton = QPushButton("Z -")
        self.zMinusButton.setObjectName("MinusButton")

        self.zPlusButton = QPushButton("Z +")
        self.zPlusButton.setObjectName("PlusButton")

        # -------------------------------------------------------------
        # Speed Slider
        # -------------------------------------------------------------

        
        speedLabel = QLabel("Jog Speed")
        speedLabel.setObjectName("speedSliderLabel")
        speedGrid =  QGridLayout()
        self.speedSlider = QSlider(Qt.Orientation.Horizontal)
        self.speedSlider.setObjectName("speedSlider")

        self.speedSlider.setMinimum(1)
        self.speedSlider.setMaximum(30)
        self.speedSlider.setValue(0)

        self.speedValueLabel = QLabel("0 mm/s")
        self.speedValueLabel.setObjectName("valueLabel")
        self.speedValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sendSpeedButton = QPushButton("Set Speed")
        self.sendSpeedButton.setObjectName("setSpeedbtn")

        speedGrid.addWidget(self.speedSlider,0,0)
        speedGrid.addWidget(self.speedValueLabel,0,1)
        speedGrid.setColumnStretch(0, 3)
        speedGrid.setColumnStretch(1, 1)

        # ADD EVERYTHING TO THE LAYOUT

        
        

        leftLayout.addWidget(self.jogSliderLabel)
        leftLayout.addLayout(jogSliderGrid)
        leftLayout.addWidget(speedLabel)
        leftLayout.addLayout(speedGrid)
        leftLayout.addWidget(self.sendSpeedButton)

        jogGrid.addWidget(self.xMinusButton, 0, 0)
        jogGrid.addWidget(self.xPlusButton, 0, 1)

        jogGrid.addWidget(self.yMinusButton, 1, 0)
        jogGrid.addWidget(self.yPlusButton, 1, 1)

        jogGrid.addWidget(self.zMinusButton, 2, 0)
        jogGrid.addWidget(self.zPlusButton, 2, 1)

        leftLayout.addLayout(jogGrid)
        

        

        # -------------------------------------------------------------
        # Set Home
        # -------------------------------------------------------------

        self.setHomeButton = QPushButton("Set Home")
        self.setHomeButton.setObjectName("setHomeButton")
        

        leftLayout.addWidget(self.setHomeButton)

        #leftLayout.addStretch()

        # -------------------------------------------------------------
        # All Stop
        # -------------------------------------------------------------

        self.allStopButton = QPushButton("ALL\nSTOP")
        self.allStopButton.setObjectName("allStop")
        self.allStopButton.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )
        leftLayout.addWidget(self.allStopButton,stretch=1)


        ###############################################################
        # RIGHT PANEL
        ###############################################################

        rightPanel = QFrame()
        rightPanel.setObjectName("rightPanel")

        rightLayout = QVBoxLayout(rightPanel)

        # =============================================================
        # PLACEHOLDER
        #
        # Future top toolbar:
        #
        #  Explanation text
        #  Browse Toolpath Button
        #  Locked filename display
        #  Simulate Button
        #  Run Button
        #
        # =============================================================

        # Placeholder widget

        toolbarPlaceholder = QLabel(
            "Future Toolpath Controls Placeholder"
        )

        toolbarPlaceholder.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        toolbarPlaceholder.setObjectName(
            "toolpathToolbarPlaceholder"
        )

        toolbarPlaceholder.setFrameShape(
            QFrame.Shape.Box
        )

        rightLayout.addWidget(toolbarPlaceholder)

        # =============================================================
        # PLACEHOLDER
        #
        # Future Toolpath Visualizer
        #
        # Could eventually become:
        #   - PyQtGraph
        #   - OpenGL
        #   - QGraphicsView
        #
        # =============================================================

        self.visualizerPlaceholder = QFrame()

        self.visualizerPlaceholder.setObjectName(
            "toolpathVisualizer"
        )

        self.visualizerPlaceholder.setFrameShape(
            QFrame.Shape.Box
        )

        self.visualizerPlaceholder.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        rightLayout.addWidget(self.visualizerPlaceholder)

        # Output window for messages/errors
        rightLayout.addWidget(QLabel("Output"))
        self.output_window = QTextEdit()
        self.output_window.setReadOnly(True)
        self.output_window.setMaximumHeight(75)
        rightLayout.addWidget(self.output_window)

        ###############################################################

        mainLayout.addWidget(leftPanel)
        mainLayout.addWidget(rightPanel, 1)

    # ==================================================================
    # Signal Connections
    # ==================================================================

    def connect_signals(self):

        # Jog buttons

        self.xPlusButton.clicked.connect(
            lambda: self.jogRequested.emit("X", +1)
        )

        self.xMinusButton.clicked.connect(
            lambda: self.jogRequested.emit("X", -1)
        )

        self.yPlusButton.clicked.connect(
            lambda: self.jogRequested.emit("Y", +1)
        )

        self.yMinusButton.clicked.connect(
            lambda: self.jogRequested.emit("Y", -1)
        )

        self.zPlusButton.clicked.connect(
            lambda: self.jogRequested.emit("Z", +1)
        )

        self.zMinusButton.clicked.connect(
            lambda: self.jogRequested.emit("Z", -1)
        )

        # Speed
        self.speedSlider.valueChanged.connect(
            self._speed_slider_changed
        )

        self.jogSlider.valueChanged.connect(
            self._jog_slider_changed
        )

        self.sendSpeedButton.clicked.connect(
            lambda: self.speedChanged.emit(self.pendingSpeed)
        )

        self.connectGantryButton.clicked.connect(
            self.connectGantry.emit
        )

        # Home

        self.setHomeButton.clicked.connect(
            self.setHomeRequested.emit
        )

        # All Stop
        self.allStopButton.clicked.connect(
            self.allStopRequested.emit
        )

    # ==================================================================
    # Internal Slots
    # ==================================================================

    def _jog_slider_changed(self, value):

        self.jogValueLabel.setText(str(value)+" mm")
        self.jogChanged.emit(value)
        
    def _speed_slider_changed(self, value):

        self.speedValueLabel.setText(str(value)+"mm/s")
        self.pendingSpeed = value

    # ==================================================================
    # Public Interface
    # ==================================================================

    def set_speed(self, value: int):
        """
        Controller can update slider position.
        """
        self.speedSlider.setValue(value)

    # ---------------------------------------------------------------

    def set_machine_enabled(self, enabled: bool):
        """
        Enable/disable jogging.
        """

        self.xPlusButton.setEnabled(enabled)
        self.xMinusButton.setEnabled(enabled)

        self.yPlusButton.setEnabled(enabled)
        self.yMinusButton.setEnabled(enabled)

        self.zPlusButton.setEnabled(enabled)
        self.zMinusButton.setEnabled(enabled)

        self.setHomeButton.setEnabled(enabled)

    # ---------------------------------------------------------------

    def set_status_message(self, text: str):
        """
        Placeholder.

        Eventually this may update a status label or explanation box.
        """
        pass

    # ---------------------------------------------------------------

    def set_loaded_toolpath(self, filename: str):
        """
        Placeholder.

        Future locked filename display.
        """
        pass

    # ---------------------------------------------------------------

    def load_toolpath_preview(self):
        """
        Placeholder.

        Controller will eventually pass geometry for visualization.
        """
        pass

    # ---------------------------------------------------------------

    def animate_toolpath(self):
        """
        Placeholder.

        Animate end effector motion.
        """
        pass

    def appendToOutput(self, text):
        # strip extra newlines
        if text.strip():
            self.output_window.append(text)