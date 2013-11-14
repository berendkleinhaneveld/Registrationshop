"""
PointsWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QScrollArea
from PySide.QtGui import QFont
from PySide.QtGui import QFrame
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from PySide.QtCore import Signal
from ui.widgets import Style


class PointsWidget(QWidget):
	"""
	PointsWidget
	"""

	activeLandmarkChanged = Signal(int)

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

		self.landmarkLocationsWidget = QWidget()
		Style.styleWidgetForTab(self.landmarkLocationsWidget)
		landmarkLocationsLayout = QGridLayout()
		landmarkLocationsLayout.setAlignment(Qt.AlignTop)
		landmarkLocationsLayout.setContentsMargins(0, 0, 0, 0)
		landmarkLocationsLayout.setSpacing(0)
		self.landmarkLocationsWidget.setLayout(landmarkLocationsLayout)
		self.scrollArea.setWidget(self.landmarkLocationsWidget)

		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.scrollArea)
		self.setLayout(layout)

	@Slot(list, list)
	def setPoints(self, points):
		self._clearLandmarkWidgets()
		layout = self.landmarkLocationsWidget.layout()
		for index in range(len(points)):
			landmarkWidget = LandmarkLocationWidget()
			landmarkWidget.setIndex(index)
			landmarkWidget.active = (index == self.activeIndex)
			landmarkWidget.activated.connect(self.landmarkIsActived)
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

	def landmarkIsActived(self, index, state):
		if not state:
			self.activeIndex = len(self.landmarkWidgets)
		else:
			self.activeIndex = index
		self.activeLandmarkChanged.emit(self.activeIndex)


class LandmarkLocationWidget(QWidget):
	# Signals
	activated = Signal(int, bool)
	removed = Signal(int)

	def __init__(self):
		super(LandmarkLocationWidget, self).__init__()
		self._active = False
		self._font = QFont()
		self._font.setPointSize(10)

		self.indexLabel = QLabel()
		self.indexLabel.setMaximumWidth(8)
		self.indexLabel.setMinimumWidth(8)

		self.doneButton = QPushButton("Done")
		self.doneButton.setMaximumWidth(50)
		self.doneButton.setFont(self._font)
		self.doneButton.clicked.connect(self.doneButtonClicked)

		self.fixedButton = QPushButton("")
		self.fixedButton.setFont(self._font)
		self.movingButton = QPushButton("")
		self.movingButton.setFont(self._font)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setHorizontalSpacing(4)
		layout.setVerticalSpacing(0)
		layout.addWidget(self.indexLabel, 0, 0)
		layout.addWidget(self.fixedButton, 0, 1)
		layout.addWidget(self.movingButton, 0, 2)
		layout.addWidget(self.doneButton, 0, 3)
		self.setLayout(layout)
		self._updateState()
		
	def setIndex(self, index):
		self.index = index
		self.indexLabel.setText(str(index+1))

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

	def _updateState(self):
		if self._active:
			self.doneButton.setText("Done")
		else:
			self.doneButton.setText("Edit")
		self.fixedButton.setEnabled(self._active)
		self.movingButton.setEnabled(self._active)
