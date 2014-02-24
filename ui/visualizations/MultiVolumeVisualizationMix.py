"""
MultiVolumeVisualizationMix

:Authors:
	Berend Klein Haneveld
"""
from MultiVolumeVisualization import MultiVolumeVisualization
from MultiVolumeVisualization import CreateFunctionFromProperties
from MultiVolumeVisualization import CreateEmptyFunctions
from VolumeVisualization import VisualizationTypeSimple
from core.decorators import overrides
from PySide.QtGui import QGroupBox
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
		self.sliderFixedOpacity.setDisabled(self.fixedVisualization.visualizationType != VisualizationTypeSimple)
		self.labelFixedOpacity.setDisabled(self.fixedVisualization.visualizationType != VisualizationTypeSimple)

	@overrides(MultiVolumeVisualization)
	def setMovingVisualization(self, visualization):
		self.movingVisualization = visualization
		self.movingVolProp = self._createVolPropFromVis(self.movingVisualization, self.movingOpacity)
		self.sliderMovingOpacity.setDisabled(self.movingVisualization.visualizationType != VisualizationTypeSimple)
		self.labelMovingOpacity.setDisabled(self.movingVisualization.visualizationType != VisualizationTypeSimple)

	@overrides(MultiVolumeVisualization)
	def getParameterWidget(self):
		self.labelFixedOpacity = QLabel("Fixed:")
		self.labelFixedOpacity.setAlignment(Qt.AlignRight)
		self.labelMovingOpacity = QLabel("Moving:")
		self.labelMovingOpacity.setAlignment(Qt.AlignRight)

		self.sliderFixedOpacity = QSlider(Qt.Horizontal)
		self.sliderFixedOpacity.setValue(pow(self.fixedOpacity, 1.0/3.0) * 100.0)

		self.sliderMovingOpacity = QSlider(Qt.Horizontal)
		self.sliderMovingOpacity.setValue(pow(self.movingOpacity, 1.0/3.0) * 100.0)

		self.blendTypeComboBox = QComboBox()
		self.blendTypeComboBox.addItem("Default additive blend")
		self.blendTypeComboBox.addItem("Difference blend")
		self.blendTypeComboBox.currentIndexChanged.connect(self.valueChanged)

		# Be sure to connect after the values are set...
		self.sliderFixedOpacity.valueChanged.connect(self.valueChanged)
		self.sliderMovingOpacity.valueChanged.connect(self.valueChanged)

		groupLayout = QGridLayout()
		groupLayout.setAlignment(Qt.AlignTop)
		groupLayout.addWidget(self.labelFixedOpacity, 0, 0)
		groupLayout.addWidget(self.sliderFixedOpacity, 0, 1)
		groupLayout.addWidget(self.labelMovingOpacity, 1, 0)
		groupLayout.addWidget(self.sliderMovingOpacity, 1, 1)

		groupBox = QGroupBox()
		groupBox.setTitle("Opacity:")
		groupBox.setLayout(groupLayout)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(groupBox)

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
		self.fixedOpacity = applyOpacityFunction(float(self.sliderFixedOpacity.value()) / 100.0)
		self.movingOpacity = applyOpacityFunction(float(self.sliderMovingOpacity.value()) / 100.0)
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


def applyOpacityFunction(value):
	"""
	Make sure that the slider opacity values are not linear.
	"""
	return value * value * value
