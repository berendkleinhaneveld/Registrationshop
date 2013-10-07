"""
TwoStepPicker

:Authors:
	Berend Klein Haneveld
"""
from Picker import Picker
from core.decorators import overrides
from core.operations import *
from vtk import vtkLineSource
from vtk import vtkSphereSource
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkAssembly
from vtk import vtkProp3DFollower
from vtk import vtkMath
from vtk import vtkImageInterpolator
from PySide.QtCore import Signal


class TwoStepPicker(Picker):
	"""
	TwoStepPicker
	"""

	pickedLocation = Signal(list)

	def __init__(self):
		super(TwoStepPicker, self).__init__()
		self.props = []
		self.overlayProps = []
		self.lineActor = None

	def setPropertiesWidget(self, widget):
		self.propertiesWidget = widget

	@overrides(Picker)
	def setWidget(self, widget):
		self.widget = widget
		self.AddObserver(self.widget.rwi, "KeyPressEvent", self.keyPress)
		self.AddObserver(self.widget.rwi, "MouseMoveEvent", self.mouseMove)

	@overrides(Picker)
	def cleanUp(self):
		super(TwoStepPicker, self).cleanUp()
		if self.widget:
			for prop in self.props:
				self.widget.renderer.RemoveViewProp(prop)
			for prop in self.overlayProps:
				self.widget.rendererOverlay.RemoveViewProp(prop)

		self.props = []
		self.overlayProps = []
		self.lineActor = None
		if hasattr(self, "sphereSource"):
			del self.sphereSource

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
		a, b = ClosestPoints(lineSource.GetPoint1(), lineSource.GetPoint2(), q1, q2)
		if not hasattr(self, "sphereSource"):
			self.sphereSource = vtkSphereSource()
			self.sphereSource.SetRadius(20)
			sphereMapper = vtkDataSetMapper()
			sphereMapper.SetInputConnection(self.sphereSource.GetOutputPort())
			sphereActor = vtkActor()
			sphereActor.SetMapper(sphereMapper)
			sphereActor.GetProperty().SetColor(0.2, 1, 0.5)
			self.widget.renderer.AddViewProp(sphereActor)
			self.props.append(sphereActor)
			self._createLocator()
		self.sphereSource.SetCenter(a[0], a[1], a[2])
		self.assemblyFollower.SetPosition(a[0], a[1], a[2])
		self.widget.render()

	def keyPress(self, iren, event=""):
		"""
		vtk action callback
		"""
		key = iren.GetKeyCode()
		if key != "a":
			# if key == " ":
			# 	print "Hallelujah!"
			return
		x, y = iren.GetEventPosition()
		p1, p2 = rayForMouse(self.widget.renderer, x, y)
		if not self.lineActor:
			self._setLine(p1, p2)
		else:
			point = list(self.sphereSource.GetCenter())
			self.pickedLocation.emit(point)
			self.cleanUp()
			self.setWidget(self.widget)
			self.widget.render()

	def _setLine(self, point1, point2):
		# TODO: transform the points from the bounds
		bounds = self.widget.volume.GetBounds()
		# Cube has 8 corners, 6 sides, 12 triangles
		p0 = [bounds[0], bounds[2], bounds[4]]
		p1 = [bounds[1], bounds[2], bounds[4]]
		p2 = [bounds[0], bounds[3], bounds[4]]
		p3 = [bounds[0], bounds[2], bounds[5]]
		p4 = [bounds[1], bounds[3], bounds[4]]
		p5 = [bounds[0], bounds[3], bounds[5]]
		p6 = [bounds[1], bounds[2], bounds[5]]
		p7 = [bounds[1], bounds[3], bounds[5]]

		# For each triangle have to check intersection
		triangles = []
		triangles.append([p0, p1, p4])
		triangles.append([p0, p2, p4])
		triangles.append([p0, p2, p5])
		triangles.append([p0, p3, p5])
		triangles.append([p0, p1, p6])
		triangles.append([p0, p3, p6])
		triangles.append([p7, p6, p3])
		triangles.append([p7, p6, p3])
		triangles.append([p7, p5, p2])
		triangles.append([p7, p4, p2])
		triangles.append([p7, p6, p1])
		triangles.append([p7, p4, p1])

		result = map(lambda x: lineIntersectionWithTriangle(point1, point2, x), triangles)
		intersections = []
		for x in result:
			if x[0] is True:
				intersections.append(x[1])
		assert len(intersections) == 2 or len(intersections) == 0
		if len(intersections) == 2:
			self.lineActor = createLine(intersections[0], intersections[1])
			self.widget.renderer.AddViewProp(self.lineActor)
			self.props.append(self.lineActor)
			self.widget.render()

			ab = Subtract(intersections[1], intersections[0])
			abLength = Length(ab)
			abNorm = Normalize(ab)
			stepLength = abLength / 64.0
			abStep = Multiply(abNorm, stepLength)
			sampleLocations = [intersections[0]]
			for i in range(64):
				sampleLocations.append(Add(sampleLocations[i], abStep))
			interpolator = vtkImageInterpolator()
			interpolator.Initialize(self.widget.imageData)
			samples = []
			for i in range(len(sampleLocations)):
				loc = sampleLocations[i]
				samples.append(interpolator.Interpolate(loc[0], loc[1], loc[2], 0))
			self.propertiesWidget.setSamples(samples, self.widget.imageData.GetScalarRange())

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
		self.widget.rendererOverlay.AddViewProp(self.assemblyFollower)
		self.overlayProps.append(self.assemblyFollower)
		self.widget.render()


def lineIntersectionWithTriangle(pointA, pointB, triangle):
	"""
	Solve linear system for intersection with plane
	defined by plane through 3 points. If the first
	value of outVector is between 0 and 1, it is on the
	line between the 2 given points. If the other values
	of outVector are also between 0 and 1 and they add up
	to a max of 1, then the intersection is within the
	specified triangle.
	:rtype: bool, list(3)
	"""
	A = pointA
	B = pointB
	P0 = triangle[0]
	P1 = triangle[1]
	P2 = triangle[2]

	matrix = [[0 for x in range(3)] for x in range(3)]
	matrix[0][0] = A[0]-B[0]
	matrix[1][0] = A[1]-B[1]
	matrix[2][0] = A[2]-B[2]
	matrix[0][1] = P1[0]-P0[0]
	matrix[1][1] = P1[1]-P0[1]
	matrix[2][1] = P1[2]-P0[2]
	matrix[0][2] = P2[0]-P0[0]
	matrix[1][2] = P2[1]-P0[1]
	matrix[2][2] = P2[2]-P0[2]

	inVector = [0 for x in range(3)]
	inVector[0] = A[0] - P0[0]
	inVector[1] = A[1] - P0[1]
	inVector[2] = A[2] - P0[2]

	outVector = [0 for x in range(3)]
	vtkMath.LinearSolve3x3(matrix, inVector, outVector)

	intersectsTriangle = False
	if (outVector[0] >= 0 and outVector[0] <= 1
		and outVector[1] >= 0 and outVector[1] <= 1
		and outVector[2] >= 0 and outVector[2] <= 1
		and outVector[1] + outVector[2] <= 1):
		intersectsTriangle = True

	# intersection = Ia + (Ib - Ia)*t
	vec = Subtract(pointB, pointA)
	vec = Multiply(vec, outVector[0])
	intersection = Add(pointA, vec)
	return intersectsTriangle, intersection


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
