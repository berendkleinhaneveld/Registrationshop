"""
DeformableTransformationTool

:Authors:
	Berend Klein Haneveld 2013
"""
from TransformationTool import TransformationTool
from core.decorators import overrides
from PySide.QtGui import QWidget


class DeformableTransformationTool(TransformationTool):
	def __init__(self):
		super(DeformableTransformationTool, self).__init__()

	def setTransformation(self, transformation):
		self.transformation = transformation
		print self.transformation.name

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed, moving, multi):
		self.multiWidget = multi
		self.movingWidget = moving

	@overrides(TransformationTool)
	def applyTransform(self):
		pass

	@overrides(TransformationTool)
	def cleanUp(self):
		pass

	@overrides(TransformationTool)
	def getParameterWidget(self):
		widget = QWidget()
		return widget
