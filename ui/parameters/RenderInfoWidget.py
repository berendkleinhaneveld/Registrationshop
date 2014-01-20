"""
RenderInfoWidget

:Authors:
	Berend Klein Haneveld
"""

import os
from PySide.QtGui import QWidget
from ui.widgets import Style
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QPushButton
from PySide.QtGui import QDialog
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QGroupBox
from PySide.QtGui import QScrollArea
from PySide.QtGui import QFrame
from PySide.QtCore import Slot
from PySide.QtCore import Qt
from core.project import ProjectController
from core.data import DataReader
from core.data.DataAnalyzer import DataAnalyzer
from ui.widgets.histogram import Histogram
from ui.widgets.histogram import HistogramWidget


class RenderInfoWidget(QWidget):
	"""
	RenderInfoWidget shows information about the loaded dataset. Things like
	filenames, range of data values, size of data, etc.
	"""
	def __init__(self):
		super(RenderInfoWidget, self).__init__()

		self.scrollArea = QScrollArea()
		self.scrollArea.setFrameShape(QFrame.NoFrame)
		self.scrollArea.setAutoFillBackground(False)
		self.scrollArea.setAttribute(Qt.WA_TranslucentBackground)
		self.scrollArea.setWidgetResizable(True)

		Style.styleWidgetForTab(self)
		Style.styleWidgetForTab(self.scrollArea)

	@Slot(basestring)
	def setFile(self, fileName):
		"""
		Slot that reads properties of the dataset and displays them in a few widgets.
		"""
		if fileName is None:
			return

		self.fileName = fileName

		# Read info from dataset
		# TODO: read out the real world dimensions in inch or cm
		# TODO: scalar type (int, float, short, etc.)
		imageReader = DataReader()
		imageData = imageReader.GetImageData(fileName)

		directory, name = os.path.split(fileName)
		dimensions = imageData.GetDimensions()
		minimum, maximum = imageData.GetScalarRange()
		scalarType = imageData.GetScalarTypeAsString()

		bins = DataAnalyzer.histogramForData(imageData, 256)

		self.histogram = Histogram()
		self.histogram.bins = bins
		self.histogram.enabled = True

		self.histogramWidget = HistogramWidget()
		self.histogramWidget.setMinimumHeight(100)
		self.histogramWidget.setHistogram(self.histogram)
		self.histogramWidget.setAxeMode(bottom=HistogramWidget.AxeClear,
			left=HistogramWidget.AxeLog)
		Style.styleWidgetForTab(self.histogramWidget)

		nameText = name
		dimsText = "(" + str(dimensions[0]) + ", " + str(dimensions[1]) + ", " + str(dimensions[2]) + ")"
		voxsText = str(dimensions[0] * dimensions[1] * dimensions[2])
		rangText = "[" + str(minimum) + " : " + str(maximum) + "]"
		typeText = scalarType

		layout = self.layout()
		if not layout:
			# Create a new layout
			layout = QGridLayout()
			layout.setAlignment(Qt.AlignTop)

			# Create string representations
			nameLabels = []
			nameLabels.append(QLabel("File name:"))
			nameLabels.append(QLabel("Dimensions:"))
			nameLabels.append(QLabel("Voxels:"))
			nameLabels.append(QLabel("Range:"))
			nameLabels.append(QLabel("Data type:"))

			for label in nameLabels:
				label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

			# Create 'dynamic' labels
			self.labelTitle = QLabel(nameText)
			self.labelDimensions = QLabel(dimsText)
			self.labelVoxels = QLabel(voxsText)
			self.labelRange = QLabel(rangText)
			self.labelType = QLabel(typeText)

			index = 0
			for label in nameLabels:
				layout.addWidget(label, index, 0)
				index += 1

			layout.addWidget(self.labelTitle, 0, 1)
			layout.addWidget(self.labelDimensions, 1, 1)
			layout.addWidget(self.labelVoxels, 2, 1)
			layout.addWidget(self.labelRange, 3, 1)
			layout.addWidget(self.labelType, 4, 1)
			layout.addWidget(self.histogramWidget, 5, 0, 1, 2)

			widget = QWidget()
			widget.setLayout(layout)
			Style.styleWidgetForTab(widget)
			self.scrollArea.setWidget(widget)

			scrollLayout = QGridLayout()
			scrollLayout.setSpacing(0)
			scrollLayout.setContentsMargins(0, 0, 0, 0)
			scrollLayout.addWidget(self.scrollArea)
			self.setLayout(scrollLayout)
		else:
			# Just update the text for the 'dynamic' labels
			self.labelTitle.setText(nameText)
			self.labelDimensions.setText(dimsText)
			self.labelVoxels.setText(voxsText)
			self.labelRange.setText(rangText)
			self.labelType.setText(typeText)
