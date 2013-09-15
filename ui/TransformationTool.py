"""
TransformationTool

TODO:
* Give the spheres corresponding colors or numbers

:Authors:
	Berend Klein Haneveld
"""


class TransformationTool(object):
	"""
	TransformationTool
	"""

	def __init__(self):
		super(TransformationTool, self).__init__()

		self.__callbacks = []

	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		raise NotImplementedError()

	def applyTransform(self):
		raise NotImplementedError()

	def cleanUp(self):
		raise NotImplementedError()

	def AddObserver(self, obj, eventName, callbackFunction):
		callback = obj.AddObserver(eventName, callbackFunction)
		self.__callbacks.append((obj, callback))

	def cleanUpCallbacks(self):
		"""
		Cleans up the vtkCallBacks
		"""
		for obj, callback in self.__callbacks:
			obj.RemoveObserver(callback)
		self.__callbacks = []

	def getParameterWidget(self):
		raise NotImplementedError()


class DeformableTransformationTool(TransformationTool):
	def __init__(self):
		super(DeformableTransformationTool, self).__init__()
