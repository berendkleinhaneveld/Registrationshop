"""
SliceCompareViewerWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkInteractorStyleUser
from vtk import vtkImagePlaneWidget
from vtk import vtkLookupTable
from vtk import vtkCellPicker
from vtk import vtkImageAppendComponents
from vtk import vtkImageShiftScale
from vtk import vtkImageCast
from vtk import vtkImageMapToColors
from vtk import vtkDiscretizableColorTransferFunction
from vtk import vtkImageBlend
# from vtk import vtkLookupTable
from vtk import vtkColorTransferFunction
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkPiecewiseFunction
from vtk import vtkImageToImageStencil
from vtk import vtkImageExtractComponents
from vtk import vtkImageMathematics
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.Interactor import Interactor
from core.vtkDrawing import CreateCircle
from core.vtkDrawing import CreateSquare
from core.vtkDrawing import CreateLine
from core.vtkDrawing import ColorActor


class SliceCompareViewerWidget(QWidget, Interactor):
	"""
	SliceCompareViewerWidget shows slices that you can scroll through. Slicing happens
	in world coordinates. It can be synced to another slicer widget.
	"""

	slicePositionChanged = Signal(object)
	mouseMoved = Signal(object)

	def __init__(self):
		super(SliceCompareViewerWidget, self).__init__()

		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)
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

		# Known state of mouse (maybe can ask the event as well...)
		self.leftButtonPressed = False

		self.locator = []

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

	def setFixedImageData(self, fixed):
		self.fixedImagedata = fixed

	def setSlicerWidget(self, fixed, moving):
		self.fixedSlicerWidget = fixed
		self.movingSlicerWidget = moving
		self.slicer = None

	def mouseWheelChanged(self, arg1, arg2):
		pass

	def mouseMovedEvent(self, arg1, arg2):
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

	def transferfunction(self, imagedata, color):
		scalarRange = imagedata.GetScalarRange()

		opacity = vtkPiecewiseFunction()
		opacity.AddPoint(scalarRange[0], 0)
		opacity.AddPoint(scalarRange[1], 1)

		transfer = vtkDiscretizableColorTransferFunction()
		transfer.AddRGBPoint(scalarRange[0], 0, 0, 0)
		transfer.AddRGBPoint(scalarRange[1], color[0], color[1], color[2])
		transfer.SetScalarOpacityFunction(opacity)
		return transfer

	def adjustTransferFunction(self, transferfunction, lower, upper):
		transfer = vtkColorTransferFunction()
		val1 = [0.0 for _ in range(6)]
		val2 = [0.0 for _ in range(6)]
		transferfunction.GetNodeValue(0, val1)
		transferfunction.GetNodeValue(1, val2)
		val1[0] = lower
		val2[0] = upper
		transfer.AddRGBPoint(val1[0], val1[1], val1[2], val1[3], val1[4], val1[5])
		transfer.AddRGBPoint(val2[0], val2[1], val2[2], val2[3], val2[4], val2[5])
		transfer.Build()
		return transfer

	def updateCompareView(self):
		fixedSlice = self.fixedSlicerWidget.slicer.GetResliceOutput()
		movingSlice = self.movingSlicerWidget.slicer.GetResliceOutput()

		window = self.fixedSlicerWidget.slicer.GetWindow()
		level = self.fixedSlicerWidget.slicer.GetLevel()

		lower = level - window / 2.0
		upper = level + window / 2.0

		fixedTransfer = self.adjustTransferFunction(self.fixedSlicerWidget.transfer, lower, upper)
		movingTransfer = self.adjustTransferFunction(self.movingSlicerWidget.transfer, lower, upper)

		fixedMap = vtkImageMapToColors()
		fixedMap.SetInputData(fixedSlice)
		fixedMap.SetLookupTable(fixedTransfer)

		movingMap = vtkImageMapToColors()
		movingMap.SetInputData(movingSlice)
		movingMap.SetLookupTable(movingTransfer)

		maths = vtkImageMathematics()
		maths.SetInputConnection(0, fixedMap.GetOutputPort())
		maths.SetInputConnection(1, movingMap.GetOutputPort())
		maths.SetOperationToAdd()
		maths.Update()

		# self.blender = vtkImageBlend()
		# self.blender.SetOpacity(0, 0.5)
		# self.blender.SetOpacity(1, 0.5)
		# self.blender.AddInputConnection(fixedMap.GetOutputPort())
		# self.blender.AddInputConnection(movingMap.GetOutputPort())

		# redChannel = vtkImageExtractComponents()
		# greenChannel = vtkImageExtractComponents()
		# blueChannel = vtkImageExtractComponents()

		# redChannel.SetInputConnection(self.blender.GetOutputPort())
		# greenChannel.SetInputConnection(self.blender.GetOutputPort())
		# blueChannel.SetInputConnection(self.blender.GetOutputPort())

		# redChannel.SetComponents(0)
		# greenChannel.SetComponents(1)
		# blueChannel.SetComponents(2)

		# redScale = vtkImageShiftScale()
		# greenScale = vtkImageShiftScale()
		# blueScale = vtkImageShiftScale()

		# redScale.SetInputConnection(redChannel.GetOutputPort())
		# greenScale.SetInputConnection(greenChannel.GetOutputPort())
		# blueScale.SetInputConnection(blueChannel.GetOutputPort())

		# redScale.SetScale(2.0)
		# greenScale.SetScale(2.0)
		# blueScale.SetScale(2.0)

		# result = vtkImageAppendComponents()
		# result.AddInputConnection(redScale.GetOutputPort())
		# result.AddInputConnection(greenScale.GetOutputPort())
		# result.AddInputConnection(blueScale.GetOutputPort())

		# fixedMap.Update()

		# otherMath = vtkImageMathematics()
		# otherMath.SetOperationToMax()
		# otherMath.AddInputData(maths.GetOutput())
		# otherMath.SetConstantK(1.0)

		if not hasattr(self, "dataSetMapper"):
			self.dataSetMapper = vtkDataSetMapper()

		# Do not establish a vtk pipeline connection!
		# Otherwise the pipeline will be executed on every render call...
		self.dataSetMapper.SetInputData(maths.GetOutput())

		if not hasattr(self, "actor"):
			self.actor = vtkActor()
			self.actor.SetMapper(self.dataSetMapper)
			self.renderer.AddViewProp(self.actor)

			orig = self.fixedSlicerWidget.slicer.GetOrigin()
			self.actor.SetPosition(orig[0], orig[1], orig[2])

		if not self.locator:
			bounds = self.fixedImagedata.GetBounds()
			size = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
			meanSize = sum(size) / len(size)
			width = meanSize / 20.0
			color = [1.0, 1.0, 1.0]
			square = CreateSquare(width, color, 2)
			square.GetProperty().SetLineWidth(2)
			color = [0.2, 0.2, 0.2]
			line1 = CreateLine([0, width / 2.0, 0], [0, 10000, 0], color)
			line2 = CreateLine([0, -width / 2.0, 0], [0, -10000, 0], color)
			line3 = CreateLine([width / 2.0, 0, 0], [10000, 0, 0], color)
			line4 = CreateLine([-width / 2.0, 0, 0], [-10000, 0, 0], color)
			
			self.locator = [square, line1, line2, line3, line4]  # , otherSquare]
			for actor in self.locator:
				self.rendererOverlay.AddViewProp(actor)

	def render(self):
		self.renderer.Render()
		self.rwi.GetRenderWindow().Render()
