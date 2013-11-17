"""
SurfacePicker

:Authors:
	Berend Klein Haneveld
"""
import math
from Picker import Picker
from ui.Interactor import Interactor
from vtk import vtkVolumePicker
from vtk import vtkActor
from vtk import vtkConeSource
from vtk import vtkDataSetMapper
from PySide.QtCore import Signal


class SurfacePicker(Picker, Interactor):
	"""
	SurfacePicker is a dedicated picker for points in 3D datasets.
	"""

	pickedLocation = Signal(list)

	def __init__(self):
		super(SurfacePicker, self).__init__()
		self.props = []
		self.picker = vtkVolumePicker()
		self.picker.SetTolerance(1e-6)
		self.picker.SetVolumeOpacityIsovalue(0.1)
		self.widget = None

	def setWidget(self, widget):
		self.widget = widget

		# TODO: make size relative to image data size
		bounds = self.widget.imageData.GetBounds()
		mean = reduce(lambda x, y: x + y, bounds) / 3.0
		multiplier = mean / 100.0
		coneSource = vtkConeSource()
		coneSource.CappingOn()
		coneSource.SetHeight(12*multiplier)
		coneSource.SetRadius(5*multiplier)
		coneSource.SetResolution(6)
		coneSource.SetCenter(6*multiplier, 0, 0)
		coneSource.SetDirection(-1, 0, 0)

		coneMapper = vtkDataSetMapper()
		coneMapper.SetInputConnection(coneSource.GetOutputPort())

		self.redCone = vtkActor()
		self.redCone.PickableOff()
		self.redCone.SetMapper(coneMapper)
		self.redCone.GetProperty().SetColor(1, 0, 0)

		self.greenCone = vtkActor()
		self.greenCone.PickableOff()
		self.greenCone.SetMapper(coneMapper)
		self.greenCone.GetProperty().SetColor(0, 1, 0)

		self.widget.renderer.AddViewProp(self.redCone)
		self.widget.renderer.AddViewProp(self.greenCone)

		self.AddObserver(self.widget.rwi, "MouseMoveEvent", self.mouseMove)
		self.AddObserver(self.widget.rwi, "KeyPressEvent", self.keyPress)

	def cleanUp(self):
		if self.widget:
			self.widget.renderer.RemoveViewProp(self.greenCone)
			self.widget.renderer.RemoveViewProp(self.redCone)
			self.widget.rwi.ShowCursor()

		self.cleanUpCallbacks()

	# Callbacks

	def mouseMove(self, iren, event=""):
		self.widget.rwi.HideCursor()
		p, n = PickPoint(iren, self.widget.renderer, self.picker)
		
		self.redCone.SetPosition(p[0], p[1], p[2])
		self.greenCone.SetPosition(p[0], p[1], p[2])
		PointCone(self.redCone, n[0], n[1], n[2])
		PointCone(self.greenCone, -n[0], -n[1], -n[2])

		self.widget.render()

	def keyPress(self, iren, event=""):
		key = iren.GetKeyCode()
		if key != "a":
			return
		point, normal = PickPoint(iren, self.widget.renderer, self.picker)
		self.pickedLocation.emit(point)


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


def PickPoint(iren, renderer, picker):
	"""
	Returns the picked position and normal.
	"""
	x, y = iren.GetEventPosition()
	picker.Pick(x, y, 0, renderer)
	return picker.GetPickPosition(), picker.GetPickNormal()
