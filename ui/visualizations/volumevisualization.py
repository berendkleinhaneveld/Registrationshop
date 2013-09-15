"""
VolumeVisualization

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtCore import Signal
from PySide.QtCore import QObject

# Define Render Types
VisualizationTypeSimple = "Simple"
VisualizationTypeGray = "Gray scale"
VisualizationTypeCT = "CT"
VisualizationTypeMIP = "MIP"
VisualizationTypeRamp = "Ramp"

VolumePropKey = "VolumeVisualization"
VisualizationTypeKey = "VisualizationTypeKey"
ColorFuncKey = "ColorFuncKey"
TransFuncKey = "TransFuncKey"


# Volume properties

class VolumeVisualization(QObject):
	"""
	VolumeVisualization is an interface class for the different render types
	"""

	updatedTransferFunction = Signal()

	def __init__(self):
		super(VolumeVisualization, self).__init__()

		self.volProp = None
		self.visualizationType = None

	def getParameterWidget(self):
		"""
		This method should be overridden in the subclasses.
		:rtype: QWidget
		"""
		raise NotImplementedError()

	def setImageData(self, imageData):
		"""
		This method should be overridden in the subclasses.
		:type imageData: vtkImageData
		"""
		raise NotImplementedError()

	def configureMapper(self, mapper):
		raise NotImplementedError()

	def updateTransferFunction(self):
		raise NotImplementedError()

	def valueChanged(self, value):
		raise NotImplementedError()
