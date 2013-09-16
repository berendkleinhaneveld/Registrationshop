"""
Interactor

:Authors:
	Berend Klein Haneveld
"""


class Interactor(object):
	"""
	Interactor
	"""

	def __init__(self):
		super(Interactor, self).__init__()

	def initInteractor(self):
		self.__callbacks = []

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
