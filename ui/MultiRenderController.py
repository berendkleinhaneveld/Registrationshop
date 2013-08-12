"""
MultiRenderController

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtCore import QObject
from PySide.QtCore import Slot
from PySide.QtCore import Signal
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from core.data.DataReader import DataReader
from core.data.DataResizer import DataResizer

class MultiRenderController(QObject):
	"""
	MultiRenderController
	"""

	fixedDataChanged = Signal(object)
	movingDataChanged = Signal(object)
	fixedVolumePropertyChanged = Signal(object)
	fixedVolumePropertyUpdated = Signal(object)
	movingVolumePropertyChanged = Signal(object)
	movingVolumePropertyUpdated = Signal(object)
	slicesChanged = Signal(object)
	slicesUpdated = Signal(object)

	maxVoxelSize = 9000000

	def __init__(self, mulitRenderWidget):
		super(MultiRenderController, self).__init__()

		self.multiRenderWidget = mulitRenderWidget
		self.fixedImageData = None
		self.movingImageData = None
		self.fixedVolumeProperty = None
		self.movingVolumeProperty = None
		self.fixedOpacity = 1.0
		self.movingOpacity = 1.0
		self.slices = [False, False, False]

	@Slot(basestring)
	def setFixedFile(self, fileName):
		if fileName is None:
			self.fixedImageData = None
			self.fixedVolumeProperty = None
			self.multiRenderWidget.setFixedData(self.fixedImageData)
			self.multiRenderWidget.setFixedVolumeProperty(self.fixedVolumeProperty)
			self.fixedDataChanged.emit(self.fixedImageData)
			self.fixedVolumePropertyChanged.emit(self.fixedVolumeProperty)
			return

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		imageResizer = DataResizer()
		self.fixedImageData = imageResizer.ResizeData(imageData, maximum=self.maxVoxelSize)
		self.multiRenderWidget.setFixedData(self.fixedImageData)
		self.fixedDataChanged.emit(self.fixedImageData)


	@Slot(basestring)
	def setMovingFile(self, fileName):
		if fileName is None:
			self.movingImageData = None
			self.movingVolumeProperty = None
			self.multiRenderWidget.setMovingData(self.movingImageData)
			self.multiRenderWidget.setMovingVolumeProperty(self.movingVolumeProperty)
			self.movingDataChanged.emit(self.movingImageData)
			self.movingVolumePropertyChanged.emit(self.movingVolumeProperty)
			return

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		imageResizer = DataResizer()
		self.movingImageData = imageResizer.ResizeData(imageData, maximum=self.maxVoxelSize)
		self.multiRenderWidget.setMovingData(self.movingImageData)
		self.movingDataChanged.emit(self.movingImageData)

	def setFixedOpacity(self, opacity):
		self.fixedOpacity = opacity
		self.updateFixedVolumeProperty()

	def setMovingOpacity(self, opacity):
		self.movingOpacity = opacity
		self.updateMovingVolumeProperty()

	def setTransformBoxVisibility(self, visibility):
		pass

	@Slot(object)
	def setFixedVolumeProperty(self, volumeProperty):
		self.fixedVolumeProperty = volumeProperty
		self.updateFixedVolumeProperty()

	@Slot(object)
	def setMovingVolumeProperty(self, volumeProperty):
		self.movingVolumeProperty = volumeProperty
		self.updateMovingVolumeProperty()

	@Slot(object)
	def setRenderSettings(self, renderSettings):
		print "Warning: MultiRenderController.setRenderSettings(renderSettings) not implemented yet"
		pass

	def getRenderSettings(self):
		print "Warning: MultiRenderController.getRenderSettings() not implemented yet"
		return None

	def setSliceVisibility(self, sliceIndex, visibility):
		"""
		:type sliceIndex: int
		:type visibility: bool
		"""
		self.slices[sliceIndex] = visibility
		self.multiRenderWidget.setSlices(self.slices)
		self.slicesUpdated.emit(self.slices)

	# Private methods

	def updateFixedVolumeProperty(self):
		fixedVolumeProperty = vtkVolumeProperty()
		if self.fixedVolumeProperty is not None:
			fixedVolumeProperty.DeepCopy(self.fixedVolumeProperty.volumeProperty)
			fixedOpacityFunction = CreateFunctionFromOpacityAndVolumeProperty(self.fixedOpacity, fixedVolumeProperty)
			fixedVolumeProperty.SetScalarOpacity(fixedOpacityFunction)
		else:
			color, opacityFunction = CreateEmptyFunctions()
			fixedVolumeProperty.SetColor(color)
			fixedVolumeProperty.SetScalarOpacity(opacityFunction)

		self.multiRenderWidget.setFixedVolumeProperty(fixedVolumeProperty)
		self.fixedVolumePropertyUpdated.emit(fixedVolumeProperty)

	def updateMovingVolumeProperty(self):
		movingVolumeProperty = vtkVolumeProperty()
		if self.movingVolumeProperty is not None:
			movingVolumeProperty.DeepCopy(self.movingVolumeProperty.volumeProperty)
			movingOpacityFunction = CreateFunctionFromOpacityAndVolumeProperty(self.movingOpacity, movingVolumeProperty)
			movingVolumeProperty.SetScalarOpacity(movingOpacityFunction)
		else:
			color, opacityFunction = CreateEmptyFunctions()
			movingVolumeProperty.SetColor(color)
			movingVolumeProperty.SetScalarOpacity(opacityFunction)

		self.multiRenderWidget.setMovingVolumeProperty(movingVolumeProperty)
		self.movingVolumePropertyUpdated.emit(movingVolumeProperty)

def CreateFunctionFromOpacityAndVolumeProperty(opacity, volProp):
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
	colorFunction.AddRGBPoint( 0, 0, 0, 0, 0.0, 0.0)
	colorFunction.AddRGBPoint( 1000, 0, 0, 0, 0.0, 0.0)

	opacityFunction = vtkPiecewiseFunction()
	opacityFunction.AddPoint( 0, 0, 0.0, 0.0)
	opacityFunction.AddPoint( 1000, 0, 0.0, 0.0)

	return colorFunction, opacityFunction
