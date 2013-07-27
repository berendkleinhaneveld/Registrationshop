"""
RenderPropertyWidgets

Holds the following class definitions:

* RenderPropWidget
* RenderParameterWidget
* RenderInfoWidget
* ResultPropWidget

:Authors:
	Berend Klein Haneveld

Notes:
There is a RenderWidget object and a RenderPropWidget.
The RenderWidget will render the dataset defined by the project (fixed or 
moving)
The RenderPropWidget will hold the parameters and properties for the dataset.

Steps:
User loads file.
ProjectController changes filename.
RenderWidget loads the dataset. (But needs its parameters from RPW)
(RenderPropWidget is a container for the RenderParameterWidget and the 
RenderInfoWidget.)
RenderParameterWidget gets the parameter widget from RenderWidget.
RenderWidget gets the parameter widget from its VolumeProperty.
RenderInfoWidget also gets the parameters from RenderWidget.
"""

import sys, os
from PySide.QtGui import QWidget
from PySide.QtGui import QPushButton
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QGridLayout
from PySide.QtGui import QTabWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QComboBox
from PySide.QtGui import QScrollArea
from PySide.QtGui import QFrame
from PySide.QtGui import QCheckBox
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from PySide.QtCore import SIGNAL
from core.data.DataReader import DataReader

class RenderPropWidget(QWidget):
	"""
	RenderPropWidget is a widget that is displayed under the render widgets. It
	contains a tabwidget in which information of the data can be displayed and 
	in which visualization parameters can be shown. One of the tabs is a 
	RenderParameterWidget object.
	"""
	def __init__(self, renderWidget, parent=None):
		super(RenderPropWidget, self).__init__(parent=parent)

		# Three tabs: Visualization, data info and slices
		self.visParamTabWidget = RenderParameterWidget(renderWidget)
		self.dataInfoTabWidget = RenderInfoWidget()
		self.slicesTabWidget = RenderSlicerParamWidget(renderWidget)

		# Create the load dataset widget
		self.loadDataWidget = QWidget()
		self.loadDataButton = QPushButton()
		self.loadDataButton.setText("Load a dataset")

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.loadDataButton)
		self.loadDataWidget.setLayout(layout)

		# Create the tab widget
		self.tabWidget = QTabWidget()
		self.tabWidget.addTab(self.visParamTabWidget, "Visualization")
		self.tabWidget.addTab(self.dataInfoTabWidget, "Data info")
		self.tabWidget.addTab(self.slicesTabWidget, "Slices")

		layout = QVBoxLayout()
		layout.addWidget(self.loadDataWidget)	
		self.setLayout(layout)

	def setFileChangedSignal(self, signal):
		"""
		:param signal: Signal that is connected to some file-loading slots. 
		:type signal: SIGNAL
		"""
		self.signal = signal
		self.signal.connect(self.loadFile)
		self.signal.connect(self.dataInfoTabWidget.loadFile)

	def setLoadDataSlot(self, slot):
		"""
		The button is connected to the given slot. The slot action should load 
		a dataset from disk.

		:type slot: Slot
		"""
		self.loadDataButton.clicked.connect(slot)

	@Slot(basestring)
	def loadFile(self, fileName):
		"""
		When a file is loaded, the 'load data' button is removed from the widget
		and the actual tabs with parameters are put on screen.
		"""
		layout = self.layout()
		if fileName is None:
			if layout.indexOf(self.tabWidget) != -1:
				# Remove the parameter widgets
				layout.removeWidget(self.tabWidget)
				self.tabWidget.setParent(None)
				# Show the load data button
				layout.addWidget(self.loadDataWidget)
				self.setLayout(layout)
		else:
			if layout.indexOf(self.loadDataWidget) != -1:
				# Remove the load data button
				layout.removeWidget(self.loadDataWidget)
				self.loadDataWidget.setParent(None)
				# Add the parameter widgets
				layout.addWidget(self.tabWidget)
				self.setLayout(layout)

class RenderParameterWidget(QWidget):
	"""
	RenderParameterWidget is a widget that is shown in the render property 
	widget. It holds a combo box with which different visualizations can be 
	chosen. Beneath the combo box it displays a widget in a scroll view that 
	contains widgets with which parameters of the visualization can be adjusted.
	"""
	def __init__(self, renderWidget, parent=None):
		super(RenderParameterWidget, self).__init__(parent=parent)

		self.renderWidget = renderWidget
		self.renderWidget.loadedData.connect(self.dataLoaded)

		self.visTypeLabel = QLabel("Visualization type")
		self.visTypeLabel.setMaximumHeight(20)

		self.visTypeCompoBox = QComboBox()
		for renderType in self.renderWidget.renderTypes:
			self.visTypeCompoBox.addItem(renderType)

		self.paramWidget = None

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.visTypeLabel)
		layout.addWidget(self.visTypeCompoBox)
		self.setLayout(layout)

		self.scrollArea = QScrollArea()
		self.scrollArea.setFrameShape(QFrame.NoFrame)
		self.scrollArea.setAutoFillBackground(False)
		self.scrollArea.setAttribute(Qt.WA_TranslucentBackground)
		self.scrollArea.setWidgetResizable(True)

		self.visTypeCompoBox.currentIndexChanged.connect(self.renderTypeComboBoxChanged)

	def UpdateWidgetFromRenderWidget(self):
		"""
		Update the parameter widget with a widget from the render widget.
		"""
		# Add the scroll area for the parameter widget if it is not there yet
		layout = self.layout()
		if layout.indexOf(self.scrollArea) == -1:
			layout.addWidget(self.scrollArea)
			self.setLayout(layout)

		# Clear the previous parameter widget
		if self.paramWidget is not None:
			self.paramWidget.setParent(None)
			self.renderWidget.renderVolumeProperty.disconnect(SIGNAL("updatedTransferFunction"), self.transferFunctionChanged)

		# Get a new parameter widget from the render widget
		self.paramWidget = self.renderWidget.GetParameterWidget()
		if sys.platform.startswith("darwin"):
			# default background of tabs on OSX is 237, 237, 237
			self.paramWidget.setStyleSheet("background: rgb(229, 229, 229)")
		self.scrollArea.setWidget(self.paramWidget)
		self.renderWidget.renderVolumeProperty.updatedTransferFunction.connect(self.transferFunctionChanged)

	@Slot(int)
	def renderTypeComboBoxChanged(self, index):
		"""
		Slot that changes the render type. Also updates parameters and makes
		sure that the renderWidget renders with the new renderType.
		:type index: any
		"""
		self.renderWidget.SetRenderType(self.visTypeCompoBox.currentText())
		self.UpdateWidgetFromRenderWidget()
		self.renderWidget.Update()

	@Slot()
	def dataLoaded(self):
		"""
		When data has been changed, the parameters have to be updated. This is because
		some of the parameters are dependent on properties of the data.
		"""
		# Get the correct widget from the RenderWidget
		self.UpdateWidgetFromRenderWidget()

	@Slot()
	def transferFunctionChanged(self):
		"""
		Slot that can be used when a transfer function has changed so that
		the render will be updated afterwards.
		"""
		self.renderWidget.Update()

class RenderInfoWidget(QWidget):
	"""
	RenderInfoWidget shows information about the loaded dataset. Things like
	filenames, range of data values, size of data, etc.
	"""
	def __init__(self):
		super(RenderInfoWidget, self).__init__()

	@Slot(basestring)
	def loadFile(self, fileName):
		"""
		Slot that reads properties of the dataset and displays them in a few widgets.
		"""
		if fileName is None:
			return

		# Read info from dataset
		# TODO: read out the real world dimensions in inch or cm
		# TODO: scalar type (int, float, short, etc.)
		imageReader = DataReader()
		imageData = imageReader.GetImageData(fileName)

		directory, name = os.path.split(fileName)
		dimensions = imageData.GetDimensions()
		minimum, maximum = imageData.GetScalarRange()

		# Create string representations
		nameField = QLabel("File name:")
		dimsField = QLabel("Dimensions:")
		voxsField = QLabel("Voxels:")
		rangField = QLabel("Range:")

		nameField.setAlignment(Qt.AlignRight)
		dimsField.setAlignment(Qt.AlignRight)
		voxsField.setAlignment(Qt.AlignRight)
		rangField.setAlignment(Qt.AlignRight)

		nameText = name
		dimsText = "(" + str(dimensions[0]) + ", " + str(dimensions[1]) + ", " + str(dimensions[2]) + ")"
		voxsText = str(dimensions[0] * dimensions[1] * dimensions[2])
		rangText = "[" + str(minimum) + " : " + str(maximum) + "]"

		# Create labels
		labelTitle = QLabel(nameText)
		labelDimensions = QLabel(dimsText)
		labelVoxels = QLabel(voxsText)
		labelRange = QLabel(rangText)

		# Create a nice layout for the labels
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(nameField, 0, 0)
		layout.addWidget(dimsField, 1, 0)
		layout.addWidget(voxsField, 2, 0)
		layout.addWidget(rangField, 3, 0)

		layout.addWidget(labelTitle, 0, 1)
		layout.addWidget(labelDimensions, 1, 1)
		layout.addWidget(labelVoxels, 2, 1)
		layout.addWidget(labelRange, 3, 1)
		self.setLayout(layout)

class RenderSlicerParamWidget(QWidget):
	"""
	RenderSlicerParamWidget shows parameters with which slicers can be 
	manipulated.
	"""
	def __init__(self, renderWidget, parent=None):
		super(RenderSlicerParamWidget, self).__init__(parent=parent)

		self.renderWidget = renderWidget
		self.renderWidget.loadedData.connect(self.dataLoaded)

	@Slot()
	def checkBoxChanged(self):
		"""
		Callback function for the check boxes.
		"""
		for index in range(3):
			showCheckBox = self.sliceCheckBoxes[index].checkState() == Qt.Checked
			self.renderWidget.showSlice(index, showCheckBox)

		self.renderWidget.Update()

	@Slot()
	def dataLoaded(self):
		"""
		Slot for when data is loaded into the corresponding render widget.
		Creates layout with labels and check boxes.
		"""
		self.slicesLabel = QLabel("Show slices for directions:")
		self.sliceLabelTexts = ["x", "y", "z"]
		self.sliceLabels = [QLabel(text) for text in self.sliceLabelTexts]
		self.sliceCheckBoxes = [QCheckBox() for i in range(3)]
		for index in range(3):
			self.sliceCheckBoxes[index].clicked.connect(self.checkBoxChanged)
			self.sliceLabels[index].setAlignment(Qt.AlignRight)

		# Create a nice layout for the labels
		layout = QGridLayout()
		self.setLayout(layout)
		layout.setAlignment(Qt.AlignTop)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 3)
		layout.addWidget(self.slicesLabel, 0, 0, 1, -1)
		for index in range(3):
			layout.addWidget(self.sliceLabels[index], index+1, 0)
			layout.addWidget(self.sliceCheckBoxes[index], index+1, 1)

class ResultPropWidget(QWidget):
	"""
	ResultPropWidget is a widget that is displayed under the result render
	widget. It contains tabs with some controls for interaction and 
	visualization of the combined / multi-volume render widget.
	"""
	def __init__(self, renderWidget, parent=None):
		super(ResultPropWidget, self).__init__(parent=parent)

		# Two tabs: Visualization and Data info
		self.mixParamWidget = RenderMixerParamWidget(renderWidget)
		self.registrationHistoryWidget = QWidget()
		self.slicesTabWidget = RenderSlicerParamWidget(renderWidget)

		# Create the tab widget
		self.tabWidget = QTabWidget()
		self.tabWidget.addTab(self.mixParamWidget, "Mix")
		self.tabWidget.addTab(self.registrationHistoryWidget, "History")
		self.tabWidget.addTab(self.slicesTabWidget, "Slices")

		layout = QVBoxLayout()
		self.setLayout(layout)
		layout.addWidget(self.tabWidget)

class RenderMixerParamWidget(QWidget):
	"""
	RenderMixerParamWidget is a widget that shows some mixer controls
	for the multi-volume render widget.
	"""
	def __init__(self, multiRenderWidget):
		super(RenderMixerParamWidget, self).__init__()
		self.multiRenderWidget = multiRenderWidget

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Hello world"))
		self.setLayout(layout)
		
