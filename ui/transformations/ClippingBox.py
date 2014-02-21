"""
ClippingBox

:Authors:
	Berend Klein Haneveld
"""
from ui.Interactor import Interactor
from PySide.QtCore import QObject
from PySide.QtCore import Signal
from vtk import vtkBoxWidget
from vtk import vtkPlanes
from vtk import vtkImagePlaneWidget
from vtk import vtkPolyData
from vtk import vtkTransform


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
		self.tranform = vtkTransform()

		self.clippingBoxState = False
		self.clippingPlanesState = True

	def setWidget(self, widget):
		self.widget = widget
		self.clippingBox.SetInteractor(self.widget.rwi)
		self.clippingBox.SetDefaultRenderer(self.widget.renderer)
		self.clippingBox.SetPlaceFactor(1.0)
		self.clippingBox.SetRotationEnabled(False)
		self.clippingBox.InsideOutOn()
		self.clippingBox.GetSelectedFaceProperty().SetOpacity(0.3)

	def showClippingBox(self, show):
		self.clippingBoxState = show
		self._updateClippingBoxAndPlanes()

	def showClippingPlanes(self, show):
		self.clippingPlanesState = show
		self._updateClippingBoxAndPlanes()

	def cleanUp(self):
		self.enable(False)
		self.cleanUpCallbacks()

	def update(self):
		volVis = self.widget.volumeVisualization
		from ui.visualizations.VolumeVisualization import VisualizationTypeSimple
		if volVis is None or volVis.visualizationType != VisualizationTypeSimple:
			for i in range(6):
				lookupTable = self.planes[i].GetLookupTable()
				lookupTable.SetAlphaRange(1.0, 1.0)
				lookupTable.Build()
			return

		# TODO: also use the upper bound
		minimum = volVis.minimum
		maximum = volVis.maximum
		lowerBound = volVis.lowerBound
		window = maximum - minimum
		level = minimum + window / 2.0

		for i in range(6):
			self.planes[i].SetWindowLevel(window, level)
			lookupTable = self.planes[i].GetLookupTable()
			nrOfValues = lookupTable.GetNumberOfTableValues()
			lowerBorder = (lowerBound - minimum) / (maximum - minimum)
			currVal = 0.0
			j = 0
			# Make all values beneath a certain gray value transparent
			while currVal < lowerBorder and j < nrOfValues:
				value = list(lookupTable.GetTableValue(j))
				value[3] = 0.0
				lookupTable.SetTableValue(j, value)
				currVal = value[0]
				j += 1
			# Don't forget to set all the following opacity values to 1.0
			while j < nrOfValues:
				value = list(lookupTable.GetTableValue(j))
				value[3] = 1.0
				lookupTable.SetTableValue(j, value)
				j += 1

			lookupTable.Build()

	def setImageData(self, imageData):
		self.imageData = imageData
		self.clippingBox.SetInputData(imageData)
		self.clippingBox.PlaceWidget()

		for i in range(6):
			imagePlaneWidget = vtkImagePlaneWidget()
			imagePlaneWidget.SetInteractor(self.widget.rwi)
			imagePlaneWidget.PlaceWidget()
			imagePlaneWidget.SetInputData(imageData)
			imagePlaneWidget.DisplayTextOff()
			imagePlaneWidget.PickingManagedOff()
			
			imagePlaneWidget.SetRestrictPlaneToVolume(1)
			cursorProperty = imagePlaneWidget.GetCursorProperty()
			cursorProperty.SetOpacity(0.0)
			planeProperty = imagePlaneWidget.GetPlaneProperty()
			planeProperty.SetColor(0, 0, 0)
			planeProperty.SetOpacity(0.0)
			selectedPlaneProperty = imagePlaneWidget.GetSelectedPlaneProperty()
			selectedPlaneProperty.SetColor(0, 0, 0)
			selectedPlaneProperty.SetOpacity(0.0)
			self.planes.append(imagePlaneWidget)

		self.AddObserver(self.clippingBox, "InteractionEvent", self.transformCallback)

	def resetClippingBox(self):
		# Reset the planes by setting identity transform
		transform = vtkTransform()
		self.clippingBox.SetTransform(transform)

		# Make sure the mapper is informed of the changes
		planes = vtkPlanes()
		self.clippingBox.GetPlanes(planes)
		self.updateMapperWithClippingPlanes(planes)

		# Update the image plane widgets
		self.updateImagePlanes()

	def setTransform(self, transform):
		"""
		Deprecated...
		"""
		assert False
		self.tranform = transform
		self.clippingBox.SetTransform(transform)

		for plane in self.planes:
			plane.SetUserTransform(transform)

		self.updateImagePlanes()

	def _updateClippingBoxAndPlanes(self):
		# Update visibility of clipping box
		if self.clippingBoxState:
			self.clippingBox.EnabledOn()
		else:
			self.clippingBox.EnabledOff()

		# Update visibility of the plane widgets
		if self.clippingPlanesState:
			for plane in self.planes:
				plane.On()
				plane.InteractionOff()
			self.updateImagePlanes()
		else:
			for plane in self.planes:
				plane.Off()

	def updateImagePlanes(self):
		# First get the planes of the clipping box
		planes = vtkPlanes()
		self.clippingBox.GetPlanes(planes)

		# Also get the polydata of the box
		p = []
		polyData = vtkPolyData()
		self.clippingBox.GetPolyData(polyData)

		# Append a 4th element to the polydata points
		for i in range(8):
			point = list(polyData.GetPoint(i))
			p.append(point + [1.0])

		# Transform all the polydata points
		inv = self.tranform.GetInverse()
		for i in range(len(p)):
			inv.MultiplyPoint(p[i], p[i])
			p[i] = p[i][0:3]
			
		center = [0, 0, 0]
		for point in p:
			center[0] += point[0]
			center[1] += point[1]
			center[2] += point[2]

		center[0] /= len(p)
		center[1] /= len(p)
		center[2] /= len(p)

		for i in range(len(p)):
			point = p[i]
			for j in range(3):
				dist = point[j] - center[j]
				p[i][j] += (dist / 30.0)

		# Update the position of all the planes
		self.planes[0].SetOrigin(p[0])
		self.planes[0].SetPoint1(p[4])
		self.planes[0].SetPoint2(p[3])
		self.planes[1].SetOrigin(p[3])
		self.planes[1].SetPoint1(p[7])
		self.planes[1].SetPoint2(p[2])
		self.planes[2].SetOrigin(p[2])
		self.planes[2].SetPoint1(p[6])
		self.planes[2].SetPoint2(p[1])
		self.planes[3].SetOrigin(p[1])
		self.planes[3].SetPoint1(p[5])
		self.planes[3].SetPoint2(p[0])
		self.planes[4].SetOrigin(p[0])
		self.planes[4].SetPoint2(p[3])
		self.planes[4].SetPoint1(p[1])
		self.planes[5].SetOrigin(p[4])
		self.planes[5].SetPoint1(p[7])
		self.planes[5].SetPoint2(p[5])

		for plane in self.planes:
			plane.UpdatePlacement()

	def updateMapperWithClippingPlanes(self, planes):
		self.widget.mapper.SetClippingPlanes(planes)

	def transformCallback(self, arg1, arg2):
		planes = vtkPlanes()
		arg1.GetPlanes(planes)
		self.updateMapperWithClippingPlanes(planes)
		self.updateImagePlanes()
