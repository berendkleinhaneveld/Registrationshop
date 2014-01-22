"""
LandmarkWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QPushButton
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QTextEdit
from PySide.QtGui import QFrame
from PySide.QtGui import QComboBox
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from PySide.QtCore import Signal
from histogram import TrackingHistogramWidget
from histogram import Histogram
from histogram import HistogramWidget
from ui.transformations.LandmarkTransformationTool import TwoStepType
from ui.transformations.LandmarkTransformationTool import SurfaceType


class LandmarkWidget(QWidget):

	landmarkTypeChanged = Signal(object)

	def __init__(self):
		super(LandmarkWidget, self).__init__()
		
		self.typeLabel = QLabel("Picker type:")
		self.typeCombo = QComboBox()
		self.typeCombo.addItem("Surface")
		self.typeCombo.addItem("Two step")
		self.typeCombo.currentIndexChanged.connect(self.comboboxChanged)

		self.surfaceWidget = SurfaceLandmarkWidget()
		self.twoStepWidget = TwoStepLandmarkWidget()
		self.surfaceWidget.setHidden(True)
		self.twoStepWidget.setHidden(True)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.typeLabel, 0, 0)
		layout.addWidget(self.typeCombo, 0, 1)
		layout.addWidget(self.surfaceWidget, 1, 0, 1, 2)
		layout.addWidget(self.twoStepWidget, 2, 0, 1, 2)
		self.setLayout(layout)

		self.update()

	def update(self):
		idx = self.typeCombo.currentIndex()
		if idx == 0:
			self.surfaceWidget.setHidden(False)
			self.twoStepWidget.setHidden(True)
			self.landmarkType = SurfaceType
		elif idx == 1:
			self.surfaceWidget.setHidden(True)
			self.twoStepWidget.setHidden(False)
			self.landmarkType = TwoStepType

	@Slot(int)
	def comboboxChanged(self, index):
		self.update()
		self.landmarkTypeChanged.emit(self)


class SurfaceLandmarkWidget(QWidget):
	def __init__(self):
		super(SurfaceLandmarkWidget, self).__init__()
		
		self.textFrame = QTextEdit("<p>Hold your mouse over the volume "
			"to move the locator. To create a landmark, press 'Space'.</p>"
			"<p>When you want to proceed to the following landmark, "
			"click the 'Done' button behind the landmark pair in the "
			"center of the window.</p>")
		self.textFrame.setReadOnly(True)
		self.textFrame.setFrameShape(QFrame.NoFrame)
		self.textFrame.setAutoFillBackground(False)
		self.textFrame.setAttribute(Qt.WA_TranslucentBackground)
		self.textFrame.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.textFrame.setStyleSheet("background: #aaa")

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.textFrame)
		self.setLayout(layout)


class TwoStepLandmarkWidget(QWidget):
	"""
	TwoStepLandmarkWidget
	"""

	pickedPosition = Signal()

	def __init__(self):
		super(TwoStepLandmarkWidget, self).__init__()

		self.textFrame = QTextEdit("<p>Place your mouse over the desired "
			"landmark point. Press 'Space' to shoot a ray through the volume. "
			"Move the volume around and move the mouse to move the locator. "
			"Press 'Space' again to define the final place of the landmark.</p>"
			"<p>You can also use the ray profile to define the landmark's location.</p>")
		self.textFrame.setReadOnly(True)
		self.textFrame.setFrameShape(QFrame.NoFrame)
		self.textFrame.setAutoFillBackground(False)
		self.textFrame.setAttribute(Qt.WA_TranslucentBackground)
		self.textFrame.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.textFrame.setStyleSheet("background: #aaa")

		self.histogramWidget = TrackingHistogramWidget()
		self.histogramWidget.setMinimumHeight(100)
		self.histogramWidget.setVisible(False)

		self.button = QPushButton("Pick current landmark position")
		self.button.clicked.connect(self.applyButtonClicked)
		self.button.setVisible(False)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.textFrame)
		layout.addWidget(self.histogramWidget)
		layout.addWidget(self.button)
		self.setLayout(layout)

	def setSamples(self, samples, scope=None):
		self.textFrame.setVisible(False)
		self.histogramWidget.setVisible(True)

		self.histogram = Histogram()
		self.histogram.bins = samples
		
		if scope:
			self.histogram.minY = scope[0]
			self.histogram.maxY = scope[1]
			self.histogram.enabled = True

		self.histogramWidget.setHistogram(self.histogram)
		self.histogramWidget.setAxeMode(left=HistogramWidget.AxeNormal)
		self.histogramWidget.nodeItem.tracking = True
		self.button.setVisible(True)

	@Slot()
	def applyButtonClicked(self):
		self.pickedPosition.emit()

	@Slot()
	def pickedLocation(self, location):
		self.histogramWidget.nodeItem.tracking = False
		self.button.setVisible(False)
