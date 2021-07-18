"""
PointsWidget

:Authors:
    Berend Klein Haneveld
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QScrollArea
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal
from ui.widgets import Style


class PointsWidget(QWidget):
    """
    PointsWidget
    """

    activeLandmarkChanged = Signal(int)
    landmarkDeleted = Signal(int)

    def __init__(self):
        super(PointsWidget, self).__init__()

        self.landmarkWidgets = []
        self.activeIndex = 0

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setAutoFillBackground(False)
        self.scrollArea.setAttribute(Qt.WA_TranslucentBackground)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)

        landmarkLocationsLayout = QGridLayout()
        landmarkLocationsLayout.setSpacing(0)
        landmarkLocationsLayout.setContentsMargins(0, 0, 0, 0)
        landmarkLocationsLayout.setAlignment(Qt.AlignTop)

        self.landmarkLocationsWidget = QWidget()
        Style.styleWidgetForTab(self.landmarkLocationsWidget)
        self.landmarkLocationsWidget.setLayout(landmarkLocationsLayout)
        self.scrollArea.setWidget(self.landmarkLocationsWidget)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollArea)
        self.setLayout(layout)

    @Slot(list)
    def setPoints(self, points):
        self._clearLandmarkWidgets()
        layout = self.landmarkLocationsWidget.layout()
        for index in range(len(points)):
            landmarkWidget = LandmarkLocationWidget()
            landmarkWidget.setIndex(index)
            landmarkWidget.active = index == self.activeIndex
            landmarkWidget.activated.connect(self.activateLandmark)
            landmarkWidget.deleted.connect(self.deleteLandmark)
            landmarkWidget.setLandmarkSet(points[index])
            layout.addWidget(landmarkWidget, index, 0)
            self.landmarkWidgets.append(landmarkWidget)

    def _clearLandmarkWidgets(self):
        layout = self.landmarkLocationsWidget.layout()
        for widget in self.landmarkWidgets:
            widget.activated.disconnect()
            layout.removeWidget(widget)
            widget.deleteLater()
        self.landmarkWidgets = []

    @Slot(int, object)
    def activateLandmark(self, index, state):
        if not state:
            self.activeIndex = len(self.landmarkWidgets)
        else:
            self.activeIndex = index
        self.activeLandmarkChanged.emit(self.activeIndex)

    @Slot(int)
    def deleteLandmark(self, index):
        self.activateLandmark(index, False)
        self.landmarkDeleted.emit(index)


class SpecialButton(QLabel):
    def __init__(self):
        super(SpecialButton, self).__init__("")

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "QLabel:enabled { background: #ccc }" "QLabel { background: none }"
        )

    def wheelEvent(self, wheelEv):
        """
        Overrides QGraphicsView.wheelEvent()
        Make sure nothing happens when the user scrolls over this widget.
        """
        wheelEv.ignore()


class LandmarkLocationWidget(QWidget):
    # Signals
    activated = Signal(int, bool)
    deleted = Signal(int)

    def __init__(self):
        super(LandmarkLocationWidget, self).__init__()
        self._active = False
        self._font = QFont()
        self._font.setPointSize(10)

        self.indexLabel = QLabel()
        self.indexLabel.setMaximumWidth(10)
        self.indexLabel.setMinimumWidth(10)

        self.doneButton = QPushButton("Done")
        self.doneButton.setMaximumWidth(50)
        self.doneButton.setFont(self._font)
        self.doneButton.clicked.connect(self.doneButtonClicked)

        self.deleteButton = QPushButton("X")
        self.deleteButton.setMaximumWidth(15)
        self.deleteButton.setMinimumWidth(15)
        self.deleteButton.setMaximumHeight(15)
        self.deleteButton.setMinimumHeight(15)
        self.deleteButton.setFont(self._font)
        self.deleteButton.setVisible(False)
        self.deleteButton.clicked.connect(self.deleteButtonClicked)

        self.fixedButton = SpecialButton()
        self.fixedButton.setFont(self._font)
        self.movingButton = SpecialButton()
        self.movingButton.setFont(self._font)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(0)
        layout.addWidget(self.deleteButton, 0, 0)
        layout.addWidget(self.indexLabel, 0, 1)
        layout.addWidget(self.fixedButton, 0, 2)
        layout.addWidget(self.movingButton, 0, 3)
        layout.addWidget(self.doneButton, 0, 4)
        self.setLayout(layout)
        self._updateState()

    def setIndex(self, index):
        self.index = index
        self.indexLabel.setText(str(index + 1))

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self._updateState()

    def setLandmarkSet(self, points):
        self.setFixedLandmark(points[0])
        self.setMovingLandmark(points[1])

    def setFixedLandmark(self, landmark):
        if not landmark:
            return
        labelX = "%2.0f" % landmark[0]
        labelY = "%2.0f" % landmark[1]
        labelZ = "%2.0f" % landmark[2]
        self.fixedButton.setText(labelX + ", " + labelY + ", " + labelZ)

    def setMovingLandmark(self, landmark):
        if not landmark:
            return
        labelX = "%2.0f" % landmark[0]
        labelY = "%2.0f" % landmark[1]
        labelZ = "%2.0f" % landmark[2]
        self.movingButton.setText(labelX + ", " + labelY + ", " + labelZ)

    @Slot()
    def doneButtonClicked(self):
        self._active = not self._active
        self.activated.emit(self.index, self._active)
        self._updateState()

    @Slot()
    def deleteButtonClicked(self):
        self.deleted.emit(self.index)

    def _updateState(self):
        text = "Done" if self._active else "Edit"
        self.doneButton.setText(text)
        self.deleteButton.setVisible(self._active)
        self.indexLabel.setVisible(not self._active)
        self.fixedButton.setEnabled(self._active)
        self.movingButton.setEnabled(self._active)
