"""
TransformBox

:Authors:
	Berend Klein Haneveld
"""
from ui.Interactor import Interactor
from PySide.QtCore import QObject
from vtk import vtkBoxWidget
from vtk import vtkTransform
from PySide.QtCore import Signal


class TransformBox(QObject, Interactor):
	"""
	TransformBox
	"""
	transformUpdated = Signal(object)

	def __init__(self):
		super(TransformBox, self).__init__()

	def setWidget(self, widget):
		self.widget = widget

	def cleanUp(self):
		# Hide the transformation box
		self.transformBox.EnabledOff()
		self.cleanUpCallbacks()

	def setImageData(self, imageData):
		self.transformBox = vtkBoxWidget()
		self.transformBox.SetInteractor(self.widget.rwi)
		self.transformBox.SetPlaceFactor(1.01)
		self.transformBox.SetInputData(imageData)
		self.transformBox.SetDefaultRenderer(self.widget.rendererOverlay)
		self.transformBox.InsideOutOn()
		self.transformBox.PlaceWidget()

		self.AddObserver(self.transformBox, "InteractionEvent", self.transformCallback)
		self.transformBox.GetSelectedFaceProperty().SetOpacity(0.3)
		self.transformBox.EnabledOn()

	def setTransform(self, transform):
		self.transformBox.SetTransform(transform)

	def transformCallback(self, arg1, arg2):
		transform = vtkTransform()
		arg1.GetTransform(transform)
		self.transformUpdated.emit(transform)
