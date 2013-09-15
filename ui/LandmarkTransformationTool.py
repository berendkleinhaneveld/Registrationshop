"""
LandmarkTransformationTool (TransformationTool)

:Authors:
	Berend Klein Haneveld
"""
import math
from ui.TransformationTool import TransformationTool
from core.decorators import overrides
from PySide.QtGui import QWidget
from vtk import vtkConeSource
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkVolumePicker
from vtk import vtkSphereSource
from vtk import vtkPolyDataMapper
from vtk import vtkTransform
from vtk import vtkLandmarkTransform
from vtk import vtkPoints


class LandmarkTransformationTool(TransformationTool):
	"""
	Use the 'A' key to set a landmark.
	It will also undo the user transform if there was one

	The user can only set one landmark at a time.
	"""

	def __init__(self):
		super(LandmarkTransformationTool, self).__init__()

		self.fixedPoints = []
		self.movingPoints = []

	@overrides(TransformationTool)
	def getParameterWidget(self):
		widget = QWidget()
		return widget

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		self.fixedWidget = fixed
		self.movingWidget = moving
		self.multiWidget = multi

		# Reset any previous 'free' transforms
		self.multiWidget.resetAllTransforms()

		self.fixedProps = []
		self.movingProps = []
		self.multiProps = []

		self.setupTool()

	def cleanUp(self):
		self.cleanUpCallbacks()

		for prop in self.fixedProps:
			self.fixedWidget.renderer.RemoveViewProp(prop)
		for prop in self.movingProps:
			self.movingWidget.renderer.RemoveViewProp(prop)
		for prop in self.multiProps:
			self.multiWidget.renderer.RemoveViewProp(prop)

		self.fixedProps = []
		self.movingProps = []
		self.multiProps = []

	def applyTransform(self):
		self.multiWidget.applyUserTransform()

	def AddPropToWidget(self, prop, widget):
		if widget is self.fixedWidget:
			self.fixedProps.append(prop)
		elif widget is self.movingWidget:
			self.movingProps.append(prop)
		elif widget is self.multiWidget:
			self.multiProps.append(prop)
		widget.renderer.AddViewProp(prop)
		widget.render()

	def setupTool(self):
		multiplier = 5
		self.coneSource = vtkConeSource()
		self.coneSource.CappingOn()
		self.coneSource.SetHeight(12*multiplier)
		self.coneSource.SetRadius(5*multiplier)
		self.coneSource.SetResolution(6)
		self.coneSource.SetCenter(6*multiplier, 0, 0)
		self.coneSource.SetDirection(-1, 0, 0)

		self.coneMapper = vtkDataSetMapper()
		self.coneMapper.SetInputConnection(self.coneSource.GetOutputPort())

		self.fixedProps, self.fixedPicker = self.addConesToWidget(self.fixedWidget)
		self.movingProps, self.movingPicker = self.addConesToWidget(self.movingWidget)

		# Note: do not add observers to the interactor but to an actor iot receive
		# messages about mouse released.
		self.AddObserver(self.fixedWidget.rwi, "MouseMoveEvent", self.MoveCursorFixed)
		self.AddObserver(self.fixedWidget.rwi, "KeyPressEvent", self.PressedVolumeFixed)
		self.AddObserver(self.movingWidget.rwi, "MouseMoveEvent", self.MoveCursorMoving)
		self.AddObserver(self.movingWidget.rwi, "KeyPressEvent", self.PressedVolumeMoving)

	def addConesToWidget(self, widget):
		"""
		Returns array of props (2 cones) and the picker
		"""
		redCone = vtkActor()
		redCone.PickableOff()
		redCone.SetMapper(self.coneMapper)
		redCone.GetProperty().SetColor(1, 0, 0)

		greenCone = vtkActor()
		greenCone.PickableOff()
		greenCone.SetMapper(self.coneMapper)
		greenCone.GetProperty().SetColor(0, 1, 0)

		# Add the two cones (or just one, if you want)
		self.AddPropToWidget(redCone, widget)
		self.AddPropToWidget(greenCone, widget)

		picker = vtkVolumePicker()
		picker.SetTolerance(1e-6)
		picker.SetVolumeOpacityIsovalue(0.1)
		# locator is optional, but improves performance for large polydata
		# picker.AddLocator(boneLocator)

		return [redCone, greenCone], picker

	def MoveCursorFixed(self, iren, event=""):
		self.MoveCursor(self.fixedWidget, self.fixedProps, self.fixedPicker, iren, event)

	def MoveCursorMoving(self, iren, event=""):
		self.MoveCursor(self.movingWidget, self.movingProps, self.movingPicker, iren, event)

	def MoveCursor(self, widget, props, picker, iren, event=""):
		widget.rwi.HideCursor()
		redCone, greenCone = props[0:2]
		p, n = PickPoint(iren, widget, picker)
		
		redCone.SetPosition(p[0], p[1], p[2])
		PointCone(redCone, n[0], n[1], n[2])
		greenCone.SetPosition(p[0], p[1], p[2])
		PointCone(greenCone, -n[0], -n[1], -n[2])

		iren.Render()

	def AddFixedLandmark(self, position):
		self.fixedPoints.append(position)
		self.UpdateTransform()

		sphere = CreateSphere()
		sphere.SetPosition(position[0], position[1], position[2])

		self.lastFixedSphere = sphere
		self.AddPropToWidget(sphere, self.fixedWidget)
		self.AddPropToWidget(sphere, self.multiWidget)

	def ReplaceLastFixedLandmark(self, position):
		self.fixedPoints[-1] = position
		self.UpdateTransform()
		self.lastFixedSphere.SetPosition(position)

	def ReplaceLastMovingLandmark(self, position):
		self.movingPoints[-1] = position
		self.UpdateTransform()
		self.lastMovingSphere.SetPosition(position)
		self.lastMovingSphere2.SetPosition(position)

	def AddMovingLandmark(self, position):
		"""
		Adds the given position to the list of landmark points.
		Also creates spheres in the moving widget and the multi
		widget.
		"""
		self.movingPoints.append(position)
		self.UpdateTransform()

		sphere = CreateSphere()
		sphere.SetPosition(position[0], position[1], position[2])
		self.AddPropToWidget(sphere, self.movingWidget)
		self.lastMovingSphere = sphere
		sphere2 = CreateSphere()
		sphere2.SetPosition(position[0], position[1], position[2])
		sphere2.SetUserTransform(self.multiWidget.mapper.GetSecondInputUserTransform())
		self.lastMovingSphere2 = sphere2
		self.AddPropToWidget(sphere2, self.multiWidget)

	def UpdateTransform(self):
		"""
		Update the landmark transform
		"""
		if len(self.fixedPoints) == 0 or len(self.movingPoints) == 0:
			return

		fixedPoints = vtkPoints()
		movingPoints = vtkPoints()
		numberOfSets = min(len(self.fixedPoints), len(self.movingPoints))
		fixedPoints.SetNumberOfPoints(numberOfSets)
		movingPoints.SetNumberOfPoints(numberOfSets)

		for index in range(numberOfSets):
			fixedPoint = self.fixedPoints[index]
			movingPoint = self.movingPoints[index]
			fixedPoints.SetPoint(index, fixedPoint)
			movingPoints.SetPoint(index, movingPoint)

		landmarkTransform = vtkLandmarkTransform()
		landmarkTransform.SetModeToRigidBody()
		landmarkTransform.SetSourceLandmarks(fixedPoints)
		landmarkTransform.SetTargetLandmarks(movingPoints)
		landmarkTransform.Update()

		matrix = landmarkTransform.GetMatrix()

		transform = vtkTransform()
		transform.Identity()
		transform.SetMatrix(matrix)
		transform.Update()
		transform.Inverse()
		
		self.multiWidget.setUserTransform(transform)
		# TODO: the multi render widget only updates on mouse over...

	def PressedVolumeFixed(self, iren, event=""):
		"""
		Add sphere in multi render.
		If there are both fixed and moving points, do
		the transform.
		"""
		# Do not pick again, but instead use the position of
		# the cone so that you can rotate the volume and then
		# after rotating it and seeing that it is in the right
		# position can secure that location
		key = iren.GetKeyCode()
		if key != "a":
			return
		p = self.fixedProps[0].GetPosition()
		if len(self.fixedPoints) > len(self.movingPoints):
			self.ReplaceLastFixedLandmark(p)
		else:
			self.AddFixedLandmark(p)

	def PressedVolumeMoving(self, iren, event=""):
		key = iren.GetKeyCode()
		if key != "a":
			return
		p = self.movingProps[0].GetPosition()
		if len(self.fixedPoints) == len(self.movingPoints):
			self.ReplaceLastMovingLandmark(p)
		else:
			self.AddMovingLandmark(p)
		# TODO: also move the sphere in the multi widget


def CreateSphere():
	sphereSource = vtkSphereSource()
	sphereSource.SetRadius(20)
	sphereSource.SetThetaResolution(6)
	sphereSource.SetPhiResolution(6)

	sphereMapper = vtkPolyDataMapper()
	sphereMapper.SetInputConnection(sphereSource.GetOutputPort())

	sphere = vtkActor()
	sphere.PickableOff()
	sphere.SetMapper(sphereMapper)
	sphere.GetProperty().SetColor(1.0, 1.0, 0.6)

	return sphere


def PointCone(actor, nx, ny, nz):
	"""
	A function to point an actor along a vector.
	"""
	actor.SetOrientation(0.0, 0.0, 0.0)
	n = math.sqrt(nx**2 + ny**2 + nz**2)
	if (nx < 0.0):
		actor.RotateWXYZ(180, 0, 1, 0)
		n = -n
	actor.RotateWXYZ(180, (nx+n)*0.5, ny*0.5, nz*0.5)


def PickPoint(iren, widget, picker):
	"""
	Returns the picked position and normal.
	"""
	x, y = iren.GetEventPosition()
	picker.Pick(x, y, 0, widget.renderer)
	return picker.GetPickPosition(), picker.GetPickNormal()
