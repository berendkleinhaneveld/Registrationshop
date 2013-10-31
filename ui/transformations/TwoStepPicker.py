"""
TwoStepPicker

:Authors:
	Berend Klein Haneveld
"""
from Picker import Picker
from core.decorators import overrides
from core.operations import Multiply
from core.operations import Add
from core.operations import ClosestPoints
from core.operations import Subtract
from core.operations import LineIntersectionWithTriangle
from core.operations import Length
from core.operations import Normalize
from vtk import vtkLineSource
from vtk import vtkSphereSource
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkAssembly
from vtk import vtkTransform
from vtk import vtkProp3DFollower
from vtk import vtkMath
from vtk import vtkImageInterpolator
from PySide.QtCore import Signal
from PySide.QtCore import Slot


class TwoStepPicker(Picker):
	"""
	TwoStepPicker
	"""

	pickedLocation = Signal(list)
	locatorUpdated = Signal(float)

	def __init__(self):
		super(TwoStepPicker, self).__init__()

		self.props = []
		self.overlayProps = []
		self.lineActor = None
		self.sphereSource = None

	def setPropertiesWidget(self, widget):
		self.propertiesWidget = widget
		self.propertiesWidget.histogramWidget.updatedPosition.connect(self.histogramUpdatedPosition)
		self.locatorUpdated.connect(self.propertiesWidget.histogramWidget.locatorUpdated)
		self.propertiesWidget.pickedPosition.connect(self.pickedPosition)
		self.pickedLocation.connect(self.propertiesWidget.pickedLocation)

	@overrides(Picker)
	def setWidget(self, widget):
		self.widget = widget
		self.AddObserver(self.widget.rwi, "KeyPressEvent", self.keyPress)
		self.AddObserver(self.widget.rwi, "MouseMoveEvent", self.mouseMove)

	@overrides(Picker)
	def cleanUp(self):
		super(TwoStepPicker, self).cleanUp()
		
		for prop in self.props:
			self.widget.renderer.RemoveViewProp(prop)
		for prop in self.overlayProps:
			self.widget.rendererOverlay.RemoveViewProp(prop)

		self.props = []
		self.overlayProps = []
		self.lineActor = None
		self.sphereSource = None

	@Slot(float)
	def histogramUpdatedPosition(self, position):
		lineSource = self.lineActor.GetMapper().GetInputConnection(0, 0).GetProducer()
		p1 = lineSource.GetPoint1()
		p2 = lineSource.GetPoint2()
		part = Add(p2, Multiply(Subtract(p1, p2), position))
		if self.sphereSource:
			self.sphereSource.SetCenter(part[0], part[1], part[2])
		self.assemblyFollower.SetPosition(part[0], part[1], part[2])
		self.widget.render()

	def mouseMove(self, iren, event=""):
		"""
		vtk action callback
		"""
		if not self.lineActor:
			# TODO: show crosshair or some other thing instead of cursor
			self.widget.rwi.ShowCursor()
			return

		x, y = iren.GetEventPosition()
		lineSource = self.lineActor.GetMapper().GetInputConnection(0, 0).GetProducer()
		q1, q2 = rayForMouse(self.widget.renderer, x, y)
		p1 = lineSource.GetPoint1()  # Volume entry point
		p2 = lineSource.GetPoint2()  # Volume exit point
		a, b = ClosestPoints(p1, p2, q1, q2, clamp=True)
		if not self.sphereSource:
			self.sphereSource = vtkSphereSource()
			self.sphereSource.SetRadius(20)
			sphereMapper = vtkDataSetMapper()
			sphereMapper.SetInputConnection(self.sphereSource.GetOutputPort())
			sphereActor = vtkActor()
			sphereActor.SetMapper(sphereMapper)
			sphereActor.GetProperty().SetColor(0.2, 1, 0.5)
			self._addToRender(sphereActor)
			self._createLocator()
		self.sphereSource.SetCenter(a[0], a[1], a[2])
		self.assemblyFollower.SetPosition(a[0], a[1], a[2])
		lengthA = Length(Subtract(a, p2))
		lengthRay = Length(Subtract(p2, p1))
		self.locatorUpdated.emit(lengthA / lengthRay)
		self.widget.render()

	def keyPress(self, iren, event=""):
		"""
		vtk action callback
		"""
		key = iren.GetKeyCode()
		if key != "a":
			# if key == " ":
			# 	print "Pressed space"
			return
		x, y = iren.GetEventPosition()
		# p1 and p2 are in world coordination
		p1, p2 = rayForMouse(self.widget.renderer, x, y)
		if not self.lineActor:
			self._setLine(p1, p2)
		else:
			self._pickPosition()

	def _pickPosition(self):
		# point in world coordinates
		point = list(self.sphereSource.GetCenter())
		matrix = self.widget.volume.GetMatrix()
		transform = vtkTransform()
		transform.SetMatrix(matrix)
		transform.Inverse()
		# transformedPoint in local coordinates
		tranformedPoint = transform.TransformPoint(point)
		point = list(tranformedPoint)
		self.cleanUp()
		self.pickedLocation.emit(point)
		self.setWidget(self.widget)
		self.widget.render()

	def pickedPosition(self):
		"""
		Position is float between 0 and 1
		"""
		self._pickPosition()

	def _setLine(self, point1, point2):
		"""
		Input points should be world coordinates.
		"""
		bounds = list(self.widget.imageData.GetBounds())
		matrix = self.widget.volume.GetMatrix()
		transform = vtkTransform()
		transform.SetMatrix(matrix)

		# Create points for all of the corners of the bounds
		p = [[0 for x in range(3)] for x in range(8)]
		p[0] = [bounds[0], bounds[2], bounds[4]]
		p[1] = [bounds[1], bounds[2], bounds[4]]
		p[2] = [bounds[0], bounds[3], bounds[4]]
		p[3] = [bounds[0], bounds[2], bounds[5]]
		p[4] = [bounds[1], bounds[3], bounds[4]]
		p[5] = [bounds[0], bounds[3], bounds[5]]
		p[6] = [bounds[1], bounds[2], bounds[5]]
		p[7] = [bounds[1], bounds[3], bounds[5]]

		# Transform corner points
		tp = map(lambda x: list(transform.TransformPoint(x[0], x[1], x[2])), p)

		# Create triangles for each face of the cube
		triangles = []
		triangles.append([tp[0], tp[1], tp[4]])
		triangles.append([tp[0], tp[2], tp[4]])
		triangles.append([tp[0], tp[2], tp[5]])
		triangles.append([tp[0], tp[3], tp[5]])
		triangles.append([tp[0], tp[1], tp[6]])
		triangles.append([tp[0], tp[3], tp[6]])
		triangles.append([tp[7], tp[6], tp[3]])
		triangles.append([tp[7], tp[5], tp[3]])
		triangles.append([tp[7], tp[5], tp[2]])
		triangles.append([tp[7], tp[4], tp[2]])
		triangles.append([tp[7], tp[6], tp[1]])
		triangles.append([tp[7], tp[4], tp[1]])

		# Check intersection for each triangle
		result = map(lambda x: LineIntersectionWithTriangle(point1, point2, x), triangles)
		intersections = [x[1] for x in result if x[0]]
		assert len(intersections) == 2 or len(intersections) == 0

		if len(intersections) == 2:
			# Draw line in renderer and in overlay renderer in world coordinates
			self.lineActor = createLine(intersections[0], intersections[1])
			self._addToRender(self.lineActor)
			self.lineActorOverlay = createLine(intersections[0], intersections[1])
			self.lineActorOverlay.GetProperty().SetColor(1.0, 1.0, 1.0)
			self.lineActorOverlay.GetProperty().SetOpacity(0.5)
			self.lineActorOverlay.GetProperty().SetLineStipplePattern(0xf0f0)
			self.lineActorOverlay.GetProperty().SetLineStippleRepeatFactor(1)
			self._addToOverlay(self.lineActorOverlay)
			# Note: the line has no transformation, so it will not update
			# together with the transformation of the volume.

			self.widget.render()

			# Sample volume for ray profile
			# Should be done in local coordinates, so the intersections
			# have to be transformed again
			transform.Inverse()
			localIntersections = map(lambda x: list(transform.TransformPoint(x[0], x[1], x[2])), intersections)
			ab = Subtract(localIntersections[0], localIntersections[1])
			abLength = Length(ab)
			abNorm = Normalize(ab)
			nrOfSteps = 128
			stepLength = abLength / float(nrOfSteps)
			abStep = Multiply(abNorm, stepLength)
			sampleLocations = [localIntersections[1]]
			for i in range(nrOfSteps):
				sampleLocations.append(Add(sampleLocations[i], abStep))
			interpolator = vtkImageInterpolator()
			interpolator.Initialize(self.widget.imageData)
			samples = []
			for i in range(len(sampleLocations)):
				loc = sampleLocations[i]
				samples.append(interpolator.Interpolate(loc[0], loc[1], loc[2], 0))
			self.propertiesWidget.setSamples(samples, self.widget.imageData.GetScalarRange())

	def _addToRender(self, prop):
		self.widget.renderer.AddViewProp(prop)
		self.props.append(prop)

	def _addToOverlay(self, prop):
		self.widget.rendererOverlay.AddViewProp(prop)
		self.overlayProps.append(prop)

	def _createLocator(self):
		halfSize = 25
		gapSize = 15

		upLine = createLine([0, gapSize, 0], [0, gapSize+halfSize, 0])
		downLine = createLine([0, -gapSize, 0], [0, -(gapSize+halfSize), 0])
		rightLine = createLine([gapSize, 0, 0], [gapSize+halfSize, 0, 0])
		leftLine = createLine([-gapSize, 0, 0], [-(gapSize+halfSize), 0, 0])

		assembly = vtkAssembly()
		assembly.AddPart(upLine)
		assembly.AddPart(downLine)
		assembly.AddPart(leftLine)
		assembly.AddPart(rightLine)

		self.assemblyFollower = vtkProp3DFollower()
		self.assemblyFollower.SetProp3D(assembly)
		self.assemblyFollower.SetCamera(self.widget.renderer.GetActiveCamera())
		self._addToOverlay(self.assemblyFollower)

		self.widget.render()


def createLine(p1, p2):
	lineSource = vtkLineSource()
	lineSource.SetPoint1(p1[0], p1[1], p1[2])
	lineSource.SetPoint2(p2[0], p2[1], p2[2])

	lineMapper = vtkDataSetMapper()
	lineMapper.SetInputConnection(lineSource.GetOutputPort())

	lineActor = vtkActor()
	lineActor.SetMapper(lineMapper)
	return lineActor


def rayForMouse(renderer, selectionX, selectionY):
	"""
	Code taken from vtkPicker::Pick()
	Returns two points in world coordination.
	"""
	# Get camera focal point and position. Convert to display (screen)
	# coordinates. We need a depth value for z-buffer.
	camera = renderer.GetActiveCamera()
	camPosition = list(camera.GetPosition())
	camPosition.append(1.0)
	cameraFP = list(camera.GetFocalPoint())
	cameraFP.append(1.0)
	renderer.SetWorldPoint(cameraFP[0], cameraFP[1], cameraFP[2], cameraFP[3])
	renderer.WorldToDisplay()
	displayCoords = renderer.GetDisplayPoint()
	selectionZ = displayCoords[2]

	# Convert the selection point into world coordinates.
	renderer.SetDisplayPoint(selectionX, selectionY, selectionZ)
	renderer.DisplayToWorld()
	worldCoords = renderer.GetWorldPoint()
	pickPosition = []
	for index in range(3):
		pickPosition.append(worldCoords[index] / worldCoords[3])

	# Compute the ray endpoints.  The ray is along the line running from
	# the camera position to the selection point, starting where this line
	# intersects the front clipping plane, and terminating where this
	# line intersects the back clipping plane.
	ray = []
	for index in range(3):
		ray.append(pickPosition[index] - camPosition[index])
	cameraDOP = []
	for index in range(3):
		cameraDOP.append(cameraFP[index] - camPosition[index])

	vtkMath.Normalize(cameraDOP)
	rayLength = vtkMath.Dot(cameraDOP, ray)

	clipRange = camera.GetClippingRange()
	tF = clipRange[0] / rayLength
	tB = clipRange[1] / rayLength
	p1World = []
	p2World = []
	for index in range(3):
		p1World.append(camPosition[index] + tF*ray[index])
		p2World.append(camPosition[index] + tB*ray[index])

	# TODO: clip the line just outside the volume
	return p1World, p2World
