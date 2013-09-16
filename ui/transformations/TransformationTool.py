"""
TransformationTool

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtCore import QObject


class TransformationTool(QObject):
	"""
	TransformationTool
	"""

	def __init__(self):
		super(TransformationTool, self).__init__()

	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		raise NotImplementedError()

	def applyTransform(self):
		raise NotImplementedError()

	def cleanUp(self):
		raise NotImplementedError()

	def getParameterWidget(self):
		raise NotImplementedError()
