"""
TransformWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtCore import QObject
from PySide.QtCore import Signal
from vtk import vtkTransform
from ui.Interactor import Interactor


class TransformWidget(QObject, Interactor):
	"""
	Abstract widget that serves as super for actual
	transformation widgets, such a translation, scale
	and rotate widgets.
	"""

	updatedTransform = Signal()

	def __init__(self):
		super(TransformWidget, self).__init__()
		self.rwi = None
		self.renderer = None
		self.pos = [0, 0, 0]

		self.handles = []
		self.representations = []
		self.transform = vtkTransform()

	def setObjects(self, rwi, renderer, pos):
		self.rwi = rwi
		self.renderer = renderer
		self.pos = pos

		self._internalInit()

	def _internalInit(self):
		pass

	def setPosition(self, pos):
		# self.pos = pos
		for rep in self.representations:
			rep.SetWorldPosition(pos)

	def On(self):
		for handle in self.handles:
			handle.On()

	def Off(self):
		for handle in self.handles:
			handle.Off()
