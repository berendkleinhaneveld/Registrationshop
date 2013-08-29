"""
MultiVolumeVisualization

:Authors:
	Berend Klein Haneveld
"""

from core.decorators import overrides
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QSlider
from PySide.QtGui import QWidget
from PySide.QtCore import Qt
from PySide.QtCore import QObject
from PySide.QtCore import Signal
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from vtk import vtkMath

# Define render types for multi render
MultiVisualizationTypeMix = "Default mix"
MultiVisualizationTypeMIP = "Combined MIP"
MultiVisualizationTypeMIDA = "Single MIDA"


class MultiVolumeVisualizationFactory(object):
	"""
	MultiVolumeVisualizationFactory can be used to make
	MultiVolumeVisualization objects.
	"""
	def __init__(self):
		super(MultiVolumeVisualizationFactory, self).__init__()

	@classmethod
	def CreateProperty(cls, visualizationType):
		if visualizationType == MultiVisualizationTypeMix:
			return MixMultiVolumeVisualization()
		elif visualizationType == MultiVisualizationTypeMIP:
			return MIPMultiVolumeVisualization()
		elif visualizationType == MultiVisualizationTypeMIDA:
			return MIDAMultiVolumeVisualization()
		else:
			print "Warning: unknown visualizationType given:", visualizationType
			return MixMultiVolumeVisualization()
			# assert False


# Volume Properties

class MultiVolumeVisualization(QObject):
	"""
	MultiVolumeVisualization is the superclass for all multi
	volume visualizations.
	"""

	updatedTransferFunction = Signal()

	def __init__(self):
		super(MultiVolumeVisualization, self).__init__()

		self.fixedVolProp = None
		self.movingVolProp = None

	def getParameterWidget(self):
		raise NotImplementedError()

	def setImageData(self, fixedImageData, movingImageData):
		pass

	def updateTransferFunctions(self):
		raise NotImplementedError()

	def valueChanged(self, value):
		raise NotImplementedError()

	def configureMapper(self, mapper):
		raise NotImplementedError()

	def setFixedVisualization(self, visualization):
		"""
		:type visualization: VolumeVisualization
		"""
		pass

	def setMovingVisualization(self, visualization):
		"""
		:type visualization: VolumeVisualization
		"""
		pass


class MixMultiVolumeVisualization(MultiVolumeVisualization):
	"""
	MixMultiVolumeVisualization is a visualization that
	just mixes the two given volume properties together.
	"""
	def __init__(self):
		super(MixMultiVolumeVisualization, self).__init__()

		self.fixedOpacity = 1.0
		self.movingOpacity = 1.0

		self.fixedVisualization = None
		self.movingVisualization = None

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
		self.labelFixedOpacity = QLabel("Opacity of fixed volume")
		self.labelMovingOpacity = QLabel("Opacity of moving volume")

		self.sliderFixedOpacity = QSlider(Qt.Horizontal)
		self.sliderFixedOpacity.setValue(pow(self.fixedOpacity, 1.0/3.0) * 100.0)

		self.sliderMovingOpacity = QSlider(Qt.Horizontal)
		self.sliderMovingOpacity.setValue(pow(self.movingOpacity, 1.0/3.0) * 100.0)

		# Be sure not to connect before the values are set...
		self.sliderFixedOpacity.valueChanged.connect(self.valueChanged)
		self.sliderMovingOpacity.valueChanged.connect(self.valueChanged)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.labelFixedOpacity, 0, 0)
		layout.addWidget(self.sliderFixedOpacity, 0, 1)
		layout.addWidget(self.labelMovingOpacity, 1, 0)
		layout.addWidget(self.sliderMovingOpacity, 1, 1)

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
		self.fixedOpacity = self.applyOpacityFunction(float(self.sliderFixedOpacity.value()) / 100.0)
		self.movingOpacity = self.applyOpacityFunction(float(self.sliderMovingOpacity.value()) / 100.0)
		self.updateTransferFunctions()

	def updateTransferFunctions(self):
		self.fixedVolProp = self._createVolPropFromVis(self.fixedVisualization, self.fixedOpacity)
		self.movingVolProp = self._createVolPropFromVis(self.movingVisualization, self.movingOpacity)

		self.updatedTransferFunction.emit()

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

	@overrides(MultiVolumeVisualization)
	def configureMapper(self, mapper):
		# Shader type 0 is normal 'mix' shader
		mapper.SetShaderType(0)

	def applyOpacityFunction(self, value):
		"""
		Make sure that the slider opacity values are not linear.
		"""
		return value * value * value


class MIPMultiVolumeVisualization(MultiVolumeVisualization):
	"""
	MIPMultiVolumeVisualization is a visualization that shows
	MIP visualizations of both datasets and adds them
	together. It uses complementary colors for the datasets
	so that the visualization is white in the spots where
	they are the same.
	"""
	def __init__(self):
		super(MIPMultiVolumeVisualization, self).__init__()

		self.fixedHue = 0

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

	def setImageData(self, fixedImageData, movingImageData):
		self.fixedImageData = fixedImageData
		self.movingImageData = movingImageData

	def updateTransferFunctions(self):
		self.fixedVolProp = self._createVolPropFromImageData(self.fixedImageData)
		self.movingVolProp = self._createVolPropFromImageData(self.movingImageData)

		self.updatedTransferFunction.emit()

	def _createVolPropFromImageData(self, imageData):
		volProp = vtkVolumeProperty()
		if imageData is not None:
			color, opacityFunction = CreateRangeFunctions(imageData)
		else:
			color, opacityFunction = CreateEmptyFunctions()
		volProp.SetColor(color)
		volProp.SetScalarOpacity(opacityFunction)

		return volProp

	def valueChanged(self, value):
		self.fixedHue = self.hueSlider.value()
		self.updateTransferFunctions()

	def configureMapper(self, mapper):
		mapper.SetShaderType(1)


class MIDAMultiVolumeVisualization(MultiVolumeVisualization):
	"""
	MIDAMultiVolumeVisualization is a visualization that shows
	two MIDA renders.
	"""
	def __init__(self):
		super(MIDAMultiVolumeVisualization, self).__init__()

	def getParameterWidget(self):
		return QWidget()

	def setImageData(self, fixedImageData, movingImageData):
		self.fixedImageData = fixedImageData
		self.movingImageData = movingImageData

	def updateTransferFunctions(self):
		self.fixedVolProp = self._createVolPropFromImageData(self.fixedImageData, [1.0, 0.5, 0.0])
		self.movingVolProp = self._createVolPropFromImageData(self.movingImageData, [1.0, 1.0, 1.0])

		self.updatedTransferFunction.emit()

	def _createVolPropFromImageData(self, imageData, color):
		volProp = vtkVolumeProperty()
		if imageData is not None:
			color, opacityFunction = CreateRangeFunctions(imageData, color)
		else:
			color, opacityFunction = CreateEmptyFunctions()
		volProp.SetColor(color)
		volProp.SetScalarOpacity(opacityFunction)

		return volProp

	def valueChanged(self, value):
		self.updateTransferFunctions()

	def configureMapper(self, mapper):
		mapper.SetShaderType(2)


# Convenience functions

def CreateFunctionFromProperties(opacity, volProp):
	"""
	:type opacityFunction: vtkVolumeProperty
	"""
	opacityFunction = volProp.GetScalarOpacity()
	for index in range(opacityFunction.GetSize()):
		val = [0 for x in range(4)]
		opacityFunction.GetNodeValue(index, val)
		val[1] = val[1] * float(opacity)
		opacityFunction.SetNodeValue(index, val)
	return opacityFunction


def CreateEmptyFunctions():
	"""
	:rtype: vtkColorTransferFunction, vtkPiecewiseFunction
	"""
	# Transfer functions and properties
	colorFunction = vtkColorTransferFunction()
	colorFunction.AddRGBPoint(0, 0, 0, 0, 0.0, 0.0)
	colorFunction.AddRGBPoint(1000, 0, 0, 0, 0.0, 0.0)

	opacityFunction = vtkPiecewiseFunction()
	opacityFunction.AddPoint(0, 0, 0.0, 0.0)
	opacityFunction.AddPoint(1000, 0, 0.0, 0.0)

	return colorFunction, opacityFunction


def CreateRangeFunctions(imageData, color=None):
	"""
	:type imageData: vktImageData
	:type color: array of length 3 (r, g, b)
	:rtype: vtkColorTransferFunction, vtkPiecewiseFunction
	"""
	col = [1, 1, 1]
	if color is not None:
		col = color
	minimum, maximum = imageData.GetScalarRange()
	colorFunction = vtkColorTransferFunction()
	colorFunction.AddRGBSegment(minimum, 0, 0, 0, maximum, col[0], col[1], col[2])

	opacityFunction = vtkPiecewiseFunction()
	opacityFunction.AddSegment(minimum, 0.0, maximum, 1.0)

	return colorFunction, opacityFunction

# def CreateRangeFunctionsWithHue(imageData, )
