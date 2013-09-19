"""
DeformableTransformationTool

:Authors:
	Berend Klein Haneveld 2013
"""
from TransformationTool import TransformationTool
from core.decorators import overrides
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtCore import Qt
from ParameterWidget import ParameterWidget


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
		titleLabel = QLabel(self.transformation.name)

		paramWidget = ParameterWidget()
		paramWidget.parameterModel.setTransformation(self.transformation)

		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(titleLabel)
		layout.addWidget(paramWidget)

		widget = QWidget()
		widget.setLayout(layout)
		return widget
