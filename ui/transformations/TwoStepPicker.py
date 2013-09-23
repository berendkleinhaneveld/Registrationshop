"""
TwoStepPicker

:Authors:
	Berend Klein Haneveld
"""
from ui.Interactor import Interactor
from vtk import vtkLineSource
from vtk import vtkSphereSource
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkAssembly
from vtk import vtkProp3DFollower
from vtk import vtkMath
from PySide.QtCore import QObject
from PySide.QtCore import Signal


class TwoStepPicker(QObject, Interactor):
	"""
	TwoStepPicker
	"""

	pickedLocation = Signal(list)

	def __init__(self):
		super(TwoStepPicker, self).__init__()
		self.props = []
		self.overlayProps = []
		self.lines = []

	def setWidget(self, widget):
		self.widget = widget
		self.AddObserver(self.widget.rwi, "KeyPressEvent", self.keyPress)
		self.AddObserver(self.widget.rwi, "MouseMoveEvent", self.mouseMove)

	def cleanUp(self):
		if self.widget:
			for prop in self.props:
				self.widget.renderer.RemoveViewProp(prop)
			for prop in self.overlayProps:
				self.widget.overlayRenderer.RemoveViewProp(prop)
		self.cleanUpCallbacks()

		self.props = []
		self.overlayProps = []
		self.lines = []
		if hasattr(self, "sphereSource"):
			del self.sphereSource

	def addLine(self, point1, point2):
		lineSource = vtkLineSource()
		lineSource.SetPoint1(point1[0], point1[1], point1[2])
		lineSource.SetPoint2(point2[0], point2[1], point2[2])

		lineMapper = vtkDataSetMapper()
		lineMapper.SetInputConnection(lineSource.GetOutputPort())

		lineActor = vtkActor()
		lineActor.PickableOff()
		lineActor.SetMapper(lineMapper)
		lineActor.GetProperty().SetColor(1, 0, 0)

		self.widget.renderer.AddViewProp(lineActor)
		self.props.append(lineActor)
		self.lines.append(lineSource)
		self.widget.render()

	def createLine(self, p1, p2):
		lineSource = vtkLineSource()
		lineSource.SetPoint1(p1[0], p1[1], p1[2])
		lineSource.SetPoint2(p2[0], p2[1], p2[2])
		lineMapper = vtkDataSetMapper()
		lineMapper.SetInputConnection(lineSource.GetOutputPort())
		lineActor = vtkActor()
		lineActor.SetMapper(lineMapper)
		return lineActor

	def createLocator(self):
		halfSize = 25
		gapSize = 15

		upLine = self.createLine([0, gapSize, 0], [0, gapSize+halfSize, 0])
		downLine = self.createLine([0, -gapSize, 0], [0, -(gapSize+halfSize), 0])
		rightLine = self.createLine([gapSize, 0, 0], [gapSize+halfSize, 0, 0])
		leftLine = self.createLine([-gapSize, 0, 0], [-(gapSize+halfSize), 0, 0])

		assembly = vtkAssembly()
		assembly.AddPart(upLine)
		assembly.AddPart(downLine)
		assembly.AddPart(leftLine)
		assembly.AddPart(rightLine)

		self.assemblyFollower = vtkProp3DFollower()
		self.assemblyFollower.SetProp3D(assembly)
		self.assemblyFollower.SetCamera(self.widget.overlayRenderer.GetActiveCamera())
		self.widget.overlayRenderer.AddViewProp(self.assemblyFollower)
		self.overlayProps.append(self.assemblyFollower)
		self.widget.render()

	def closestPoints(self, p1, p2, q1, q2):
		"""
		Get the 3D minimum distance between 2 lines
		input: two 3D lines p and q, defined by points p1, p2
		return: the two closest points on line p and q
		"""
		u = subtract(p2, p1)
		v = subtract(q2, q1)
		w = subtract(p1, q1)
		a = dot(u, u)         # always >= 0
		b = dot(u, v)
		c = dot(v, v)         # always >= 0
		d = dot(u, w)
		e = dot(v, w)
		D = a*c - b*b        # always >= 0
		sc = tc = 0.0

		# compute the line parameters of the two closest points
		if (D < 0.000001):			# the lines are almost parallel
			sc = 0.0
			if b > c:				# use the largest denominator
				tc = d / b
			else:
				tc = e / c
		else:
			sc = (b*e - c*d) / D
			tc = (a*e - b*d) / D

		return add(multiply(u, sc), p1), add(multiply(v, tc), q1)

	def mouseMove(self, iren, event=""):
		if len(self.lines) == 0:
			self.widget.rwi.ShowCursor()
			return
		x, y = iren.GetEventPosition()
		line1 = self.lines[0]
		q1, q2 = self.rayForMouse(x, y)
		a, b = self.closestPoints(line1.GetPoint1(), line1.GetPoint2(), q1, q2)
		if not hasattr(self, "sphereSource"):
			self.sphereSource = vtkSphereSource()
			self.sphereSource.SetRadius(20)
			sphereMapper = vtkDataSetMapper()
			sphereMapper.SetInputConnection(self.sphereSource.GetOutputPort())
			sphereActor = vtkActor()
			sphereActor.SetMapper(sphereMapper)
			sphereActor.GetProperty().SetColor(0.2, 1, 0.5)
			self.widget.renderer.AddViewProp(sphereActor)
			self.createLocator()
		self.sphereSource.SetCenter(a[0], a[1], a[2])
		self.assemblyFollower.SetPosition(a[0], a[1], a[2])
		self.widget.render()

	def keyPress(self, iren, event=""):
		key = iren.GetKeyCode()
		if key != "a":
			if key == " ":
				print "Hallelujah!"
			return
		x, y = iren.GetEventPosition()
		p1, p2 = self.rayForMouse(x, y)
		if len(self.lines) == 1:
			point = list(self.sphereSource.GetCenter())
			self.pickedLocation.emit(point)
			self.cleanUp()
			self.setWidget(self.widget)
			self.widget.render()
		else:
			self.addLine(p1, p2)

	def rayForMouse(self, selectionX, selectionY):
		"""
		Code taken from vtkPicker::Pick()
		"""
		renderer = self.widget.renderer
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


def dot(u, v):
	assert len(u) == len(v)
	result = 0
	for i in range(len(u)):
		result += u[i] * v[i]
	return result


def subtract(p1, p2):
	result = []
	for i in range(len(p1)):
		result.append(p1[i] - p2[i])
	return result


def multiply(p, s):
	result = []
	for i in range(len(p)):
		result.append(s * p[i])
	return result


def add(p1, p2):
	result = []
	for i in range(len(p1)):
		result.append(p1[i] + p2[i])
	return result


def mean(vectorList):
	result = []
	count = len(vectorList)
	vectorLength = len(vectorList[0])
	for i in range(vectorLength):
		result.append(0.0)

	for i in range(count):
		for j in range(vectorLength):
			result[j] += vectorList[i][j] / count

	return result
