"""
TransformationTool

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtCore import QObject
from PySide.QtCore import Signal


class TransformationTool(QObject):
	"""
	TransformationTool
	"""
	toolFinished = Signal()

	def __init__(self):
		super(TransformationTool, self).__init__()

	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		raise NotImplementedError()

	def cancelTransform(self):
		raise NotImplementedError()

	def applyTransform(self):
		raise NotImplementedError()

	def cleanUp(self):
		raise NotImplementedError()

	def getParameterWidget(self):
		raise NotImplementedError()
