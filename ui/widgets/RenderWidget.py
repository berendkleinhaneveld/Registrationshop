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
from vtk import vtkImagePlaneWidget
from vtk import vtkMatrix4x4
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

		self.volume = None
		self.mapper = vtkOpenGLGPUVolumeRayCastMapper()
		self.mapper.SetAutoAdjustSampleDistances(1)
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

	def getUserTransform(self):
		return self.userTransform

	def getFullTransform(self):
		return self._getConcatenatedTransform()

	def setUserTransform(self, transform):
		self.userTransform = transform
		self._updateTransform()

	def resetUserTransform(self):
		self.userTransform = vtkTransform()
		self._updateTransform()

	def resetAllTransforms(self):
		self.baseTransform = vtkTransform()
		self.userTransform = vtkTransform()
		self._updateTransform()

	def applyUserTransform(self):
		"""
		Concatenates the user transform with the base transform
		into the new base transform. Resets the user transform.
		"""
		self.baseTransform = self._getConcatenatedTransform()
		self.resetUserTransform()

	def _updateTransform(self):
		"""
		Updates the transform of the second volume.
		"""
		transform = self._getConcatenatedTransform()
		transform.Update()
		self.volume.SetUserTransform(transform)

	def _getConcatenatedTransform(self):
		"""
		Creates and returns a new vtkTransform that exists
		of the base and user transforms concatenated.
		"""
		completeTransform = vtkTransform()
		completeTransform.Concatenate(self.userTransform)
		completeTransform.Concatenate(self.baseTransform)
		completeTransform.Update()

		return self._getCopyOfTransform(completeTransform)

	def _getCopyOfTransform(self, transform):
		newTransform = vtkTransform()
		matrix = vtkMatrix4x4()
		matrix.DeepCopy(transform.GetMatrix())
		newTransform.SetMatrix(matrix)
		return newTransform
