"""
TransformationTool

TODO:
* Create unified AddViewProp method for easier cleanup of renderer
* Show spheres for landmarks in both single and multi render widget
* Spread this class over multiple files?

:Authors:
	Berend Klein Haneveld
"""
import math
from vtk import vtkBoxWidget
from vtk import vtkTransform
from vtk import vtkConeSource
from vtk import vtkSphereSource
from vtk import vtkPolyDataMapper
from vtk import vtkVolumePicker
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkPoints
from core.decorators import overrides


class TransformationTool(object):
	"""
	TransformationTool
	"""

	def __init__(self):
		super(TransformationTool, self).__init__()

		self.__callbacks = []

	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		raise NotImplementedError()

	def cleanUp(self):
		raise NotImplementedError()

	def AddObserver(self, obj, eventName, callbackFunction):
		callback = obj.AddObserver(eventName, callbackFunction)
		self.__callbacks.append((obj, callback))

	def cleanUpCallbacks(self):
		for obj, callback in self.__callbacks:
			obj.RemoveObserver(callback)
		self.__callbacks = []


class UserTransformationTool(TransformationTool):
	def __init__(self):
		super(UserTransformationTool, self).__init__()

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		self.renderWidget = multi
		self.setImageData(self.renderWidget.movingImageData)

	@overrides(TransformationTool)
	def cleanUp(self):
		# Hide the transformation box
		self.transformBox.EnabledOff()
		self.cleanUpCallbacks()

		# Reset the transformation
		transform = vtkTransform()
		transform.Identity()
		self.renderWidget.mapper.SetSecondInputUserTransform(transform)
		self.renderWidget.render()

	def setImageData(self, movingImageData):
		self.transformBox = vtkBoxWidget()
		self.transformBox.SetInteractor(self.renderWidget.rwi)
		self.transformBox.SetPlaceFactor(1.01)
		self.transformBox.SetInputData(movingImageData)
		self.transformBox.SetDefaultRenderer(self.renderWidget.renderer)
		self.transformBox.InsideOutOn()
		self.transformBox.PlaceWidget()

		self.AddObserver(self.transformBox, "InteractionEvent", self.transformCallback)
		self.transformBox.GetSelectedFaceProperty().SetOpacity(0.3)
		self.transformBox.EnabledOn()

	def transformCallback(self, arg1, arg2):
		transform = vtkTransform()
		arg1.GetTransform(transform)
		self.renderWidget.mapper.SetSecondInputUserTransform(transform)


class LandmarkTransformationTool(TransformationTool):
	def __init__(self):
		super(LandmarkTransformationTool, self).__init__()

		self.fixedPoints = vtkPoints()
		self.movingPoints = vtkPoints()

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		self.fixedWidget = fixed
		self.movingWidget = moving
		self.multiWidget = multi

		self.setupTool()

	def cleanUp(self):
		self.fixedWidget.renderer.RemoveViewProp(self.fixedProps[0])
		self.fixedWidget.renderer.RemoveViewProp(self.fixedProps[1])
		self.movingWidget.renderer.RemoveViewProp(self.movingProps[0])
		self.movingWidget.renderer.RemoveViewProp(self.movingProps[1])

		self.cleanUpCallbacks()

	def setupTool(self):
		multiplier = 5
		self.coneSource = vtkConeSource()
		self.coneSource.CappingOn()
		self.coneSource.SetHeight(12*multiplier)
		self.coneSource.SetRadius(5*multiplier)
		self.coneSource.SetResolution(31)
		self.coneSource.SetCenter(6*multiplier, 0, 0)
		self.coneSource.SetDirection(-1, 0, 0)

		self.coneMapper = vtkDataSetMapper()
		self.coneMapper.SetInputConnection(self.coneSource.GetOutputPort())

		self.fixedProps = self.addConesToWidget(self.fixedWidget)
		self.movingProps = self.addConesToWidget(self.movingWidget)

		# Note: do not add observers to the interactor but to an actor iot receive
		# messages about mouse released.
		self.AddObserver(self.fixedWidget.rwi, "MouseMoveEvent", self.MoveCursorFixed)
		self.AddObserver(self.fixedWidget.rwi, "KeyPressEvent", self.PressedVolumeFixed)
		self.AddObserver(self.movingWidget.rwi, "MouseMoveEvent", self.MoveCursorMoving)
		self.AddObserver(self.movingWidget.rwi, "KeyPressEvent", self.PressedVolumeMoving)

	def addConesToWidget(self, widget):
		redCone = vtkActor()
		redCone.PickableOff()
		redCone.SetMapper(self.coneMapper)
		redCone.GetProperty().SetColor(1, 0, 0)

		greenCone = vtkActor()
		greenCone.PickableOff()
		greenCone.SetMapper(self.coneMapper)
		greenCone.GetProperty().SetColor(0, 1, 0)

		# Add the two cones (or just one, if you want)
		widget.renderer.AddViewProp(redCone)
		widget.renderer.AddViewProp(greenCone)

		picker = vtkVolumePicker()
		picker.SetTolerance(1e-6)
		picker.SetVolumeOpacityIsovalue(0.1)
		# locator is optional, but improves performance for large polydata
		# picker.AddLocator(boneLocator)

		return [redCone, greenCone, picker]

	# A function to move the cursor with the mouse
	def MoveCursorFixed(self, iren, event=""):
		self.MoveCursor(self.fixedWidget, self.fixedProps, iren, event)

	def MoveCursorMoving(self, iren, event=""):
		self.MoveCursor(self.movingWidget, self.movingProps, iren, event)

	def MoveCursor(self, widget, props, iren, event=""):
		widget.rwi.HideCursor()
		redCone, greenCone, picker = props[0:3]
		p, n = PickPoint(iren, widget, picker)
		
		redCone.SetPosition(p[0], p[1], p[2])
		PointCone(redCone, n[0], n[1], n[2])
		greenCone.SetPosition(p[0], p[1], p[2])
		PointCone(greenCone, -n[0], -n[1], -n[2])

		iren.Render()

	def PressedVolumeFixed(self, iren, event=""):
		"""
		Add sphere in multi render.
		If there are both fixed and moving points, do
		the transform.
		"""
		sphere = CreateSphere()

		# Do not pick again, but instead use the position of
		# the cone so that you can rotate the volume and then
		# after rotating it and seeing that it is in the right
		# position can secure that location
		p = self.fixedProps[0].GetPosition()
		sphere.SetPosition(p[0], p[1], p[2])

		self.fixedWidget.renderer.AddViewProp(sphere)

	def PressedVolumeMoving(self, iren, event=""):
		p = self.movingProps[0].GetPosition()
		sphere = CreateSphere()
		sphere.SetPosition(p[0], p[1], p[2])
		self.movingWidget.renderer.AddViewProp(sphere)

	def ClickedVolume(self, iren, event=""):
		"""
		Left button release does not seem to get forwarded from interactor
		to listeners...
		"""
		pass


def CreateSphere():
	sphereSource = vtkSphereSource()
	sphereSource.SetRadius(20)
	sphereSource.SetThetaResolution(18)
	sphereSource.SetPhiResolution(18)

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

		
class DeformableTransformationTool(TransformationTool):
	def __init__(self):
		super(DeformableTransformationTool, self).__init__()
