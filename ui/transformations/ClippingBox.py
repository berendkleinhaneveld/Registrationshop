"""
ClippingBox

:Authors:
	Berend Klein Haneveld
"""
from ui.Interactor import Interactor
from PySide.QtCore import QObject
from vtk import vtkBoxWidget
from vtk import vtkPlanes
from vtk import vtkImagePlaneWidget
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
		self.planes = []

	def setWidget(self, widget):
		self.widget = widget
		self.clippingBox.SetInteractor(self.widget.rwi)
		self.clippingBox.SetDefaultRenderer(self.widget.renderer)

	def enable(self, enable):
		if enable:
			self.clippingBox.EnabledOn()
			for plane in self.planes:
				plane.On()
				plane.InteractionOff()
				plane.PickingManagedOff()
			self.updateImagePlanes()
		else:
			self.clippingBox.EnabledOff()
			for plane in self.planes:
				plane.Off()
		self.widget.render()

	def cleanUp(self):
		# Hide the transformation box
		self.clippingBox.EnabledOff()
		self.cleanUpCallbacks()

	def setImageData(self, imageData):
		self.imageData = imageData
		self.clippingBox.SetPlaceFactor(1.01)
		self.clippingBox.SetRotationEnabled(False)
		self.clippingBox.SetInputData(imageData)
		self.clippingBox.InsideOutOn()
		self.clippingBox.PlaceWidget()

		for i in range(6):
			imagePlaneWidget = vtkImagePlaneWidget()
			imagePlaneWidget.DisplayTextOff()
			imagePlaneWidget.SetInteractor(self.widget.rwi)
			imagePlaneWidget.SetInputData(imageData)
			imagePlaneWidget.SetRestrictPlaneToVolume(1)
			imagePlaneWidget.PlaceWidget()
			cursorProperty = imagePlaneWidget.GetCursorProperty()
			cursorProperty.SetOpacity(0.0)
			planeProperty = imagePlaneWidget.GetPlaneProperty()
			planeProperty.SetColor(0, 0, 0)
			selectedPlaneProperty = imagePlaneWidget.GetSelectedPlaneProperty()
			selectedPlaneProperty.SetColor(0, 0, 0)
			self.planes.append(imagePlaneWidget)

		self.AddObserver(self.clippingBox, "InteractionEvent", self.transformCallback)
		self.clippingBox.GetSelectedFaceProperty().SetOpacity(0.3)

	def setTransform(self, transform):
		self.clippingBox.SetTransform(transform)

	def updateImagePlanes(self):
		planes = vtkPlanes()
		self.clippingBox.GetPlanes(planes)
		bounds = planes.GetPoints().GetBounds()

		# Create points for all of the corners of the bounds
		p = [[0 for x in range(3)] for x in range(8)]
		p[0] = [bounds[0], bounds[2], bounds[4]]
		p[1] = [bounds[0], bounds[2], bounds[5]]
		p[2] = [bounds[0], bounds[3], bounds[4]]
		p[3] = [bounds[0], bounds[3], bounds[5]]
		p[4] = [bounds[1], bounds[3], bounds[4]]
		p[5] = [bounds[1], bounds[3], bounds[5]]
		p[6] = [bounds[1], bounds[2], bounds[4]]
		p[7] = [bounds[1], bounds[2], bounds[5]]

		self.planes[0].SetOrigin(p[0])
		self.planes[0].SetPoint1(p[1])
		self.planes[0].SetPoint2(p[2])
		self.planes[1].SetOrigin(p[2])
		self.planes[1].SetPoint1(p[3])
		self.planes[1].SetPoint2(p[4])
		self.planes[2].SetOrigin(p[4])
		self.planes[2].SetPoint1(p[5])
		self.planes[2].SetPoint2(p[6])
		self.planes[3].SetOrigin(p[6])
		self.planes[3].SetPoint1(p[7])
		self.planes[3].SetPoint2(p[0])
		self.planes[4].SetOrigin(p[0])
		self.planes[4].SetPoint2(p[2])
		self.planes[4].SetPoint1(p[6])
		self.planes[5].SetOrigin(p[1])
		self.planes[5].SetPoint1(p[3])
		self.planes[5].SetPoint2(p[7])

		for i in range(6):
			self.planes[i].UpdatePlacement()

	def transformCallback(self, arg1, arg2):
		planes = vtkPlanes()
		arg1.GetPlanes(planes)
		self.widget.mapper.SetClippingPlanes(planes)
		self.updateImagePlanes()
