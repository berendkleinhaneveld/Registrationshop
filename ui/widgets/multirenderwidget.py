"""
MultiRenderWidget

:Authors:
	Berend Klein Haneveld
"""

from libvtkGPUMultiVolumeRenderPython import vtkOpenGLGPUMultiVolumeRayCastMapper
from vtk import vtkRenderer
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkImagePlaneWidget
from vtk import vtkVolume
from vtk import vtkImageData
from vtk import vtkAxesActor
from vtk import vtkOrientationMarkerWidget
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from vtk import vtkTransform
from vtk import vtkVolumeProperty
from vtk import vtkMatrix4x4
from vtk import VTK_FLOAT
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


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

		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)

		self.rwi = QVTKRenderWindowInteractor(parent=self)
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)

		self.imagePlaneWidgets = [vtkImagePlaneWidget() for i in range(3)]
		for index in range(3):
			self.imagePlaneWidgets[index].DisplayTextOn()
			self.imagePlaneWidgets[index].SetInteractor(self.rwi)

		self.mapper = vtkOpenGLGPUMultiVolumeRayCastMapper()
		self.mapper.SetBlendModeToComposite()
		self.volume = vtkVolume()
		self.volume.SetMapper(self.mapper)
		self.renderer.AddViewProp(self.volume)

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

		self.shouldResetCamera = False

		self.mapper.SetInputData(0, self.fixedImageData)
		self.mapper.SetInputData(1, self.movingImageData)

		# Keep track of the base and user transforms
		self.baseTransform = vtkTransform()
		self.userTransform = vtkTransform()
		# TODO: save the base transform in the project file

		axesActor = vtkAxesActor()
		self.orientationWidget = vtkOrientationMarkerWidget()
		self.orientationWidget.SetViewport(0.05, 0.05, 0.3, 0.3)
		self.orientationWidget.SetOrientationMarker(axesActor)
		self.orientationWidget.SetInteractor(self.rwi)
		self.orientationWidget.EnabledOn()
		self.orientationWidget.InteractiveOff()

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
	def setFixedData(self, imageData):
		self.fixedImageData = imageData
		if self.fixedImageData is None:
			self.fixedImageData = CreateEmptyImageData()
		if self.movingImageData is None:
			self.movingImageData = CreateEmptyImageData()

		self.mapper.SetInputData(0, self.fixedImageData)
		self.mapper.SetInputData(1, self.movingImageData)

		for index in range(3):
			self.imagePlaneWidgets[index].SetInputData(self.fixedImageData)
			self.imagePlaneWidgets[index].SetPlaneOrientation(index)

		self.shouldResetCamera = True

	def setMovingData(self, imageData):
		self.movingImageData = imageData
		if self.movingImageData is None:
			self.movingImageData = CreateEmptyImageData()
		if self.fixedImageData is None:
			self.fixedImageData = CreateEmptyImageData()

		self.mapper.SetInputData(0, self.fixedImageData)
		self.mapper.SetInputData(1, self.movingImageData)

		self.shouldResetCamera = True

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
			self.visualization.configureMapper(self.mapper)
		self.updateVolumeProperties()

	def updateVolumeProperties(self):
		"""
		Private method to update the volume properties.
		"""
		self.volume.SetProperty(self.fixedVolumeProperty)
		self.mapper.SetProperty2(self.movingVolumeProperty)
		self.render()

	@Slot(object)
	def setSlices(self, slices):
		for sliceIndex in range(len(slices)):
			if slices[sliceIndex]:
				self.imagePlaneWidgets[sliceIndex].On()
			else:
				self.imagePlaneWidgets[sliceIndex].Off()

	def getUserTransform(self):
		return self.userTransform

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
		self.mapper.SetSecondInputUserTransform(transform)

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
	colorFunction.AddRGBPoint(0, 0.0, 0.0, 0.0)
	colorFunction.AddRGBPoint(1, 0.0, 0.0, 0.0)

	opacityFunction = vtkPiecewiseFunction()
	opacityFunction.AddPoint(0, 0)
	opacityFunction.AddPoint(1, 0)

	return colorFunction, opacityFunction
