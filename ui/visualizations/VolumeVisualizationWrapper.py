from core.vtkObjectWrapper import vtkPiecewiseFunctionWrapper
from core.vtkObjectWrapper import vtkColorTransferFunctionWrapper
from core.vtkObjectWrapper import vtkVolumePropertyWrapper
from .VolumeVisualizationFactory import VolumeVisualizationFactory


class VolumeVisualizationWrapper(object):
	"""
	VolumeVisualizationWrapper wraps around a volume property. It wraps
	all the vtk attributes in their own wrappers.
	"""
	standardAttributes = ["visualizationType",
		"sectionsOpacity",
		"lowerBound",
		"upperBound",
		"minimum",
		"maximum",
		"hue",
		"brightness",
		"window",
		"color",
		"level",
		"opacity"]

	def __init__(self, volumeVisualization=None):
		super(VolumeVisualizationWrapper, self).__init__()

		if volumeVisualization is not None:
			self.setVolumeVisualization(volumeVisualization)

	def setVolumeVisualization(self, volumeVisualization):
		for attribute in VolumeVisualizationWrapper.standardAttributes:
			if hasattr(volumeVisualization, attribute) and getattr(volumeVisualization, attribute) is not None:
				setattr(self, attribute, getattr(volumeVisualization, attribute))

		if hasattr(volumeVisualization, "volProp"):
			self.volProp = vtkVolumePropertyWrapper(volumeVisualization.volProp)
		if hasattr(volumeVisualization, "opacityFunction"):
			self.opacityFunction = vtkPiecewiseFunctionWrapper(volumeVisualization.opacityFunction)
		if hasattr(volumeVisualization, "colorFunction"):
			self.colorFunction = vtkColorTransferFunctionWrapper(volumeVisualization.colorFunction)

	def getVolumeVisualization(self):
		volumeVisualization = VolumeVisualizationFactory.CreateProperty(self.visualizationType)

		for attribute in VolumeVisualizationWrapper.standardAttributes:
			if hasattr(self, attribute) and getattr(self, attribute) is not None:
				setattr(volumeVisualization, attribute, getattr(self, attribute))

		if hasattr(self, "volProp") and self.volProp is not None:
			volumeVisualization.volProp = self.volProp.originalObject()
		if hasattr(self, "opacityFunction") and self.opacityFunction is not None:
			volumeVisualization.opacityFunction = self.opacityFunction.originalObject()
		if hasattr(self, "colorFunction") and self.colorFunction is not None:
			volumeVisualization.colorFunction = self.colorFunction.originalObject()

		return volumeVisualization
