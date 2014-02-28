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
	ClippingBox is a class that wraps around a vtkBoxWidget and
	vtkImagePlaneWidgets that can be displayed on the outside of
	the box widget.
	"""
	transformUpdated = Signal(object)

	def __init__(self):
		super(ClippingBox, self).__init__()
		self.widget = None

		self.clippingBox = vtkBoxWidget()
		self.planes = [vtkImagePlaneWidget() for _ in range(6)]
		self.transform = vtkTransform()  # For future functionality

		self._clippingBoxState = False
		self._clippingPlanesState = False

	def setWidget(self, widget):
		"""
		Sets the widget of which the interactor is used
		to display the vtkBoxWidget and the vtkImagePlaneWidgets
		"""
		self.widget = widget
		# TODO: disable interaction with the faces of the box widget
		self.clippingBox.SetInteractor(self.widget.rwi)
		self.clippingBox.SetDefaultRenderer(self.widget.renderer)
		self.clippingBox.SetPlaceFactor(1.0)
		self.clippingBox.SetRotationEnabled(False)
		self.clippingBox.InsideOutOn()
		self.clippingBox.GetSelectedFaceProperty().SetOpacity(0.3)
		self.AddObserver(self.clippingBox, "InteractionEvent", self.transformCallback)
		# Prepare the image plane widgets
		for plane in self.planes:
			plane.SetInteractor(self.widget.rwi)
			plane.DisplayTextOff()
			plane.PickingManagedOff()
			plane.SetRestrictPlaneToVolume(1)
			cursorProperty = plane.GetCursorProperty()
			cursorProperty.SetOpacity(0.0)
			planeProperty = plane.GetPlaneProperty()
			planeProperty.SetColor(0, 0, 0)
			planeProperty.SetOpacity(0.0)
			selectedPlaneProperty = plane.GetSelectedPlaneProperty()
			selectedPlaneProperty.SetColor(0, 0, 0)
			selectedPlaneProperty.SetOpacity(0.0)

	def showClippingBox(self, show):
		"""
		Shows or hides the vtkBoxWidget
		"""
		self._clippingBoxState = show

		# Update visibility of clipping box
		if self._clippingBoxState:
			self.clippingBox.EnabledOn()
		else:
			self.clippingBox.EnabledOff()

	def showClippingPlanes(self, show):
		"""
		Shows or hides the vtkImagePlaneWidgets
		"""
		self._clippingPlanesState = show

		# Update visibility of the plane widgets
		if self._clippingPlanesState:
			for plane in self.planes:
				plane.On()
				plane.InteractionOff()
			self._updateImagePlanePlacement()
		else:
			for plane in self.planes:
				plane.Off()

	def cleanUp(self):
		"""
		Inherited from Interactor
		Calls reset()
		After calling this setWidget() should be called again
		if this object is to be reused
		"""
		self.showClippingBox(False)
		self.showClippingPlanes(False)
		self.cleanUpCallbacks()

	def update(self):
		"""
		Updates the lookup tables of the slice planes (only if they are changed)
		"""
		volVis = self.widget.volumeVisualization
		from ui.visualizations.VolumeVisualization import VisualizationTypeSimple
		if volVis is None:
			if self._clippingPlanesState:
				self.showClippingPlanes(False)
			return
		elif volVis.visualizationType != VisualizationTypeSimple:
			for plane in self.planes:
				lookupTable = plane.GetLookupTable()
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
		"""
		Sets imagedata for vtkBoxWidget
		Sets imagedata for all the vtkImagePlaneWidgets
		"""
		self.imageData = imageData
		if self.imageData is None:
			self.showClippingBox(False)
			self.showClippingPlanes(False)
			return

		self.clippingBox.SetInputData(imageData)
		self.clippingBox.PlaceWidget()

		for plane in self.planes:
			plane.SetInputData(imageData)
			plane.PlaceWidget()
		
	def reset(self):
		"""
		Hides the vtkBoxWidget
		Hides the vtkImagePlaneWidgets
		Sets all input data to NULL
		Removes all vtkImagePlaneWidgets
		"""
		pass

	def resetClippingBox(self):
		"""
		Resets position and shape of the clipping box.
		"""
		# Reset the planes by setting identity transform
		transform = vtkTransform()
		self.clippingBox.SetTransform(transform)

		# Make sure the mapper is informed of the changes
		planes = vtkPlanes()
		self.clippingBox.GetPlanes(planes)
		self._updateMapperWithClippingPlanes(planes)

	def transformCallback(self, arg1, arg2):
		planes = vtkPlanes()
		arg1.GetPlanes(planes)
		self._updateMapperWithClippingPlanes(planes)

	# Private methods
		
	def _updateImagePlanePlacement(self):
		if not self._clippingPlanesState:
			return
		# First get the planes of the clipping box
		planes = vtkPlanes()
		self.clippingBox.GetPlanes(planes)

		# Also get the polydata of the box
		polyData = vtkPolyData()
		self.clippingBox.GetPolyData(polyData)

		# Append a 4th element to the polydata points
		p = []
		for i in range(8):
			p.append(list(polyData.GetPoint(i)) + [1.0])

		# Transform all the polydata points
		inv = self.transform.GetInverse()
		for i in range(len(p)):
			inv.MultiplyPoint(p[i], p[i])
			p[i] = p[i][0:3]
			
		# Calculate the center of the planes
		# so that it is possible to figure out where
		# to place the image planes
		center = [0, 0, 0]
		for point in p:
			center[0] += point[0]
			center[1] += point[1]
			center[2] += point[2]

		center[0] /= len(p)
		center[1] /= len(p)
		center[2] /= len(p)

		# Place the image plane just outside the clipping box
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

	def _updateMapperWithClippingPlanes(self, planes):
		self.widget.mapper.SetClippingPlanes(planes)
		self._updateImagePlanePlacement()
