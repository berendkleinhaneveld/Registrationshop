"""
ClippingBox

:Authors:
	Berend Klein Haneveld
"""
from ui.Interactor import Interactor
from PySide.QtCore import QObject
from vtk import vtkBoxWidget
# from vtk import vtkTransform
from vtk import vtkPlanes
from PySide.QtCore import Signal


class ClippingBox(QObject, Interactor):
	"""
	ClippingBox
	"""
	transformUpdated = Signal(object)

	def __init__(self):
		super(ClippingBox, self).__init__()
		self.widget = None

		self.clippingBox = vtkBoxWidget()

	def setWidget(self, widget):
		self.widget = widget
		self.clippingBox.SetInteractor(self.widget.rwi)
		self.clippingBox.SetDefaultRenderer(self.widget.renderer)

	def enable(self, enable):
		if enable:
			self.clippingBox.EnabledOn()
		else:
			self.clippingBox.EnabledOff()

	def cleanUp(self):
		# Hide the transformation box
		self.clippingBox.EnabledOff()
		self.cleanUpCallbacks()

	def setImageData(self, imageData):
		self.clippingBox.SetPlaceFactor(1.01)
		self.clippingBox.SetRotationEnabled(False)
		self.clippingBox.SetInputData(imageData)
		self.clippingBox.InsideOutOn()
		self.clippingBox.PlaceWidget()

		self.AddObserver(self.clippingBox, "InteractionEvent", self.transformCallback)
		self.clippingBox.GetSelectedFaceProperty().SetOpacity(0.3)

	def setTransform(self, transform):
		self.clippingBox.SetTransform(transform)

	def transformCallback(self, arg1, arg2):
		planes = vtkPlanes()
		arg1.GetPlanes(planes)
		self.widget.mapper.SetClippingPlanes(planes)
