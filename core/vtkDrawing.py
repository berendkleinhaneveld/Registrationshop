"""
vtkDrawing

Convenience methods for creating simple vtk objects
that can be used in renderers.
Call one of the methods with some custom parameters
and out comes a vtkActor that can be given to a
renderer with AddViewProp().

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkActor
from vtk import vtkVectorText
from vtk import vtkLineSource
from vtk import vtkSphereSource
from vtk import vtkRegularPolygonSource
from vtk import vtkDataSetMapper
from vtk import vtkPolyDataMapper
from vtk import vtkFollower
from vtk import vtkAssembly
from vtk import vtkMatrix4x4
from vtk import vtkTransform
from vtk import vtkOutlineSource
from vtk import vtkConeSource
from vtk import vtkParametricTorus
from vtk import vtkParametricFunctionSource
from vtk import vtkTubeFilter
from vtk import vtkAppendPolyData
from vtk import vtkCubeSource
from vtk import vtkTransformFilter
import math
from core.operations import Add
from core.operations import Subtract
from core.operations import Multiply


def TransformWithMatrix(matrix):
	"""
	Return matrix with a copy of the given matrix.
	"""
	matrixCopy = vtkMatrix4x4()
	matrixCopy.DeepCopy(matrix)

	transform = vtkTransform()
	transform.SetMatrix(matrixCopy)

	return transform


def ColorActor(actor, color, opacity=None):
	"""
	Give the actor a custom color and / or opacity.
	"""
	if color:
		actor.GetProperty().SetColor(color[0], color[1], color[2])
	if opacity:
		actor.GetProperty().SetOpacity(opacity)


def CreateLine(p1, p2, color=None):
	"""
	Creates a line between p1 and p2.
	"""
	lineSource = vtkLineSource()
	lineSource.SetPoint1(p1[0], p1[1], p1[2])
	lineSource.SetPoint2(p2[0], p2[1], p2[2])

	lineMapper = vtkDataSetMapper()
	lineMapper.SetInputConnection(lineSource.GetOutputPort())

	lineActor = vtkActor()
	lineActor.SetMapper(lineMapper)

	# Give the actor a custom color
	ColorActor(lineActor, color)

	return lineActor


def CreateLineBeginAndEnd(p1, p2, length, color=None):
	"""
	Length is value between 0 and 0.5 to specify how long
	each begin and end part is compared to the complete line.
	:rtype: list of line actors
	"""
	point1 = p1
	point2 = Add(p1, Multiply(Subtract(p2, p1), length))
	point3 = p2
	point4 = Add(p2, Multiply(Subtract(p1, p2), length))

	line1 = CreateLine(point1, point2, color)
	line2 = CreateLine(point3, point4, color)

	return [line1, line2]


def CreateSphere(radius, color=None):
	sphereSource = vtkSphereSource()
	sphereSource.SetRadius(radius)
	sphereSource.SetThetaResolution(18)
	sphereSource.SetPhiResolution(18)

	sphereMapper = vtkPolyDataMapper()
	sphereMapper.SetInputConnection(sphereSource.GetOutputPort())

	sphereActor = vtkActor()
	sphereActor.PickableOff()
	sphereActor.SetMapper(sphereMapper)

	# Give the actor a custom color
	ColorActor(sphereActor, color)

	# Also give the sphere object the convenience methods of
	# SetCenter() and GetCenter() that misses from the vtkActor
	# class but is present in the vtkSphereSource class
	def setCenter(x, y, z):
		sphereSource.SetCenter(x, y, z)

	def getCenter():
		return sphereSource.GetCenter()

	setattr(sphereActor, "SetCenter", setCenter)
	setattr(sphereActor, "GetCenter", getCenter)

	return sphereActor


def CreateTextItem(text, scale, camera, color=None):
	textSource = vtkVectorText()
	textSource.SetText(text)

	textMapper = vtkPolyDataMapper()
	textMapper.SetInputConnection(textSource.GetOutputPort())

	textFollower = vtkFollower()
	textFollower.SetMapper(textMapper)
	textFollower.SetCamera(camera)
	textFollower.SetScale(scale)

	# Give the actor a custom color
	ColorActor(textFollower, color)

	return textFollower


def CreateCircle(radius):
	circleSource = vtkRegularPolygonSource()
	circleSource.SetNumberOfSides(32)
	circleSource.SetRadius(radius)
	circleSource.SetGeneratePolygon(False)

	circleMapper = vtkPolyDataMapper()
	circleMapper.SetInputConnection(circleSource.GetOutputPort())

	circle = vtkActor()
	circle.PickableOff()
	circle.SetMapper(circleMapper)
	circle.GetProperty().SetColor(1.0, 0.5, 0.5)

	return circle


def CreateSquare(width, color=None, zOffset=0):
	halfWidth = width / 2.0
	squareSource = vtkOutlineSource()
	squareSource.GenerateFacesOff()
	squareSource.SetBounds(-halfWidth, halfWidth, -halfWidth, halfWidth, zOffset, zOffset)

	squareMapper = vtkPolyDataMapper()
	squareMapper.SetInputConnection(squareSource.GetOutputPort())

	square = vtkActor()
	square.PickableOff()
	square.SetMapper(squareMapper)
	square.GetProperty().SetColor(1.0, 0.5, 0.5)

	ColorActor(square, color)

	return square


def CreateTorus(point1, point2, axe):
	"""
	Creates a torus that has point1 as center point2 defines
	a point on the torus.
	"""
	direction = map(lambda x, y: x - y, point2, point1)
	length = math.sqrt(sum(map(lambda x: x ** 2, direction)))

	torus = vtkParametricTorus()
	torus.SetRingRadius(length / 1.5)
	torus.SetCrossSectionRadius(length / 30.0)

	torusSource = vtkParametricFunctionSource()
	torusSource.SetParametricFunction(torus)
	torusSource.SetScalarModeToPhase()
	torusSource.Update()

	transform = vtkTransform()
	if axe == 0:
		transform.RotateY(90)
	elif axe == 1:
		transform.RotateX(90)

	transformFilter = vtkTransformFilter()
	transformFilter.SetInputConnection(torusSource.GetOutputPort())
	transformFilter.SetTransform(transform)
	transformFilter.Update()

	torusMapper = vtkPolyDataMapper()
	torusMapper.SetInputConnection(transformFilter.GetOutputPort())

	torusActor = vtkActor()
	torusActor.SetMapper(torusMapper)

	return torusActor, transformFilter.GetOutput()


def CreateBoxOnStick(point1, point2, tipRatio=0.3):
	"""
	Creates an stick with a box as tip from point1 to point2.
	Use tipRatio for setting the ratio for tip of the arrow.
	"""
	direction = map(lambda x, y: x - y, point2, point1)
	length = math.sqrt(sum(map(lambda x: x ** 2, direction)))

	unitDir = map(lambda x: x / length, direction)
	shaftDir = map(lambda x: x * (1.0 - tipRatio), unitDir)
	tipPos = map(lambda x: x * (1.0 - (tipRatio * 0.5)), unitDir)

	lineSource = vtkLineSource()
	lineSource.SetPoint1(0, 0, 0)
	lineSource.SetPoint2(shaftDir)

	tubeFilter = vtkTubeFilter()
	tubeFilter.SetInputConnection(lineSource.GetOutputPort())
	tubeFilter.SetRadius(0.02)
	tubeFilter.SetNumberOfSides(8)
	tubeFilter.CappingOn()

	cubeSource = vtkCubeSource()
	# cubeSource.CappingOn()
	cubeSource.SetXLength(tipRatio)
	cubeSource.SetYLength(tipRatio)
	cubeSource.SetZLength(tipRatio)
	cubeSource.SetCenter(tipPos)

	polyCombine = vtkAppendPolyData()
	polyCombine.AddInputConnection(tubeFilter.GetOutputPort())
	polyCombine.AddInputConnection(cubeSource.GetOutputPort())
	polyCombine.Update()

	polyMapper = vtkDataSetMapper()
	polyMapper.SetInputConnection(polyCombine.GetOutputPort())

	arrow = vtkActor()
	arrow.SetMapper(polyMapper)
	arrow.SetScale(length)
	arrow.SetPosition(point1)
	arrow.GetProperty().SetColor(1.0, 0.0, 1.0)

	return arrow, polyCombine.GetOutput()


def CreateArrow(point1, point2, tipRatio=0.3):
	"""
	Creates an arrow from point1 to point2. Use tipRatio for
	setting the ratio for tip of the arrow.
	"""
	direction = map(lambda x, y: x - y, point2, point1)
	length = math.sqrt(sum(map(lambda x: x ** 2, direction)))

	unitDir = map(lambda x: x / length, direction)
	shaftDir = map(lambda x: x * (1.0 - tipRatio), unitDir)
	tipPos = map(lambda x: x * (1.0 - (tipRatio * 0.5)), unitDir)

	lineSource = vtkLineSource()
	lineSource.SetPoint1(0, 0, 0)
	lineSource.SetPoint2(shaftDir)

	tubeFilter = vtkTubeFilter()
	tubeFilter.SetInputConnection(lineSource.GetOutputPort())
	tubeFilter.SetRadius(0.02)
	tubeFilter.SetNumberOfSides(8)
	tubeFilter.CappingOn()

	coneSource = vtkConeSource()
	coneSource.CappingOn()
	coneSource.SetHeight(tipRatio)
	coneSource.SetRadius(.2)
	coneSource.SetResolution(16)
	coneSource.SetCenter(tipPos)
	coneSource.SetDirection(tipPos)

	polyCombine = vtkAppendPolyData()
	polyCombine.AddInputConnection(tubeFilter.GetOutputPort())
	polyCombine.AddInputConnection(coneSource.GetOutputPort())
	polyCombine.Update()

	polyMapper = vtkDataSetMapper()
	polyMapper.SetInputConnection(polyCombine.GetOutputPort())

	arrow = vtkActor()
	arrow.SetMapper(polyMapper)
	arrow.SetScale(length)
	arrow.SetPosition(point1)
	arrow.GetProperty().SetColor(1.0, 0.0, 1.0)

	return arrow, polyCombine.GetOutput()


def CreateOutline(bounds, color=None):
	squareSource = vtkOutlineSource()
	squareSource.GenerateFacesOff()
	squareSource.SetBounds(bounds)

	squareMapper = vtkPolyDataMapper()
	squareMapper.SetInputConnection(squareSource.GetOutputPort())

	square = vtkActor()
	square.PickableOff()
	square.SetMapper(squareMapper)
	square.GetProperty().SetColor(1.0, 1.0, 1.0)

	ColorActor(square, color)

	return square


def CreateBounds(bounds):
	"""
	Creates a boundary object to display around a volume.
	:rtype: list of actors
	"""
	originX = bounds[0]
	originY = bounds[2]
	originZ = bounds[4]
	boundX = bounds[1]
	boundY = bounds[3]
	boundZ = bounds[5]

	linePartLength = 0.2

	lineActors = []
	lineActors += CreateLineBeginAndEnd([originX, originY, originZ], [boundX, originY, originZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([originX, originY, originZ], [originX, boundY, originZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([originX, originY, originZ], [originX, originY, boundZ], linePartLength)

	ColorActor(lineActors[0], [1, 0, 0])
	ColorActor(lineActors[2], [0, 1, 0])
	ColorActor(lineActors[4], [0, 0, 1])

	lineActors += CreateLineBeginAndEnd([boundX, boundY, boundZ], [boundX, boundY, originZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([boundX, boundY, boundZ], [originX, boundY, boundZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([boundX, boundY, boundZ], [boundX, originY, boundZ], linePartLength)

	lineActors += CreateLineBeginAndEnd([boundX, originY, originZ], [boundX, originY, boundZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([boundX, originY, originZ], [boundX, boundY, originZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([originX, boundY, originZ], [originX, boundY, boundZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([originX, boundY, originZ], [boundX, boundY, originZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([originX, originY, boundZ], [originX, boundY, boundZ], linePartLength)
	lineActors += CreateLineBeginAndEnd([originX, originY, boundZ], [boundX, originY, boundZ], linePartLength)

	for lineActor in lineActors:
		ColorActor(lineActor, color=None, opacity=0.5)

	mean = reduce(lambda x, y: x + y, bounds) / 3.0
	sphereActor = CreateSphere(mean / 25.0)
	sphereActor.SetPosition(originX, originY, originZ)

	dataGrid = vtkAssembly()
	for lineActor in lineActors:
		dataGrid.AddPart(lineActor)

	return [dataGrid, sphereActor]


def CreateOrientationGrid(bounds, camera):
	return []
	originX = bounds[0]
	originY = bounds[2]
	originZ = bounds[4]
	boundX = bounds[1] * 1.2
	boundY = bounds[3] * 1.2
	boundZ = bounds[5] * 1.2

	lineActorsX = []
	lineActorsY = []
	lineActorsZ = []

	lineText = []

	# Create the main axes
	lineActorsX.append(CreateLine([0, 0, 0], [boundX, 0, 0]))
	lineActorsX.append(CreateLine([0, 0, 0], [originX, 0, 0]))
	lineActorsY.append(CreateLine([0, 0, 0], [0, boundY, 0]))
	lineActorsY.append(CreateLine([0, 0, 0], [0, originY, 0]))
	lineActorsZ.append(CreateLine([0, 0, 0], [0, 0, boundZ]))
	lineActorsZ.append(CreateLine([0, 0, 0], [0, 0, originZ]))

	# Create the nudges on the X axis
	subdivSize = boundX / 10
	subdivSize = ClosestToMeasurement(subdivSize)
	smallHandleSize = subdivSize / 5.0
	bigHandleSize = 2 * smallHandleSize

	for index in range(1, int(boundX / subdivSize)):
		handleSize = smallHandleSize if index % 5 != 0 else bigHandleSize
		lineActorsX.append(CreateLine([index * subdivSize, 0, 0], [index * subdivSize, handleSize, 0]))
		lineActorsX.append(CreateLine([index * subdivSize, 0, 0], [index * subdivSize, 0, handleSize]))
		if index > 0 and index % 5 == 0:
			textItem = CreateTextItem(str(index * subdivSize), 0.4 * subdivSize, camera)
			textItem.SetPosition([index * subdivSize, -handleSize, -handleSize])
			ColorActor(textItem, color=[0.6, 0.6, 0.6])
			lineText.append(textItem)

	textItemX = CreateTextItem("X", 0.5 * subdivSize, camera)
	textItemX.SetPosition([boundX, 0, 0])

	# Create the nudges on the Y axis
	subdivSize = boundY / 10
	subdivSize = ClosestToMeasurement(subdivSize)
	smallHandleSize = subdivSize / 5.0

	for index in range(1, int(boundY / subdivSize)):
		handleSize = smallHandleSize if index % 5 != 0 else bigHandleSize
		lineActorsY.append(CreateLine([0, index * subdivSize, 0], [handleSize, index * subdivSize, 0]))
		lineActorsY.append(CreateLine([0, index * subdivSize, 0], [0, index * subdivSize, handleSize]))
		if index > 0 and index % 5 == 0:
			textItem = CreateTextItem(str(index * subdivSize), 0.4 * subdivSize, camera)
			textItem.SetPosition([-smallHandleSize, index * subdivSize, -smallHandleSize])
			ColorActor(textItem, color=[0.6, 0.6, 0.6])
			lineText.append(textItem)

	textItemY = CreateTextItem("Y", 0.5 * subdivSize, camera)
	textItemY.SetPosition([0, boundY, 0])

	# Create the nudges on the Z axis
	subdivSize = boundZ / 10
	subdivSize = ClosestToMeasurement(subdivSize)
	smallHandleSize = subdivSize / 5.0

	for index in range(1, int(boundZ / subdivSize)):
		handleSize = smallHandleSize if index % 5 != 0 else bigHandleSize
		lineActorsZ.append(CreateLine([0, 0, index * subdivSize], [handleSize, 0, index * subdivSize]))
		lineActorsZ.append(CreateLine([0, 0, index * subdivSize], [0, handleSize, index * subdivSize]))
		if index > 0 and index % 5 == 0:
			textItem = CreateTextItem(str(index * subdivSize), 0.4 * subdivSize, camera)
			textItem.SetPosition([-handleSize, -handleSize, index * subdivSize])
			ColorActor(textItem, color=[0.6, 0.6, 0.6])
			lineText.append(textItem)

	textItemZ = CreateTextItem("Z", 0.5 * subdivSize, camera)
	textItemZ.SetPosition([0, 0, boundZ])

	# Color the axis: R, G and B
	for lineActor in lineActorsX:
		ColorActor(lineActor, [1, 0, 0])
	for lineActor in lineActorsY:
		ColorActor(lineActor, [0, 1, 0])
	for lineActor in lineActorsZ:
		ColorActor(lineActor, [0, 0, 1])

	# Add the lines into one big assembly
	dataGrid = vtkAssembly()
	for lineActor in (lineActorsX + lineActorsY + lineActorsZ):
		dataGrid.AddPart(lineActor)

	return [dataGrid, textItemX, textItemY, textItemZ] + lineText


def ClosestToMeasurement(number):
	# gridNudges describes the possible values for indicator intervals for the grid
	gridNudges = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]

	# Calculate diff
	diff = map(lambda x: abs(x - number), gridNudges)
	index = diff.index(min(diff))
	return gridNudges[index]
