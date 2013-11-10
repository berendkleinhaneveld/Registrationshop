"""
RenderWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkVolume
from vtk import vtkInteractorStyleTrackballCamera
from libvtkGPUMultiVolumeRenderPython import vtkOpenGLGPUVolumeRayCastMapper2 as vtkOpenGLGPUVolumeRayCastMapper
from vtk import vtkTransform
from vtk import vtkPolyDataMapper
from vtk import vtkFollower
from vtk import vtkAssembly
from vtk import vtkLineSource
from vtk import vtkVectorText
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkImagePlaneWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# gridNudges describes the possible values for indicator intervals for the grid
gridNudges = [1, 5, 10, 50, 100, 500, 1000]


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
		self.gridItems = []
		self.orientationGridItems = []

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
		# Prevent warning messages on OSX by not asking to render
		# when the render window has never rendered before
		if self.rwi.GetRenderWindow().GetNeverRendered() == 0:
			self.rwi.GetRenderWindow().Render()

	@Slot(object)
	def setData(self, imageData):
		"""
		Updates the image data. If the image data is none, then
		the volume gets removed from the renderer. Otherwise, the
		new image data is given to the mapper.
		"""
		self.imageData = imageData
		# Clean up the data grid
		self._cleanUpGrids()

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
		self._createOrientationGrid()
		self.shouldResetCamera = True
		# Don't call render, because camera should only be reset
		# when a volume property is loaded

	def _cleanUpGrids(self):
		for item in self.gridItems:
			self.renderer.RemoveViewProp(item)
		for item in self.orientationGridItems:
			self.renderer.RemoveViewProp(item)
		self.gridItems = []
		self.orientationGridItems = []

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
		if self.volume.GetProperty() != self.volumeVisualization.volProp:
			self.volume.SetProperty(self.volumeVisualization.volProp)
		if self.volume.GetMapper() != self.mapper:
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
		"""
		Create a grid that shows the bounds of the dataset.
		These parts need to be updated when the user is transformed.
		"""
		bounds = self.imageData.GetBounds()
		self.gridItems = CreateGridItems(bounds)
		for item in self.gridItems:
			self.renderer.AddViewProp(item)

	def _createOrientationGrid(self):
		"""
		Create 3 axis that show the location / coords in 3D space.
		"""
		bounds = self.imageData.GetBounds()
		self.orientationGridItems = CreateOrientationGridItems(bounds, self.renderer.GetActiveCamera())
		for item in self.orientationGridItems:
			self.renderer.AddViewProp(item)

	@Slot(object)
	def transformationsUpdated(self, transformations):
		"""
		Get the scaling transform from the transformations and apply
		it to the volume and to the grid that shows the bounds of the
		volume.
		"""
		transform = transformations.scalingTransform()
		self.volume.SetUserTransform(transform)
		for item in self.gridItems:
			item.SetUserTransform(transform)


def CreateOrientationGridItems(bounds, camera):
	# TODO: instead of line, spheres or other shapes could be used as nudges
	boundX = bounds[1] * 1.2
	boundY = bounds[3] * 1.2
	boundZ = bounds[5] * 1.2

	lineActorsX = []
	lineActorsY = []
	lineActorsZ = []
	
	# Create the main axes
	lineActorsX.append(CreateLine([0, 0, 0], [boundX, 0, 0]))
	lineActorsY.append(CreateLine([0, 0, 0], [0, boundY, 0]))
	lineActorsZ.append(CreateLine([0, 0, 0], [0, 0, boundZ]))

	# Create the nudges on the X axis
	subdivSize = boundX / 10
	subdivSize = ClosestToMeasurement(subdivSize)
	handleSize = subdivSize / 5.0

	for index in range(1, int(boundX / subdivSize)):
		lineActorsX.append(CreateLine([index * subdivSize, 0, 0], [index * subdivSize, handleSize, 0]))
		lineActorsX.append(CreateLine([index * subdivSize, 0, 0], [index * subdivSize, 0, handleSize]))

	textItemX = CreateTextItem("X", [boundX, 0, 0], [1, 1, 1], 0.5 * subdivSize, camera)

	# Create the nudges on the Y axis
	subdivSize = boundY / 10
	subdivSize = ClosestToMeasurement(subdivSize)
	handleSize = subdivSize / 5.0

	for index in range(1, int(boundY / subdivSize)):
		lineActorsY.append(CreateLine([0, index * subdivSize, 0], [handleSize, index * subdivSize, 0]))
		lineActorsY.append(CreateLine([0, index * subdivSize, 0], [0, index * subdivSize, handleSize]))

	textItemY = CreateTextItem("Y", [0, boundY, 0], [1, 1, 1], 0.5 * subdivSize, camera)

	# Create the nudges on the Z axis
	subdivSize = boundZ / 10
	subdivSize = ClosestToMeasurement(subdivSize)
	handleSize = subdivSize / 5.0

	for index in range(1, int(boundZ / subdivSize)):
		lineActorsZ.append(CreateLine([0, 0, index * subdivSize], [handleSize, 0, index * subdivSize]))
		lineActorsZ.append(CreateLine([0, 0, index * subdivSize], [0, handleSize, index * subdivSize]))

	textItemZ = CreateTextItem("Z", [0, 0, boundZ], [1, 1, 1], 0.5 * subdivSize, camera)

	# Color the axis: R, G and B
	for lineActor in lineActorsX:
		lineActor.GetProperty().SetColor(1, 0, 0)
	for lineActor in lineActorsY:
		lineActor.GetProperty().SetColor(0, 1, 0)
	for lineActor in lineActorsZ:
		lineActor.GetProperty().SetColor(0, 0, 1)

	# Add the lines into one big assembly
	dataGrid = vtkAssembly()
	for lineActor in (lineActorsX + lineActorsY + lineActorsZ):
		dataGrid.AddPart(lineActor)

	return [dataGrid, textItemX, textItemY, textItemZ]


def CreateTextItem(text, position, color, scale, camera):
	textSource = vtkVectorText()
	textSource.SetText(text)

	textMapper = vtkPolyDataMapper()
	textMapper.SetInputConnection(textSource.GetOutputPort())

	textFollower = vtkFollower()
	textFollower.SetMapper(textMapper)
	textFollower.SetCamera(camera)
	textFollower.SetPosition(position)
	textFollower.GetProperty().SetColor(color[0], color[1], color[2])
	textFollower.SetScale(scale)

	return textFollower


def CreateGridItems(bounds):
	boundX = bounds[1]
	boundY = bounds[3]
	boundZ = bounds[5]

	lineActors = []
	lineActors.append(CreateLine([0, 0, 0], [boundX, 0, 0]))
	lineActors.append(CreateLine([0, 0, 0], [0, boundY, 0]))
	lineActors.append(CreateLine([0, 0, 0], [0, 0, boundZ]))

	lineActors.append(CreateLine([boundX, boundY, boundZ], [boundX, boundY, 0]))
	lineActors.append(CreateLine([boundX, boundY, boundZ], [0, boundY, boundZ]))
	lineActors.append(CreateLine([boundX, boundY, boundZ], [boundX, 0, boundZ]))

	lineActors.append(CreateLine([boundX, 0, 0], [boundX, 0, boundZ]))
	lineActors.append(CreateLine([boundX, 0, 0], [boundX, boundY, 0]))
	lineActors.append(CreateLine([0, boundY, 0], [0, boundY, boundZ]))
	lineActors.append(CreateLine([0, boundY, 0], [boundX, boundY, 0]))
	lineActors.append(CreateLine([0, 0, boundZ], [0, boundY, boundZ]))
	lineActors.append(CreateLine([0, 0, boundZ], [boundX, 0, boundZ]))

	# TODO: only show the corners instead of full box

	dataGrid = vtkAssembly()
	for lineActor in lineActors:
		dataGrid.AddPart(lineActor)

	return [dataGrid]


def ClosestToMeasurement(number):
	# Calculate diff
	diff = map(lambda x: abs(x - number), gridNudges)
	index = diff.index(min(diff))
	return gridNudges[index]


def CreateLine(p1, p2):
	lineSource = vtkLineSource()
	lineSource.SetPoint1(p1[0], p1[1], p1[2])
	lineSource.SetPoint2(p2[0], p2[1], p2[2])

	lineMapper = vtkDataSetMapper()
	lineMapper.SetInputConnection(lineSource.GetOutputPort())

	lineActor = vtkActor()
	lineActor.SetMapper(lineMapper)
	return lineActor
