"""
LandmarkWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QPushButton
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from PySide.QtCore import Signal
from histogram import TrackingHistogramWidget
from histogram import Histogram
from histogram import HistogramWidget


class LandmarkWidget(QWidget):
	"""
	LandmarkWidget
	"""

	pickedPosition = Signal()

	def __init__(self):
		super(LandmarkWidget, self).__init__()

		self.histogramWidget = TrackingHistogramWidget()
		self.button = QPushButton("Pick current landmark position")
		self.button.clicked.connect(self.applyButtonClicked)
		self.button.setVisible(False)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Ray profile:"))
		layout.addWidget(self.histogramWidget)
		layout.addWidget(self.button)

		self.setLayout(layout)

	def setSamples(self, samples, scope=None):
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
