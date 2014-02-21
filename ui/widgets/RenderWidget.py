"""
RenderWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkVolume
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkOpenGLGPUVolumeRayCastMapper
from vtk import vtkTransform
from vtk import vtkImagePlaneWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.transformations import ClippingBox
from core.vtkDrawing import CreateBounds
from core.vtkDrawing import CreateOrientationGrid


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
		self.rwi.SetDesiredUpdateRate(0)

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

		self.clippingBox = ClippingBox()
		self.clippingBox.setWidget(self)

		# Keep track of the base and user transforms
		self.baseTransform = vtkTransform()
		self.userTransform = vtkTransform()

		self.setMinimumWidth(340)
		self.setMinimumHeight(340)

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

	def render(self):
		self.clippingBox.update()
		if self.shouldResetCamera:
			self.renderer.ResetCamera()
			self.shouldResetCamera = False
		self.rwi.Render()
		# Prevent warning messages on OSX by not asking to render
		# when the render window has never rendered before
		if not self.rwi.GetRenderWindow().GetNeverRendered():
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
		self._createClippingBox()
		self.shouldResetCamera = True
		# Don't call render, because camera should only be reset
		# when a volume property is loaded

	def showClippingBox(self, show):
		self.clippingBox.showClippingBox(show)
		self.render()

	def showClippingPlanes(self, show):
		self.clippingBox.showClippingPlanes(show)
		self.render()

	def resetClippingBox(self):
		self.clippingBox.resetClippingBox()
		self.render()

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

	@Slot(object)
	def transformationsUpdated(self, transformations):
		"""
		Get the scaling transform from the transformations and apply
		it to the volume and to the grid that shows the bounds of the
		volume.

		At the moment it is deprecated. It makes more trouble than that
		it solves any real (user) problem...
		"""
		# transform = transformations.scalingTransform()
		# if self.volume:
		# 	self.volume.SetUserTransform(transform)
		# for item in self.gridItems:
		# 	item.SetUserTransform(transform)
		# self.clippingBox.setTransform(transform)
		pass

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
		self.gridItems = CreateBounds(bounds)
		for item in self.gridItems:
			self.renderer.AddViewProp(item)

	def _createOrientationGrid(self):
		"""
		Create 3 axis that show the location / coords in 3D space.
		"""
		bounds = self.imageData.GetBounds()
		self.orientationGridItems = CreateOrientationGrid(bounds, self.renderer.GetActiveCamera())
		for item in self.orientationGridItems:
			self.renderer.AddViewProp(item)

	def _createClippingBox(self):
		"""
		Create a clipping box that fits around the data.
		"""
		self.clippingBox = ClippingBox()
		self.clippingBox.setWidget(self)
		if not self.imageData:
			self.clippingBox.enable(False)
		else:
			self.clippingBox.setImageData(self.imageData)

	def _cleanUpGrids(self):
		for item in self.gridItems:
			self.renderer.RemoveViewProp(item)
		for item in self.orientationGridItems:
			self.renderer.RemoveViewProp(item)
		self.gridItems = []
		self.orientationGridItems = []
