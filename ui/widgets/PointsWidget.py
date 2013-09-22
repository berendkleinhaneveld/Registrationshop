"""
PointsWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QPushButton
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from PySide.QtCore import Signal


class PointsWidget(QWidget):
	"""
	PointsWidget
	"""

	activeLandmarkChanged = Signal(int)

	def __init__(self):
		super(PointsWidget, self).__init__()

		self.landmarkWidgets = []
		self.activeIndex = 0

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setVerticalSpacing(0)
		layout.setHorizontalSpacing(0)
		self.setLayout(layout)

	@Slot(list, list)
	def setPoints(self, fixed, moving):
		self._clearLandmarkWidgets()
		layout = self.layout()
		for index in range(max(len(fixed), len(moving))):
			landmarkWidget = LandmarkWidget()
			landmarkWidget.setIndex(index)
			landmarkWidget.active = (index == self.activeIndex)
			landmarkWidget.activated.connect(self.landmarkIsActived)
			if index < len(fixed):
				landmarkWidget.setFixedLandmark(fixed[index])
			if index < len(moving):
				landmarkWidget.setMovingLandmark(moving[index])
			layout.addWidget(landmarkWidget, index, 0)
			self.landmarkWidgets.append(landmarkWidget)

	def _clearLandmarkWidgets(self):
		layout = self.layout()
		for widget in self.landmarkWidgets:
			layout.removeWidget(widget)
			widget.deleteLater()
		self.landmarkWidgets = []

	def landmarkIsActived(self, index, state):
		if not state:
			self.activeIndex = len(self.landmarkWidgets)
		else:
			self.activeIndex = index
		self.activeLandmarkChanged.emit(self.activeIndex)


class LandmarkWidget(QWidget):
	# Signals
	activated = Signal(int, bool)
	removed = Signal(int)

	def __init__(self):
		super(LandmarkWidget, self).__init__()
		self._active = False

		self.indexLabel = QLabel()
		self.indexLabel.setMaximumWidth(15)
		self.indexLabel.setMinimumWidth(15)

		self.doneButton = QPushButton("Done")
		self.doneButton.setMaximumWidth(80)
		self.doneButton.setMinimumWidth(80)
		self.doneButton.clicked.connect(self.doneButtonClicked)

		self.fixedButton = QPushButton("")
		self.movingButton = QPushButton("")

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setVerticalSpacing(0)
		layout.setColumnStretch(1, 1)
		layout.setColumnStretch(2, 1)
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

	def setFixedLandmark(self, landmark):
		labelX = "%2.0f" % landmark[0]
		labelY = "%2.0f" % landmark[1]
		labelZ = "%2.0f" % landmark[2]
		self.fixedButton.setText(labelX + ", " + labelY + ", " + labelZ)

	def setMovingLandmark(self, landmark):
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
