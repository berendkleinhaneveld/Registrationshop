"""
MultiVolumeVisualization

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtCore import QObject
from PySide.QtCore import Signal
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction

# Define render types for multi render
MultiVisualizationTypeMix = "Default mix"
MultiVisualizationTypeMIP = "Combined MIP"
MultiVisualizationTypeMIDA = "Single MIDA"


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

	def setMapper(self, mapper):
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
