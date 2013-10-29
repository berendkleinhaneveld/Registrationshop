"""
LandmarkWidget

:Authors:
	Berend Klein Haneveld
"""
import sys
from PySide.QtGui import *
from PySide.QtCore import *
from histogram import TrackingHistogramWidget
from histogram import Histogram
from histogram import HistogramWidget


class LandmarkWidget(QWidget):
	"""
	LandmarkWidget
	"""

	def __init__(self):
		super(LandmarkWidget, self).__init__()

		self.histogramWidget = TrackingHistogramWidget()
		# if sys.platform.startswith("darwin"):
			# self.histogramWidget.setBackgroundBrush(QBrush(QColor(229, 229, 229)))

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Landmark widget"))
		layout.addWidget(self.histogramWidget)

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
