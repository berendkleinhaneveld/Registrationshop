"""
TransformationTool

:Authors:
	Berend Klein Haneveld
"""
from vtk import vtkBoxWidget
from vtk import vtkTransform
from core.decorators import overrides


class TransformationTool(object):
	"""
	TransformationTool
	"""

	def __init__(self):
		super(TransformationTool, self).__init__()

		self.renderWidget = None

	def setRenderWidget(self, renderWidget):
		raise NotImplementedError()


class UserTransformationTool(TransformationTool):
	def __init__(self):
		super(UserTransformationTool, self).__init__()

	@overrides(TransformationTool)
	def setRenderWidget(self, multiRenderWidget):
		self.renderWidget = multiRenderWidget
		self.setImageData(self.renderWidget.movingImageData)

	def setImageData(self, movingImageData):
		self.transformBox = vtkBoxWidget()
		self.transformBox.SetInteractor(self.renderWidget.rwi)
		self.transformBox.SetPlaceFactor(1.01)
		self.transformBox.SetInputData(movingImageData)
		self.transformBox.SetDefaultRenderer(self.renderWidget.renderer)
		self.transformBox.InsideOutOn()
		self.transformBox.PlaceWidget()

		self.transformBox.AddObserver("InteractionEvent", self.transformCallback)
		self.transformBox.GetSelectedFaceProperty().SetOpacity(0.3)
		self.transformBox.EnabledOn()

	def transformCallback(self, arg1, arg2):
		transform = vtkTransform()
		arg1.GetTransform(transform)
		self.renderWidget.mapper.SetSecondInputUserTransform(transform)


class LandmarkTransformationTool(TransformationTool):
	def __init__(self, renderWidget):
		super(LandmarkTransformationTool, self).__init__(renderWidget)

		
class DeformableTransformationTool(TransformationTool):
	def __init__(self, renderWidget):
		super(DeformableTransformationTool, self).__init__(renderWidget)
