"""
MultiVolumeVisualizationMix

:Authors:
	Berend Klein Haneveld
"""
from MultiVolumeVisualization import MultiVolumeVisualization
from MultiVolumeVisualization import CreateFunctionFromProperties
from MultiVolumeVisualization import CreateEmptyFunctions
from core.decorators import overrides
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QSlider
from PySide.QtGui import QComboBox
from PySide.QtCore import Qt
from vtk import vtkVolumeProperty


class MultiVolumeVisualizationMix(MultiVolumeVisualization):
	"""
	MultiVolumeVisualizationMix is a visualization that
	just mixes the two given volume properties together.
	"""
	def __init__(self):
		super(MultiVolumeVisualizationMix, self).__init__()

		self.fixedOpacity = 1.0
		self.movingOpacity = 1.0
		self.blendType = 0  # Default blend type
		self.fixedVisualization = None
		self.movingVisualization = None
		self.mapper = None

	@overrides(MultiVolumeVisualization)
	def setImageData(self, fixedImageData, movingImageData):
		self.fixedImageData = fixedImageData
		self.movingImageData = movingImageData

	@overrides(MultiVolumeVisualization)
	def setFixedVisualization(self, visualization):
		self.fixedVisualization = visualization
		self.fixedVolProp = self._createVolPropFromVis(self.fixedVisualization, self.fixedOpacity)

	@overrides(MultiVolumeVisualization)
	def setMovingVisualization(self, visualization):
		self.movingVisualization = visualization
		self.movingVolProp = self._createVolPropFromVis(self.movingVisualization, self.movingOpacity)

	@overrides(MultiVolumeVisualization)
	def getParameterWidget(self):
		self.labelFixedOpacity = QLabel("Opacity fixed data")
		self.labelMovingOpacity = QLabel("Opacity moving data")

		self.sliderFixedOpacity = QSlider(Qt.Horizontal)
		self.sliderFixedOpacity.setValue(pow(self.fixedOpacity, 1.0/3.0) * 100.0)

		self.sliderMovingOpacity = QSlider(Qt.Horizontal)
		self.sliderMovingOpacity.setValue(pow(self.movingOpacity, 1.0/3.0) * 100.0)

		self.blendTypeComboBox = QComboBox()
		self.blendTypeComboBox.addItem("Default blend")
		self.blendTypeComboBox.addItem("Other blend type")
		self.blendTypeComboBox.currentIndexChanged.connect(self.valueChanged)

		# Be sure to connect after the values are set...
		self.sliderFixedOpacity.valueChanged.connect(self.valueChanged)
		self.sliderMovingOpacity.valueChanged.connect(self.valueChanged)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.labelFixedOpacity, 0, 0)
		layout.addWidget(self.sliderFixedOpacity, 0, 1)
		layout.addWidget(self.labelMovingOpacity, 1, 0)
		layout.addWidget(self.sliderMovingOpacity, 1, 1)
		layout.addWidget(QLabel("Blend type"), 2, 0)
		layout.addWidget(self.blendTypeComboBox, 2, 1)

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(MultiVolumeVisualization)
	def valueChanged(self, value):
		"""
		This method is called when the value of one of the sliders / fields is
		adjusted. Argument value is unused. It is just there so that it can be
		connected to the signals of the interface elements.

		:type value: int
		"""
		self.fixedOpacity = self._applyOpacityFunction(float(self.sliderFixedOpacity.value()) / 100.0)
		self.movingOpacity = self._applyOpacityFunction(float(self.sliderMovingOpacity.value()) / 100.0)
		self.blendType = self.blendTypeComboBox.currentIndex()
		self.updateTransferFunctions()

	@overrides(MultiVolumeVisualization)
	def updateTransferFunctions(self):
		self.fixedVolProp = self._createVolPropFromVis(self.fixedVisualization, self.fixedOpacity)
		self.movingVolProp = self._createVolPropFromVis(self.movingVisualization, self.movingOpacity)

		if self.mapper:
			self.mapper.SetBlendType(self.blendType)

		self.updatedTransferFunction.emit()

	@overrides(MultiVolumeVisualization)
	def setMapper(self, mapper):
		self.mapper = mapper

	def _createVolPropFromVis(self, visualization, opacity):
		volProp = vtkVolumeProperty()
		if visualization:
			volProp.DeepCopy(visualization.volProp)
			opacityFunction = CreateFunctionFromProperties(opacity, volProp)
			volProp.SetScalarOpacity(opacityFunction)
		else:
			color, opacityFunction = CreateEmptyFunctions()
			volProp.SetColor(color)
			volProp.SetScalarOpacity(opacityFunction)

		return volProp

	def _applyOpacityFunction(self, value):
		"""
		Make sure that the slider opacity values are not linear.
		"""
		return value * value * value
