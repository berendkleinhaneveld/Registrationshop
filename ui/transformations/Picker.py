"""
Picker

:Authors:
	Berend Klein Haneveld
"""
from ui.Interactor import Interactor
from PySide.QtCore import Signal
from PySide.QtCore import QObject


class Picker(QObject, Interactor):
	"""
	Picker is a dedicated picker for points in 3D datasets.
	"""

	pickedLocation = Signal(list)

	def __init__(self):
		super(Picker, self).__init__()
		self.props = []
		self.widget = None

	def setWidget(self, widget):
		raise NotImplementedError()

	def setPropertiesWidget(self, widget):
		pass

	def cleanUp(self):
		self.cleanUpCallbacks()

	# Callbacks

	def mouseMove(self, iren, event=""):
		pass

	def keyPress(self, iren, event=""):
		pass
