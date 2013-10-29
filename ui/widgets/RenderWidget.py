"""
RenderWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkVolume
from vtk import vtkInteractorStyleTrackballCamera
from libvtkGPUMultiVolumeRenderPython import vtkOpenGLGPUVolumeRayCastMapper2 as vtkOpenGLGPUVolumeRayCastMapper
from vtk import vtkOrientationMarkerWidget
from vtk import vtkAxesActor
from vtk import vtkTransform
from vtk import vtkAssembly
from vtk import vtkLineSource
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkImagePlaneWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class RenderWidget(QWidget):
	"""
	RenderWidget for rendering volumes. It has a few render types which can be
	set and adjusted.
	"""

	dataChanged = Signal()
	updated = Signal()

	def __init__(self):
		super(RenderWidget, self).__init__()

		# Default volume renderer
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
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)
		self.rwi.GetRenderWindow().AddRenderer(self.rendererOverlay)
		self.rwi.GetRenderWindow().SetNumberOfLayers(2)

		self.imagePlaneWidgets = [vtkImagePlaneWidget() for i in range(3)]
		for index in range(3):
			self.imagePlaneWidgets[index].DisplayTextOn()
			self.imagePlaneWidgets[index].SetInteractor(self.rwi)

		self.mapper = vtkOpenGLGPUVolumeRayCastMapper()
		self.mapper.SetAutoAdjustSampleDistances(1)
		self.volume = None
		self.imageData = None
		self.VolumeVisualization = None
		self.shouldResetCamera = False

		axesActor = vtkAxesActor()
		self.orientationWidget = vtkOrientationMarkerWidget()
		self.orientationWidget.SetViewport(0.05, 0.05, 0.3, 0.3)
		self.orientationWidget.SetOrientationMarker(axesActor)
		self.orientationWidget.SetInteractor(self.rwi)
		self.orientationWidget.EnabledOn()
		self.orientationWidget.InteractiveOff()

		# Keep track of the base and user transforms
		self.baseTransform = vtkTransform()
		self.userTransform = vtkTransform()

		self.setMinimumWidth(400)
		self.setMinimumHeight(400)

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

	def render(self):
		if self.shouldResetCamera:
			self.renderer.ResetCamera()
			self.shouldResetCamera = False
		self.rwi.Render()
		self.rwi.GetRenderWindow().Render()

	@Slot(object)
	def setData(self, imageData):
		"""
		Updates the image data. If the image data is none, then
		the volume gets removed from the renderer. Otherwise, the
		new image data is given to the mapper.
		"""
		self.imageData = imageData
		if self.imageData is None:
			if self.volume is not None:
				self.renderer.RemoveViewProp(self.volume)
			print "Warning: image data is None"
			self.render()
			return

		# Set the image data for the mapper
		self.mapper.SetInputData(self.imageData)

		# Set the image data for the slices
		for index in range(3):
			self.imagePlaneWidgets[index].SetInputData(self.imageData)
			self.imagePlaneWidgets[index].SetPlaneOrientation(index)

		self._createGrid()
		self.shouldResetCamera = True
		# Don't call render, because camera should only be reset
		# when a volume property is loaded

	@Slot(object)
	def setVolumeVisualization(self, volumeVisualization):
		"""
		Updates the volume property. It actually removes the volume,
		creates a new volume and sets the updated volume property and
		then adds the new volume to the renderer.
		Just updating the vtkVolumeProperty gives artifacts and seems
		to not work correctly.
		:type volumeVisualization: volumeVisualization
		"""
		self.volumeVisualization = volumeVisualization

		if self.imageData is None or self.volumeVisualization is None:
			if self.volume is not None:
				self.renderer.RemoveViewProp(self.volume)
				self.volume = None
			return

		if self.volume is None:
			self.volume = vtkVolume()
			self.renderer.AddViewProp(self.volume)

		self.volumeVisualization.setMapper(self.mapper)
		self.mapper.SetShaderType(self.volumeVisualization.shaderType())
		self.volume.SetProperty(self.volumeVisualization.volProp)
		self.volume.SetMapper(self.mapper)

		self.render()

	@Slot(object)
	def setSlices(self, slices):
		for sliceIndex in range(len(slices)):
			if slices[sliceIndex]:
				self.imagePlaneWidgets[sliceIndex].On()
			else:
				self.imagePlaneWidgets[sliceIndex].Off()

	def _syncCameras(self, camera, ev):
		"""
		Camera modified event callback. Copies the parameters of
		the renderer camera into the camera of the overlay so they
		stay synced at all times.
		"""
		self.rendererOverlay.GetActiveCamera().ShallowCopy(camera)

	def _createGrid(self):
		bounds = self.imageData.GetBounds()
		self.grid = createGrid(bounds)
		self.renderer.AddViewProp(self.grid)

	@Slot(object)
	def transformationsUpdated(self, transformations):
		transform = transformations.completeTransform()
		self.volume.SetUserTransform(transform)


def createGrid(bounds):
	boundX = bounds[1]
	boundY = bounds[3]
	boundZ = bounds[5]

	# subdivisions = 10

	# stepSizeX = boundX / subdivisions
	# stepSizeY = boundY / subdivisions
	# stepSizeZ = boundZ / subdivisions

	# if stepSizeX > 1000:
	# 	stepSizeX = 1000
	# elif stepSizeX > 100:
	# 	stepSizeX = 100
	# elif stepSizeX > 10:
	# 	stepSizeX = 10

	lineActorX = createLine([0, 0, 0], [boundX, 0, 0])
	lineActorY = createLine([0, 0, 0], [0, boundY, 0])
	lineActorZ = createLine([0, 0, 0], [0, 0, boundZ])

	dataGrid = vtkAssembly()
	dataGrid.AddPart(lineActorX)
	dataGrid.AddPart(lineActorY)
	dataGrid.AddPart(lineActorZ)


def createLine(p1, p2):
	lineSource = vtkLineSource()
	lineSource.SetPoint1(p1[0], p1[1], p1[2])
	lineSource.SetPoint2(p2[0], p2[1], p2[2])

	lineMapper = vtkDataSetMapper()
	lineMapper.SetInputConnection(lineSource.GetOutputPort())

	lineActor = vtkActor()
	lineActor.SetMapper(lineMapper)
	return lineActor
