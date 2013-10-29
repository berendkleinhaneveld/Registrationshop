"""
MultiVolumeVisualizationMIP

:Authors:
	Berend Klein Haneveld
"""
from MultiVolumeVisualization import MultiVolumeVisualization
from MultiVolumeVisualization import CreateEmptyFunctions
from MultiVolumeVisualization import CreateRangeFunctions
from core.decorators import overrides
from PySide.QtGui import QLabel
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QSlider
from PySide.QtCore import Qt
from vtk import vtkVolumeProperty


class MultiVolumeVisualizationMIP(MultiVolumeVisualization):
	"""
	MultiVolumeVisualizationMIP is a visualization that shows
	MIP visualizations of both datasets and adds them
	together. It uses complementary colors for the datasets
	so that the visualization is white in the spots where
	they are the same.
	"""
	def __init__(self):
		super(MultiVolumeVisualizationMIP, self).__init__()

		self.fixedHue = 0

	@overrides(MultiVolumeVisualization)
	def getParameterWidget(self):
		self.hueSlider = QSlider(Qt.Horizontal)
		self.hueSlider.setMaximum(360)
		self.hueSlider.setValue(self.fixedHue)
		self.hueSlider.valueChanged.connect(self.valueChanged)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Base hue"), 0, 0)
		layout.addWidget(self.hueSlider, 0, 1)

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(MultiVolumeVisualization)
	def setImageData(self, fixedImageData, movingImageData):
		self.fixedImageData = fixedImageData
		self.movingImageData = movingImageData

	@overrides(MultiVolumeVisualization)
	def updateTransferFunctions(self):
		self.fixedVolProp = self._createVolPropFromImageData(self.fixedImageData)
		self.movingVolProp = self._createVolPropFromImageData(self.movingImageData)

		self.updatedTransferFunction.emit()

	@overrides(MultiVolumeVisualization)
	def valueChanged(self, value):
		self.fixedHue = self.hueSlider.value()
		self.updateTransferFunctions()

	@overrides(MultiVolumeVisualization)
	def setMapper(self, mapper):
		self.mapper = mapper

	def _createVolPropFromImageData(self, imageData):
		volProp = vtkVolumeProperty()
		if imageData is not None:
			color, opacityFunction = CreateRangeFunctions(imageData)
		else:
			color, opacityFunction = CreateEmptyFunctions()
		volProp.SetColor(color)
		volProp.SetScalarOpacity(opacityFunction)

		return volProp
