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
from core.vtkDrawing import CreateSphere
from core.vtkDrawing import CreateLine
from core.vtkDrawing import TransformWithMatrix
from vtk import vtkAssembly
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
		self.samples = None
		self.sampleDiffs = None

	def setPropertiesWidget(self, widget):
		self.propertiesWidget = widget.twoStepWidget
		self.propertiesWidget.histogramWidget.updatedPosition.connect(self.histogramUpdatedPosition)
		self.locatorUpdated.connect(self.propertiesWidget.histogramWidget.locatorUpdated)
		self.propertiesWidget.pickedPosition.connect(self.pickedPosition)
		self.pickedLocation.connect(self.propertiesWidget.pickedLocation)

	@overrides(Picker)
	def setWidget(self, widget):
		self.widget = widget
		self.AddObserver(self.widget.rwi, "MouseMoveEvent", self.mouseMove)
		self.AddObserver(self.widget.rwi, "KeyPressEvent", self.keyPress)

	@overrides(Picker)
	def cleanUp(self):
		super(TwoStepPicker, self).cleanUp()
		self.cleanUpProps()

	def cleanUpProps(self):
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
		if not self.lineActor:
			return
		lineSource = self.lineActor.GetMapper().GetInputConnection(0, 0).GetProducer()
		p1 = lineSource.GetPoint1()
		p2 = lineSource.GetPoint2()
		part = Add(p1, Multiply(Subtract(p2, p1), position))
		self.sphereSource.SetCenter(part[0], part[1], part[2])
		self.assemblyFollower.SetPosition(part[0], part[1], part[2])
		self.widget.render()

	def camPosition(self):
		return self.widget.renderer.GetActiveCamera().GetPosition()

	def mouseMove(self, iren, event=""):
		"""
		vtk action callback
		"""
		if not self.lineActor:
			# TODO: show crosshair or some other thing instead of cursor
			self.widget.rwi.ShowCursor()
			return

		x, y = iren.GetEventPosition()
		q1, q2 = rayForMouse(self.widget.renderer, x, y)
		lineSource = self.lineActor.GetMapper().GetInputConnection(0, 0).GetProducer()
		p1 = lineSource.GetPoint1()  # Volume entry point
		p2 = lineSource.GetPoint2()  # Volume exit point
		# location is the closest point on the drawn line
		location, other = ClosestPoints(p1, p2, q1, q2, clamp=True)

		lengthToLocation = Length(Subtract(location, p1))
		lengthRay = Length(Subtract(p2, p1))
		locationRatio = lengthToLocation / lengthRay

		# If shift key is pushed in, try to snap to logical points along the ray
		if iren.GetShiftKey() != 0:
			# Get the index of the sample that is closest to the point on the ray
			sampleIndex = int(len(self.sampleDiffs) * locationRatio)
			# Sample size is the amount of samples before and after the sample index
			# that are going to be analyzed
			sampleSize = 10
			# Calculate the lower and upper bound index
			lowerBoundIndex = max(0, sampleIndex-sampleSize)
			upperBoundIndex = min(len(self.sampleDiffs), sampleIndex+sampleSize)
			samples = self.sampleDiffs[lowerBoundIndex:upperBoundIndex]
			# Create a penalty for the local samples that gives penalties to samples
			# that lay further away from the mouse
			penalty = [(sampleSize + 1) / float(1 + abs(i-sampleSize)) for i in range(2*sampleSize+1)]
			offset = lowerBoundIndex - (sampleIndex - sampleSize)
			resamples = []
			for i in range(len(samples)):
				resamples.append(samples[i] * penalty[i+offset])
			maxIndex = resamples.index(max(resamples))

			# lowerBoundIndex is the index of where the sampling starts
			# maxIndex is number that counts from the lowerBoundIndex
			locationIndex = lowerBoundIndex + maxIndex
			locationRatio = locationIndex / float(len(self.sampleDiffs))
			location = Add(p1, Multiply(Subtract(p2, p1), locationRatio))

		if not self.sphereSource:
			bounds = self.widget.imageData.GetBounds()
			sizes = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
			smallest = min(sizes)
			scale = smallest / 30
			self.sphereSource = CreateSphere(scale, [0.2, 1, 0.5])
			self._addToRender(self.sphereSource)
			self._createLocator()

		self.sphereSource.SetCenter(location[0], location[1], location[2])
		self.assemblyFollower.SetPosition(location[0], location[1], location[2])
		self.locatorUpdated.emit(locationRatio)
		self.widget.render()

	def keyPress(self, iren, event=""):
		"""
		vtk action callback
		"""
		key = iren.GetKeyCode()
		if key != "a" and key != " ":
			# if key == " ":
			# 	print "Pressed space"
			return
		x, y = iren.GetEventPosition()
		# p1 and p2 are in world coordination
		p1, p2 = rayForMouse(self.widget.renderer, x, y)
		camPos = self.camPosition()
		q1, q2 = sortedLocations(p1, p2, camPos)
		if not self.lineActor:
			self._setLine(q1, q2)
		else:
			self._pickPosition()

	def _pickPosition(self):
		# point in world coordinates
		point = list(self.sphereSource.GetCenter())
		transform = TransformWithMatrix(self.widget.volume.GetMatrix())
		transform.Inverse()
		# transformedPoint in local coordinates
		tranformedPoint = transform.TransformPoint(point)
		point = list(tranformedPoint)
		self.cleanUpProps()
		self.pickedLocation.emit(point)
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
		transform = TransformWithMatrix(self.widget.volume.GetMatrix())

		intersections = intersectionsWithBounds(bounds, transform, point1, point2)
		if not intersections:
			return

		sortedIntersections = sortedLocations(intersections[0], intersections[1], self.camPosition())

		# Draw line in renderer and in overlay renderer in world coordinates
		self.lineActor = CreateLine(sortedIntersections[0], sortedIntersections[1])
		self._addToRender(self.lineActor)
		self.lineActorOverlay = CreateLine(sortedIntersections[0], sortedIntersections[1])
		self.lineActorOverlay.GetProperty().SetColor(1.0, 1.0, 1.0)
		self.lineActorOverlay.GetProperty().SetOpacity(0.5)
		self.lineActorOverlay.GetProperty().SetLineStipplePattern(0xf0f0)
		self.lineActorOverlay.GetProperty().SetLineStippleRepeatFactor(1)
		self._addToOverlay(self.lineActorOverlay)
		self.widget.render()

		# Sample volume for ray profile: should be done in local coordinates, so the intersections
		# have to be transformed again
		transform.Inverse()
		localIntersects = map(lambda x: list(transform.TransformPoint(x[0], x[1], x[2])), sortedIntersections)
		# ab is vector pointing from localIntersects[0] to localIntersects[1]
		ab = Subtract(localIntersects[1], localIntersects[0])
		abLength = Length(ab)
		nrOfSteps = 256  # TODO: make this number dependent on data size and length of vector
		stepLength = abLength / float(nrOfSteps)
		abNorm = Normalize(ab)
		abStep = Multiply(abNorm, stepLength)
		sampleLoc = localIntersects[0]

		interpolator = vtkImageInterpolator()
		interpolator.Initialize(self.widget.imageData)
		self.samples = []
		for i in range(nrOfSteps + 1):
			# Get sample from volume
			self.samples.append(interpolator.Interpolate(sampleLoc[0], sampleLoc[1], sampleLoc[2], 0))
			# Update the sampling position
			sampleLoc = Add(sampleLoc, abStep)

		self.propertiesWidget.setSamples(self.samples, self.widget.imageData.GetScalarRange())
		self._analyzeSamples(self.samples)

	def _addToRender(self, prop):
		self.widget.renderer.AddViewProp(prop)
		self.props.append(prop)

	def _addToOverlay(self, prop):
		self.widget.rendererOverlay.AddViewProp(prop)
		self.overlayProps.append(prop)

	def _createLocator(self):
		bounds = self.widget.imageData.GetBounds()
		sizes = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
		smallest = min(sizes)
		multiplier = smallest / 30
		halfSize = 4 * multiplier
		gapSize = 2 * multiplier

		upLine = CreateLine([0, gapSize, 0], [0, gapSize+halfSize, 0])
		downLine = CreateLine([0, -gapSize, 0], [0, -(gapSize+halfSize), 0])
		rightLine = CreateLine([gapSize, 0, 0], [gapSize+halfSize, 0, 0])
		leftLine = CreateLine([-gapSize, 0, 0], [-(gapSize+halfSize), 0, 0])

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

	def _analyzeSamples(self, samples):
		self.sampleDiffs = []
		for index in range(len(samples)-1):
			sample = samples[index]
			nextSample = samples[index+1]
			self.sampleDiffs.append(abs(nextSample - sample))


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


def sortedLocations(p1, p2, camPos):
	# Sort q1 and q2 based on camera position
	# Calculate distance between the two points and the camera
	diff1 = Subtract(p1, camPos)
	diff2 = Subtract(p2, camPos)
	len1 = Length(diff1)
	len2 = Length(diff2)

	if len1 < len2:
		return p1, p2
	else:
		return p2, p1


def intersectionsWithBounds(bounds, transform, point1, point2):
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
		return intersections
	else:
		return None
