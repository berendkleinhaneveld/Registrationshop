"""
MIDAMultiVolumeVisualization

:Authors:
	Berend Klein Haneveld
"""
from multivolumevisualization import MultiVolumeVisualization
from multivolumevisualization import CreateEmptyFunctions
from multivolumevisualization import CreateRangeFunctions
from core.decorators import overrides
from PySide.QtGui import QWidget
from vtk import vtkVolumeProperty


class MIDAMultiVolumeVisualization(MultiVolumeVisualization):
	"""
	MIDAMultiVolumeVisualization is a visualization that shows
	two MIDA renders.
	"""
	def __init__(self):
		super(MIDAMultiVolumeVisualization, self).__init__()

	@overrides(MultiVolumeVisualization)
	def getParameterWidget(self):
		return QWidget()

	@overrides(MultiVolumeVisualization)
	def setImageData(self, fixedImageData, movingImageData):
		self.fixedImageData = fixedImageData
		self.movingImageData = movingImageData

	@overrides(MultiVolumeVisualization)
	def updateTransferFunctions(self):
		self.fixedVolProp = self._createVolPropFromImageData(self.fixedImageData, [1.0, 0.5, 0.0])
		self.movingVolProp = self._createVolPropFromImageData(self.movingImageData, [1.0, 1.0, 1.0])

		self.updatedTransferFunction.emit()

	@overrides(MultiVolumeVisualization)
	def valueChanged(self, value):
		self.updateTransferFunctions()

	@overrides(MultiVolumeVisualization)
	def configureMapper(self, mapper):
		mapper.SetShaderType(2)

	def _createVolPropFromImageData(self, imageData, color):
		volProp = vtkVolumeProperty()
		if imageData is not None:
			color, opacityFunction = CreateRangeFunctions(imageData, color)
		else:
			color, opacityFunction = CreateEmptyFunctions()
		volProp.SetColor(color)
		volProp.SetScalarOpacity(opacityFunction)

		return volProp
