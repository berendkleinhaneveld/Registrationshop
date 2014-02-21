"""
MultiRenderWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkOpenGLGPUMultiVolumeRayCastMapper
from vtk import vtkRenderer
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkImagePlaneWidget
from vtk import vtkVolume
from vtk import vtkImageData
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from vtk import vtkVolumeProperty
from vtk import VTK_FLOAT
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from ui.transformations import TransformationList
from ui.transformations import ClippingBox
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.vtkDrawing import CreateBounds
from core.vtkDrawing import CreateOrientationGrid


class MultiRenderWidget(QWidget):
	"""
	MultiRenderWidget is a widget that can display two datasets: fixed and
	moving dataset.
	It uses the given volume property to derive how the volumes should be
	displayed. This widget also has its own controls that define how the
	volumes from the other widgets will be mixed into one visualization.

	The hard thing is to find out how to share volumes / volume properties /
	resources between widgets while still being linked together. So for
	instance when a volume is clipped in one of the single views it should
	be immediately visible in this widget. And the problem with the volume
	properties is that the volume property for this widget should be linked
	to the other widgets so that when they update their volume properties, this
	volume property will also be updated. But it can't be the same...

	There can be a few visualization modes:
	* 'simple' mix mode
	* colorized mix mode

	Simple mix mode is a mode that displays both datasets in the same way as
	they are visualized in the other views. Two controls are given to provide
	a way of setting the opacity of both volumes so that the user can mix the
	datasets to a nice visualization.

	Colorized mix mode makes grayscale visualizations of the
	"""

	dataChanged = Signal()
	updated = Signal()

	def __init__(self):
		super(MultiRenderWidget, self).__init__()

		# Default volume renderer
		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)
		self.renderer.SetInteractive(1)
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

		self._imagePlaneWidgets = [vtkImagePlaneWidget() for i in range(3)]
		for index in range(3):
			self._imagePlaneWidgets[index].DisplayTextOn()
			self._imagePlaneWidgets[index].SetInteractor(self.rwi)

		self.mapper = vtkOpenGLGPUMultiVolumeRayCastMapper()
		self.mapper.SetBlendModeToComposite()
		self.volume = vtkVolume()
		self.volume.SetMapper(self.mapper)
		self.renderer.AddViewProp(self.volume)

		self.fixedGridItems = []
		self.movingGridItems = []
		self.orientationGridItems = []

		# Create two empty datasets
		self.fixedImageData = CreateEmptyImageData()
		self.movingImageData = CreateEmptyImageData()

		self.fixedVolumeProperty = vtkVolumeProperty()
		self.movingVolumeProperty = vtkVolumeProperty()
		color, opacityFunction = CreateEmptyFunctions()
		self.fixedVolumeProperty.SetColor(color)
		self.fixedVolumeProperty.SetScalarOpacity(opacityFunction)
		self.movingVolumeProperty.SetColor(color)
		self.movingVolumeProperty.SetScalarOpacity(opacityFunction)
		self.visualization = None  # MultiVolumeVisualization

		self.clippingBox = ClippingBox()
		self.clippingBox.setWidget(self)

		self.mapper.SetInputData(0, self.fixedImageData)
		self.mapper.SetInputData(1, self.movingImageData)

		self._transformations = TransformationList()
		self._transformations.transformationChanged.connect(self.updateTransformation)
		self._shouldResetCamera = False

		self.setMinimumWidth(340)
		self.setMinimumHeight(340)

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

	def render(self):
		if self._shouldResetCamera:
			self.renderer.ResetCamera()
			self._shouldResetCamera = False
		self.rwi.Render()
		# Prevent warning messages on OSX by not asking to render
		# when the render window has never rendered before
		if not self.rwi.GetRenderWindow().GetNeverRendered():
			self.rwi.GetRenderWindow().Render()

	@Slot(object)
	def setFixedData(self, imageData):
		self._cleanUpGrids()

		self.fixedImageData = imageData
		if self.fixedImageData is None:
			self.fixedImageData = CreateEmptyImageData()
		if self.movingImageData is None:
			self.movingImageData = CreateEmptyImageData()

		self.mapper.SetInputData(0, self.fixedImageData)
		self.mapper.SetInputData(1, self.movingImageData)

		for index in range(3):
			self._imagePlaneWidgets[index].SetInputData(self.fixedImageData)
			self._imagePlaneWidgets[index].SetPlaneOrientation(index)

		self._updateGrids()
		self._createClippingBox()
		self._shouldResetCamera = True

	@Slot(object)
	def setMovingData(self, imageData):
		self._cleanUpGrids()

		self.movingImageData = imageData
		if self.movingImageData is None:
			self.movingImageData = CreateEmptyImageData()
		if self.fixedImageData is None:
			self.fixedImageData = CreateEmptyImageData()

		self.mapper.SetInputData(0, self.fixedImageData)
		self.mapper.SetInputData(1, self.movingImageData)

		self._updateGrids()
		self._shouldResetCamera = True

	def setVolumeVisualization(self, visualization):
		self.visualization = visualization
		if self.visualization is None:
			color, opacityFunction = CreateEmptyFunctions()
			self.fixedVolumeProperty = vtkVolumeProperty()
			self.fixedVolumeProperty.SetColor(color)
			self.fixedVolumeProperty.SetScalarOpacity(opacityFunction)
			self.movingVolumeProperty = vtkVolumeProperty()
			self.movingVolumeProperty.SetColor(color)
			self.movingVolumeProperty.SetScalarOpacity(opacityFunction)
		else:
			self.fixedVolumeProperty = self.visualization.fixedVolProp
			self.movingVolumeProperty = self.visualization.movingVolProp
			self.visualization.setMapper(self.mapper)
			if self.visualization.fixedVisualization:
				self._updateMapper(self.visualization.fixedVisualization, 1)
			if self.visualization.movingVisualization:
				self._updateMapper(self.visualization.movingVisualization, 2)

		self._updateVolumeProperties()

	def _updateGrids(self):
		if not self._hasImageData():
			return

		if self._hasMovingImageData():
			self.movingGridItems = CreateBounds(self.movingImageData.GetBounds())

		boundsFixed = self.fixedImageData.GetBounds()
		boundsMoving = self.movingImageData.GetBounds()
		maxBounds = map(lambda x, y: max(x, y), boundsFixed, boundsMoving)
		self.orientationGridItems = CreateOrientationGrid(maxBounds, self.renderer.GetActiveCamera())
		for item in (self.movingGridItems + self.fixedGridItems + self.orientationGridItems):
			self.renderer.AddViewProp(item)

	def _cleanUpGrids(self):
		for item in (self.fixedGridItems + self.movingGridItems + self.orientationGridItems):
			self.renderer.RemoveViewProp(item)
		self.fixedGridItems = []
		self.movingGridItems = []
		self.orientationGridItems = []

	def _createClippingBox(self):
		if not self._hasImageData():
			self.clippingBox.showClippingBox(False)
		else:
			if self._hasFixedImageData():
				self.clippingBox.setImageData(self.fixedImageData)
			elif self._hasMovingImageData():
				self.clippingBox.setImageData(self.movingImageData)
			else:
				self.clippingBox.enable(False)

	def _hasImageData(self):
		return self._hasFixedImageData() or self._hasMovingImageData()

	def _hasFixedImageData(self):
		return self._isActualImageData(self.fixedImageData)

	def _hasMovingImageData(self):
		return self._isActualImageData(self.movingImageData)

	def _isActualImageData(self, imageData):
		dimensions = imageData.GetDimensions()
		return dimensions != (3, 3, 3)

	# Properties

	@property
	def transformations(self):
		return self._transformations

	@transformations.setter
	def transformations(self, value):
		self._transformations.copyFromTransformations(value)

	# Slots

	@Slot(object)
	def setSlices(self, slices):
		for sliceIndex in range(len(slices)):
			if slices[sliceIndex]:
				self._imagePlaneWidgets[sliceIndex].On()
			else:
				self._imagePlaneWidgets[sliceIndex].Off()

	def showClippingBox(self, show):
		self.clippingBox.showClippingBox(show)
		self.render()

	def showClippingPlanes(self, show):
		self.clippingBox.showClippingPlanes(show)
		self.render()

	def resetClippingBox(self):
		self.clippingBox.resetClippingBox()
		self.render()

	@Slot()
	def updateTransformation(self):
		transform = self._transformations.completeTransform()
		self.mapper.SetSecondInputUserTransform(transform)
		for item in self.movingGridItems:
			item.SetUserTransform(transform)
		self.render()

	# Private methods

	def _updateMapper(self, volVis, volNr):
		shaderType = volVis.shaderType()
		if volNr == 1:
			self.mapper.SetShaderType1(shaderType)
			if shaderType == 2:  # MIDA
				lowerBound = (volVis.lowerBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				upperBound = (volVis.upperBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				self.mapper.SetLowerBound1(lowerBound)
				self.mapper.SetUpperBound1(upperBound)
				self.mapper.SetBrightness1(volVis.brightness / 100.0)
			if shaderType == 1:  # MIP
				lowerBound = (volVis.lowerBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				upperBound = (volVis.upperBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				self.mapper.SetLowerBound1(lowerBound)
				self.mapper.SetUpperBound1(upperBound)
		else:
			self.mapper.SetShaderType2(shaderType)
			if shaderType == 2:  # MIDA
				lowerBound = (volVis.lowerBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				upperBound = (volVis.upperBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				self.mapper.SetLowerBound2(lowerBound)
				self.mapper.SetUpperBound2(upperBound)
				self.mapper.SetBrightness2(volVis.brightness / 100.0)
			if shaderType == 1:  # MIP
				lowerBound = (volVis.lowerBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				upperBound = (volVis.upperBound - volVis.minimum) / (volVis.maximum - volVis.minimum)
				self.mapper.SetLowerBound2(lowerBound)
				self.mapper.SetUpperBound2(upperBound)

	def _updateVolumeProperties(self):
		"""
		Private method to update the volume properties.
		"""
		if self.volume.GetProperty() != self.fixedVolumeProperty:
			self.volume.SetProperty(self.fixedVolumeProperty)
		if self.mapper.GetProperty2() != self.movingVolumeProperty:
			self.mapper.SetProperty2(self.movingVolumeProperty)
		self.render()

	def _syncCameras(self, camera, ev):
		"""
		Camera modified event callback. Copies the parameters of
		the renderer camera into the camera of the overlay so they
		stay synced at all times.
		"""
		self.rendererOverlay.GetActiveCamera().ShallowCopy(camera)


# Helper methods
def CreateEmptyImageData():
	"""
	Create an empty image data object. The multi volume mapper expects two
	inputs, so if there is only one dataset loaded, a dummy dataset can be
	created using this method. Be sure to also set a dummy volume property
	(CreateVolumeVisualizationInvisible) so that the volume does not show up in
	the renderer.

	:rtype: vtkImageData
	"""
	dimensions = [3, 3, 3]
	imageData = vtkImageData()
	imageData.Initialize()
	imageData.SetDimensions(dimensions)
	imageData.SetSpacing(1, 1, 1)
	imageData.SetOrigin(10, 10, 0)
	imageData.AllocateScalars(VTK_FLOAT, 1)
	for z in xrange(0, dimensions[2]-1):
		for y in xrange(0, dimensions[1]-1):
			for x in xrange(0, dimensions[0]-1):
				imageData.SetScalarComponentFromDouble(x, y, z, 0, 0.0)
	return imageData


def CreateEmptyFunctions():
	"""
	:rtype: vtkColorTransferFunction, vtkPiecewiseFunction
	"""
	# Transfer functions and properties
	colorFunction = vtkColorTransferFunction()
	colorFunction.AddRGBPoint(-1000, 0.0, 0.0, 0.0)
	colorFunction.AddRGBPoint(1000, 0.0, 0.0, 0.0)

	opacityFunction = vtkPiecewiseFunction()
	opacityFunction.AddPoint(-1000, 0.0)
	opacityFunction.AddPoint(1000, 0.0)

	return colorFunction, opacityFunction
