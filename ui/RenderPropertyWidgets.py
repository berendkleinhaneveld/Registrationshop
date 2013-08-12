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
from PySide.QtGui import QSlider
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
	def __init__(self, renderController, parent=None):
		super(RenderPropWidget, self).__init__(parent=parent)

		# Three tabs: Visualization, data info and slices
		self.visParamTabWidget = RenderParameterWidget(renderController)
		self.dataInfoTabWidget = RenderInfoWidget()
		self.slicesTabWidget = RenderSlicerParamWidget(renderController)

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
		self.signal.connect(self.setFile)
		self.signal.connect(self.dataInfoTabWidget.setFile)

	def setLoadDataSlot(self, slot):
		"""
		The button is connected to the given slot. The slot action should load 
		a dataset from disk.

		:type slot: Slot
		"""
		self.loadDataButton.clicked.connect(slot)

	@Slot(basestring)
	def setFile(self, fileName):
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

	def __init__(self, renderController, parent=None):
		super(RenderParameterWidget, self).__init__(parent=parent)

		self.renderController = renderController
		self.renderController.dataChanged.connect(self.dataLoaded)
		self.renderController.volumePropertyChanged.connect(self.volumePropertyLoaded)

		self.visTypeLabel = QLabel("Visualization type")
		self.visTypeLabel.setMaximumHeight(20)

		self.visTypeCompoBox = QComboBox()
		for renderType in self.renderController.renderTypes:
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
			if self.renderController.volumeProperty is not None:
				self.renderController.volumeProperty.disconnect(SIGNAL("updatedTransferFunction"), self.transferFunctionChanged)

		# Get a new parameter widget from the render widget
		self.paramWidget = self.renderController.getParameterWidget()
		if sys.platform.startswith("darwin"):
			# default background of tabs on OSX is 237, 237, 237
			self.paramWidget.setStyleSheet("background: rgb(229, 229, 229)")
		self.scrollArea.setWidget(self.paramWidget)

		if self.renderController.volumeProperty is not None:
			self.renderController.volumeProperty.updatedTransferFunction.connect(self.transferFunctionChanged)

		self.visTypeCompoBox.setCurrentIndex(self.visTypeCompoBox.findText(self.renderController.renderType))

	@Slot(int)
	def renderTypeComboBoxChanged(self, index):
		"""
		Slot that changes the render type. Also updates parameters and makes
		sure that the renderWidget renders with the new renderType.
		:type index: any
		"""
		self.renderController.setRenderType(self.visTypeCompoBox.currentText())
		self.UpdateWidgetFromRenderWidget()
		self.renderController.updateVolumeProperty()

	@Slot()
	def dataLoaded(self):
		"""
		When data has been changed, the parameters have to be updated. This is because
		some of the parameters are dependent on properties of the data.
		"""
		pass
		# Get the correct widget from the RenderWidget
		# self.UpdateWidgetFromRenderWidget()

	def volumePropertyLoaded(self, volumeProperty):
		self.UpdateWidgetFromRenderWidget()

	@Slot()
	def transferFunctionChanged(self):
		"""
		Slot that can be used when a transfer function has changed so that
		the render will be updated afterwards.
		Should be called on valueChanged by the widgets from the parameter widget.
		"""
		self.renderController.updateVolumeProperty()

class RenderInfoWidget(QWidget):
	"""
	RenderInfoWidget shows information about the loaded dataset. Things like
	filenames, range of data values, size of data, etc.
	"""
	def __init__(self):
		super(RenderInfoWidget, self).__init__()

	@Slot(basestring)
	def setFile(self, fileName):
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

		nameText = name
		dimsText = "(" + str(dimensions[0]) + ", " + str(dimensions[1]) + ", " + str(dimensions[2]) + ")"
		voxsText = str(dimensions[0] * dimensions[1] * dimensions[2])
		rangText = "[" + str(minimum) + " : " + str(maximum) + "]"

		layout = self.layout()
		if not layout:
			# Create a new layout
			layout = QGridLayout()
			layout.setAlignment(Qt.AlignTop)

			# Create string representations
			nameField = QLabel("File name:")
			dimsField = QLabel("Dimensions:")
			voxsField = QLabel("Voxels:")
			rangField = QLabel("Range:")

			nameField.setAlignment(Qt.AlignRight)
			dimsField.setAlignment(Qt.AlignRight)
			voxsField.setAlignment(Qt.AlignRight)
			rangField.setAlignment(Qt.AlignRight)

			# Create 'dynamic' labels
			self.labelTitle = QLabel(nameText)
			self.labelDimensions = QLabel(dimsText)
			self.labelVoxels = QLabel(voxsText)
			self.labelRange = QLabel(rangText)

			layout.addWidget(nameField, 0, 0)
			layout.addWidget(dimsField, 1, 0)
			layout.addWidget(voxsField, 2, 0)
			layout.addWidget(rangField, 3, 0)

			layout.addWidget(self.labelTitle, 0, 1)
			layout.addWidget(self.labelDimensions, 1, 1)
			layout.addWidget(self.labelVoxels, 2, 1)
			layout.addWidget(self.labelRange, 3, 1)
			self.setLayout(layout)
		else:
			# Just update the text for the 'dynamic' labels
			self.labelTitle.setText(nameText)
			self.labelDimensions.setText(dimsText)
			self.labelVoxels.setText(voxsText)
			self.labelRange.setText(rangText)


class RenderSlicerParamWidget(QWidget):
	"""
	RenderSlicerParamWidget shows parameters with which slicers can be 
	manipulated.
	"""
	def __init__(self, renderController, parent=None):
		super(RenderSlicerParamWidget, self).__init__(parent=parent)

		self.renderController = renderController
		self.renderController.slicesChanged.connect(self.setSlices)

		self.slicesLabel = QLabel("Show slices for directions:")
		self.sliceLabelTexts = ["x", "y", "z"]
		self.sliceLabels = [QLabel(text) for text in self.sliceLabelTexts]
		self.sliceCheckBoxes = [QCheckBox() for i in range(3)]
		for index in range(3):
			self.sliceCheckBoxes[index].clicked.connect(self.checkBoxChanged)
			self.sliceLabels[index].setAlignment(Qt.AlignRight)
			self.sliceCheckBoxes[index].setEnabled(True)

		# Create a nice layout for the labels
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 3)
		layout.addWidget(self.slicesLabel, 0, 0, 1, -1)
		for index in range(3):
			layout.addWidget(self.sliceLabels[index], index+1, 0)
			layout.addWidget(self.sliceCheckBoxes[index], index+1, 1)
		self.setLayout(layout)

	@Slot()
	def checkBoxChanged(self):
		"""
		Callback function for the check boxes.
		"""
		for index in range(3):
			showCheckBox = self.sliceCheckBoxes[index].checkState() == Qt.Checked
			self.renderController.setSliceVisibility(index, showCheckBox)

	@Slot(object)
	def setSlices(self, slices):
		for index in range(len(slices)):
			checkBox = self.sliceCheckBoxes[index]
			checkBox.setChecked(slices[index])


class ResultPropWidget(QWidget):
	"""
	ResultPropWidget is a widget that is displayed under the result render
	widget. It contains tabs with some controls for interaction and 
	visualization of the combined / multi-volume render widget.
	"""
	def __init__(self, multiRenderController, parent=None):
		super(ResultPropWidget, self).__init__(parent=parent)

		# Two tabs: Visualization and Data info
		self.mixParamWidget = RenderMixerParamWidget(multiRenderController)
		self.registrationHistoryWidget = TransformationHistoryWidget()
		self.slicesTabWidget = RenderSlicerParamWidget(multiRenderController)

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
	def __init__(self, multiRenderController):
		super(RenderMixerParamWidget, self).__init__()
		self.multiRenderController = multiRenderController

		self.labelFixedOpacity = QLabel("Opacity of fixed volume")
		self.labelFixedOpacity.setVisible(False)
		self.labelMovingOpacity = QLabel("Opacity of moving volume")
		self.labelMovingOpacity.setVisible(False)

		self.sliderFixedOpacity = QSlider(Qt.Horizontal)
		self.sliderFixedOpacity.valueChanged.connect(self.fixedSliderChangedValue)
		self.sliderFixedOpacity.setVisible(False)
		self.sliderFixedOpacity.setValue(100)

		self.sliderMovingOpacity = QSlider(Qt.Horizontal)
		self.sliderMovingOpacity.valueChanged.connect(self.movingSliderChangedValue)
		self.sliderMovingOpacity.setValue(100)
		self.sliderMovingOpacity.setVisible(False)

		self.transformCheckBox = QCheckBox()
		self.transformCheckBox.clicked.connect(self.transformCheckBoxChanged)
		self.multiRenderController.fixedDataChanged.connect(self.dataChanged)
		self.multiRenderController.movingDataChanged.connect(self.dataChanged)
		self.transformCheckBox.setVisible(False)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.labelFixedOpacity, 0, 0)
		layout.addWidget(self.sliderFixedOpacity, 0, 1)
		layout.addWidget(self.labelMovingOpacity, 1, 0)
		layout.addWidget(self.sliderMovingOpacity, 1, 1)
		layout.addWidget(self.transformCheckBox, 2, 0)
		self.setLayout(layout)

	@Slot(object)
	def dataChanged(self):
		self.sliderFixedOpacity.setVisible(self.multiRenderController.fixedImageData is not None)
		self.sliderMovingOpacity.setVisible(self.multiRenderController.movingImageData is not None)
		self.labelFixedOpacity.setVisible(self.sliderFixedOpacity.isVisible())
		self.labelMovingOpacity.setVisible(self.sliderMovingOpacity.isVisible())
		self.transformCheckBox.setVisible(self.sliderMovingOpacity.isVisible())

	@Slot(int)
	def fixedSliderChangedValue(self, value):
		opacity = self.applyOpacityFunction(float(value) / 100.0)
		self.multiRenderController.setFixedOpacity(opacity)

	@Slot(int)
	def movingSliderChangedValue(self, value):
		opacity = self.applyOpacityFunction(float(value) / 100.0)
		self.multiRenderController.setMovingOpacity(opacity)

	@Slot(bool)
	def transformCheckBoxChanged(self):
		showTransformWidget = self.transformCheckBox.checkState() == Qt.Checked
		self.multiRenderController.setTransformBoxVisibility(showTransformWidget)

	def applyOpacityFunction(self, value):
		"""
		Make sure that the slider opacity values are not linear.
		"""
		return value * value * value

class TransformationHistoryWidget(QWidget):
	"""
	TransformationHistoryWidget shows a list of applied transformations.
	
	"""
	def __init__(self):
		super(TransformationHistoryWidget, self).__init__()

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("History of transformations."))
		self.setLayout(layout)
		
