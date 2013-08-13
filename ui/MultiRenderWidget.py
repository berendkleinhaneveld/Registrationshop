"""
MultiRenderWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from libvtkGPUMultiVolumeRenderPython import vtkOpenGLGPUMultiVolumeRayCastMapper
from vtk import vtkRenderer
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkImagePlaneWidget
from vtk import vtkVersion
from vtk import vtkVolume
from vtk import vtkBoxWidget
from vtk import vtkImageData
from vtk import vtkTransform
from vtk import vtkColorTransferFunction
from vtk import vtkVolumeProperty
from vtk import vtkPiecewiseFunction
from vtk import vtkAxesActor
from vtk import vtkOrientationMarkerWidget
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

VTK_MAJOR_VERSION = vtkVersion.GetVTKMajorVersion()

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

		# These variables will later on be used for creating a comparative
		# visualization that does not use the volume properties of the 
		# render widgets
		self.fixedVolumeProperty = None
		self.movingVolumeProperty = None

		self.shouldResetCamera = False

		self.mapper.SetInput(0, self.fixedImageData)
		self.mapper.SetInput(1, self.movingImageData)

		self.tranformBox = vtkBoxWidget()
		self.tranformBox.SetInteractor(self.rwi)
		self.tranformBox.SetDefaultRenderer(self.renderer)
		
		self.tranformBox.mapper = self.mapper
		self.tranformBox.AddObserver("InteractionEvent", TransformCallback)
		self.tranformBox.GetSelectedFaceProperty().SetOpacity(0.3)

		axesActor = vtkAxesActor();
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

	@Slot(object)
	def setFixedData(self, imageData):
		self.fixedImageData = imageData
		if self.fixedImageData is None:
			self.fixedImageData = CreateEmptyImageData()

		self.mapper.SetInput(0, self.fixedImageData)
		self.mapper.SetInput(1, self.movingImageData)

		for index in range(3):
			if VTK_MAJOR_VERSION <= 5:
				self.imagePlaneWidgets[index].SetInput(self.fixedImageData)
			else:
				self.imagePlaneWidgets[index].SetInputData(self.fixedImageData)
			self.imagePlaneWidgets[index].SetPlaneOrientation(index)

		self.shouldResetCamera = True

	def setMovingData(self, imageData):
		self.movingImageData = imageData
		if self.movingImageData is None:
			self.movingImageData = CreateEmptyImageData()

		self.tranformBox.SetInput(self.movingImageData)
		self.tranformBox.PlaceWidget()
		self.tranformBox.SetPlaceFactor(1.0)
		self.tranformBox.EnabledOff()

		self.mapper.SetInput(0, self.fixedImageData)
		self.mapper.SetInput(1, self.movingImageData)

		self.shouldResetCamera = True
			
	@Slot(object)
	def setFixedVolumeProperty(self, volumeProperty):
		self.fixedVolumeProperty = volumeProperty
		self.updateVolumeProperties()

	@Slot(object)
	def setMovingVolumeProperty(self, volumeProperty):
		self.movingVolumeProperty = volumeProperty
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


	def showTransformBox(self, value):
		if value:
			self.tranformBox.EnabledOn()
		else:
			self.tranformBox.EnabledOff()

	def opacityChangedForFixedVolume(self, value):
		self.fixedOpacity = value
		self.updateVolumeProperties()

	def opacityChangedForMovingVolume(self, value):
		self.movingOpacity = value
		self.updateVolumeProperties()

def TransformCallback(arg1, arg2):
	"""
	:type arg1: vtkBoxWidget
	:type arg2: InteractionEvent
	"""
	if hasattr(arg1, "mapper"):
		transform = vtkTransform()
		arg1.GetTransform(transform)
		arg1.mapper.SetSecondInputUserTransform(transform)

# Helper methods
def CreateEmptyImageData():
	"""
	Create an empty image data object. The multi volume mapper expects two
	inputs, so if there is only one dataset loaded, a dummy dataset can be 
	created using this method. Be sure to also set a dummy volume property
	(CreateVolumePropertyInvisible) so that the volume does not show up in 
	the renderer.

	:rtype: vtkImageData
	"""
	dimensions = [3, 3, 3]
	imageData = vtkImageData()
	imageData.SetDimensions(dimensions)
	imageData.SetSpacing(1, 1, 1);
	imageData.SetOrigin(0, 0, 0);
	imageData.SetNumberOfScalarComponents(1)
	imageData.SetScalarTypeToFloat()
	imageData.AllocateScalars()
	for z in xrange(0, dimensions[2]-1):
		for y in xrange(0, dimensions[1]-1):
			for x in xrange(0, dimensions[0]-1):
				imageData.SetScalarComponentFromDouble(x, y, z, 0, 0.0)
	imageData.Update()
	return imageData

