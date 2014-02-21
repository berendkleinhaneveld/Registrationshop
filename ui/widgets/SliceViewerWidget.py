"""
SliceViewerWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkInteractorStyleUser
from vtk import vtkImagePlaneWidget
from vtk import vtkCellPicker
from vtk import vtkColorTransferFunction
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.Interactor import Interactor
from core.vtkDrawing import CreateSquare
from core.vtkDrawing import CreateLine


class SliceViewerWidget(QWidget, Interactor):
	"""
	SliceViewerWidget shows slices that you can scroll through. Slicing happens
	in world coordinates. It can be synced to another slicer widget.
	"""

	slicePositionChanged = Signal(object)
	mouseMoved = Signal(object)

	def __init__(self):
		super(SliceViewerWidget, self).__init__()

		self.color = [1, 1, 1]

		self.renderer = vtkRenderer()
		self.renderer.SetBackground(0.0, 0.0, 0.0)
		self.renderer.SetLayer(0)

		# Overlay renderer which is synced with the default renderer
		self.rendererOverlay = vtkRenderer()
		self.rendererOverlay.SetLayer(1)
		self.rendererOverlay.SetInteractive(0)
		self.renderer.GetActiveCamera().AddObserver("ModifiedEvent", self._syncCameras)

		self.rwi = QVTKRenderWindowInteractor(parent=self)
		self.rwi.SetInteractorStyle(vtkInteractorStyleUser())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)
		self.rwi.GetRenderWindow().AddRenderer(self.rendererOverlay)
		self.rwi.GetRenderWindow().SetNumberOfLayers(2)

		# Set camera to parallel
		camera = self.renderer.GetActiveCamera()
		camera.SetParallelProjection(1)

		# Add new observers for mouse wheel
		self.AddObserver(self.rwi, "CharEvent", self.charTyped)
		self.AddObserver(self.rwi, "MouseWheelBackwardEvent", self.mouseWheelChanged)
		self.AddObserver(self.rwi, "MouseWheelForwardEvent", self.mouseWheelChanged)
		self.AddObserver(self.rwi, "MouseMoveEvent", self.mouseMovedEvent, 1)

		self.picker = vtkCellPicker()
		self.picker.SetTolerance(1e-6)

		self.locator = []

		self.setStyleSheet("background-color: #333")

		layout = QGridLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi)
		self.setLayout(layout)

	def _syncCameras(self, camera, ev):
		"""
		Camera modified event callback. Copies the parameters of
		the renderer camera into the camera of the overlay so they
		stay synced at all times.
		"""
		self.rendererOverlay.GetActiveCamera().ShallowCopy(camera)

	def charTyped(self, arg1, arg2):
		# print arg1.GetKeyCode()
		pass

	def setLocatorPosition(self, position):
		for actor in self.locator:
			actor.SetPosition(position[0], position[1], position[2])

	def setImageData(self, imageData):
		self.imagedata = imageData

		scalarRange = self.imagedata.GetScalarRange()

		self.transfer = vtkColorTransferFunction()
		self.transfer.SetRange(scalarRange[0], scalarRange[1])
		self.transfer.AddRGBPoint(scalarRange[0], 0, 0, 0)
		self.transfer.AddRGBPoint(scalarRange[1], self.color[0], self.color[1], self.color[2])
		self.transfer.Build()

		# Add a slicer widget that looks at camera
		self.slicer = vtkImagePlaneWidget()
		self.slicer.DisplayTextOn()
		self.slicer.SetInteractor(self.rwi)
		self.slicer.SetInputData(imageData)
		self.slicer.SetPlaneOrientation(2)
		self.slicer.SetRestrictPlaneToVolume(1)
		self.slicer.PlaceWidget()
		self.slicer.On()
		cursorProperty = self.slicer.GetCursorProperty()
		cursorProperty.SetOpacity(0.0)
		planeProperty = self.slicer.GetPlaneProperty()
		planeProperty.SetColor(0, 0, 0)
		selectedPlaneProperty = self.slicer.GetSelectedPlaneProperty()
		selectedPlaneProperty.SetColor(0, 0, 0)

		# Reset the camera and set the clipping range
		self.renderer.ResetCamera()
		camera = self.renderer.GetActiveCamera()
		camera.SetClippingRange(0.1, 10000)

		if not self.locator:
			bounds = self.imagedata.GetBounds()
			size = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
			meanSize = sum(size) / len(size)
			width = meanSize / 20.0
			square = CreateSquare(width, self.color)
			square.GetProperty().SetLineWidth(2)

			line1 = CreateLine([0, width / 2.0, 0], [0, 10000, 0], self.color)
			line2 = CreateLine([0, -width / 2.0, 0], [0, -10000, 0], self.color)
			line3 = CreateLine([width / 2.0, 0, 0], [10000, 0, 0], self.color)
			line4 = CreateLine([-width / 2.0, 0, 0], [-10000, 0, 0], self.color)
			
			self.locator = [square, line1, line2, line3, line4]
			for actor in self.locator:
				self.rendererOverlay.AddViewProp(actor)

	def mouseWheelChanged(self, arg1, arg2):
		sign = 1 if arg2 == "MouseWheelForwardEvent" else -1
		index = self.slicer.GetSliceIndex()
		nextIndex = index + sign
		self.slicer.SetSliceIndex(nextIndex)

		self.slicePositionChanged.emit(self)

	def mouseMovedEvent(self, arg1, arg2):
		self.rwi.HideCursor()

		x, y = arg1.GetEventPosition()

		camera = self.renderer.GetActiveCamera()
		cameraFP = list(camera.GetFocalPoint()) + [1.0]
		self.renderer.SetWorldPoint(cameraFP[0], cameraFP[1], cameraFP[2], cameraFP[3])
		self.renderer.WorldToDisplay()

		# Convert the selection point into world coordinates.
		self.renderer.SetDisplayPoint(x, y, 1)
		self.renderer.DisplayToWorld()
		worldCoords = self.renderer.GetWorldPoint()
		pickPosition = map(lambda x: x / worldCoords[3], worldCoords[0:-1])
		self.mouseMoved.emit(pickPosition)

	def render(self):
		self.slicer.UpdatePlacement()
		self.renderer.Render()
		self.rwi.GetRenderWindow().Render()
