"""
Interactor

This class can be used to simply managing callback resources.
Callbacks are often used by interactors with vtk and callbacks
are hard to keep track of.
Use multiple inheritance to inherit from this class to get access
to the convenience methods.

Observers for vtk events can be added through
AddObserver(obj, eventName, callbackFunction) and when it is time
to clean up, just call cleanUpCallbacks().

:Authors:
	Berend Klein Haneveld
"""


class Interactor(object):
	"""
	Interactor
	"""

	def __init__(self):
		super(Interactor, self).__init__()

	def AddObserver(self, obj, eventName, callbackFunction, priority=None):
		"""
		Creates a callback and stores the callback so that later
		on the callbacks can be properly cleaned up.
		"""
		if not hasattr(self, "_callbacks"):
			self._callbacks = []

		if priority is not None:
			callback = obj.AddObserver(eventName, callbackFunction, priority)
		else:
			callback = obj.AddObserver(eventName, callbackFunction)
		self._callbacks.append((obj, callback))

	def cleanUpCallbacks(self):
		"""
		Cleans up the vtkCallBacks
		"""
		if not hasattr(self, "_callbacks"):
			return

		for obj, callback in self._callbacks:
			obj.RemoveObserver(callback)
		self._callbacks = []
