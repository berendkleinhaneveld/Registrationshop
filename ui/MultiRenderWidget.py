"""
MultiRenderWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtCore import Signal
from libvtkGPUMultiVolumeRenderPython import vtkOpenGLGPUMultiVolumeRayCastMapper
from vtk import vtkRenderer
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkImagePlaneWidget
from vtk import vtkVersion
from vtk import vtkVolume
from vtk import vtkImageData
from vtk import vtkColorTransferFunction
from vtk import vtkVolumeProperty
from vtk import vtkPiecewiseFunction
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

	loadedData = Signal()

	def __init__(self, fixedRenderWidget, movingRenderWidget):
		super(MultiRenderWidget, self).__init__()

		self.fixedRenderWidget = fixedRenderWidget
		self.movingRenderWidget = movingRenderWidget

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

		# Create two empty datasets
		self.fixedImageData = CreateEmptyImageData()
		self.movingImageData = CreateEmptyImageData()

		# These variables will later on be used for creating a comparative
		# visualization that does not use the volume properties of the 
		# render widgets
		self.fixedVolProp = None
		self.movingVolProp = None

		# self.datasetMix = 0.5 # Value between 0 and 1.0
		self.fixedOpacity = 1.0
		self.movingOpacity = 1.0

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

		self.fixedRenderWidget.updated.connect(self.Update)
		self.movingRenderWidget.updated.connect(self.Update)
		self.fixedRenderWidget.loadedData.connect(self.fixedRenderWidgetLoadedData)
		self.movingRenderWidget.loadedData.connect(self.movingRenderWidgetLoadedData)

	def Update(self):
		# Get the volume properties from the render widgets and apply them in this renderer
		# Steps:
		# 1. Get/copy the volume properties from the render widgets
		# 2. Adjust the volume properties with help of the slider values
		# 3. Set the newly created volume properties of the mapper/volume
		if self.fixedRenderWidget.renderVolumeProperty is not None:
			fixedVolProp = vtkVolumeProperty()
			fixedVolProp.DeepCopy(self.fixedRenderWidget.renderVolumeProperty.volumeProperty)
			opacityFunction = self.createFunctionFromOpacityAndVolumeProperty(self.fixedOpacity, fixedVolProp)
			fixedVolProp.SetScalarOpacity(opacityFunction)
			self.volume.SetProperty(fixedVolProp)
		else:
			volProp = vtkVolumeProperty()
			color, opacityFunction = CreateEmptyFunctions()
			volProp.SetColor(color)
			volProp.SetScalarOpacity(opacityFunction)
			self.volume.SetProperty(volProp)

		if self.movingRenderWidget.renderVolumeProperty is not None:
			movingVolProp = vtkVolumeProperty()
			movingVolProp.DeepCopy(self.movingRenderWidget.renderVolumeProperty.volumeProperty)
			opacityFunction = self.createFunctionFromOpacityAndVolumeProperty(self.movingOpacity, movingVolProp)
			movingVolProp.SetScalarOpacity(opacityFunction)
			self.mapper.SetProperty2(movingVolProp)
		else:
			volProp = vtkVolumeProperty()
			color, opacityFunction = CreateEmptyFunctions()
			volProp.SetColor(color)
			volProp.SetScalarOpacity(opacityFunction)
			self.mapper.SetProperty2(volProp)
		# TODO: update all the other UI elements such as boxes, interaction widgets, etc.
		self.rwi.Render()

	def fixedRenderWidgetLoadedData(self):
		self.renderer.RemoveViewProp(self.volume)
		self.setFixedData(self.fixedRenderWidget.imageData, self.fixedRenderWidget.renderVolumeProperty)
		self.renderer.AddViewProp(self.volume)
		self.renderer.ResetCamera()

	def movingRenderWidgetLoadedData(self):
		self.renderer.RemoveViewProp(self.volume)
		self.setMovingData(self.movingRenderWidget.imageData, self.movingRenderWidget.renderVolumeProperty)
		self.renderer.AddViewProp(self.volume)
		self.renderer.ResetCamera()

	def setFixedData(self, imageData, volProp):
		"""
		:type imageData: vtkImageData
		:type volProp: VolumeProperty
		"""
		self.fixedImageData = imageData

		for index in range(3):
			if VTK_MAJOR_VERSION <= 5:
				self.imagePlaneWidgets[index].SetInput(self.fixedImageData)
			else:
				self.imagePlaneWidgets[index].SetInputData(self.fixedImageData)
			self.imagePlaneWidgets[index].SetPlaneOrientation(index)

		self.mapper.SetInput(0, self.fixedImageData)
		self.mapper.SetInput(1, self.movingImageData)

		self.renderer.ResetCamera()
		self.loadedData.emit()

	def setMovingData(self, imageData, volProp):
		"""
		:type imageData: vtkImageData
		:type volProp: VolumeProperty
		"""
		self.movingImageData = imageData

		self.mapper.SetInput(0, self.fixedImageData)
		self.mapper.SetInput(1, self.movingImageData)

		self.renderer.ResetCamera()
		self.loadedData.emit()

	def showSlice(self, index, value):
		"""
		:type index: int
		:type value: bool
		"""
		if value:
			self.imagePlaneWidgets[index].On()
		else:
			self.imagePlaneWidgets[index].Off()

	def opacityChangedForFixedVolume(self, value):
		self.fixedOpacity = value
		self.Update()

	def opacityChangedForMovingVolume(self, value):
		self.movingOpacity = value
		self.Update()

	def createFunctionFromOpacityAndVolumeProperty(self, opacity, volProp):
		"""
		:type opacityFunction: vtkVolumeProperty
		"""
		opacityFunction = volProp.GetScalarOpacity()
		for index in range(opacityFunction.GetSize()):
			val = [0 for x in range(4)]
			opacityFunction.GetNodeValue(index, val)
			val[1] = val[1] * float(opacity)
			opacityFunction.SetNodeValue(index, val)
		return opacityFunction

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

def CreateEmptyFunctions():
	"""
	:rtype: vtkColorTransferFunction, vtkPiecewiseFunction
	"""
	# Transfer functions and properties
	colorFunction = vtkColorTransferFunction()
	colorFunction.AddRGBPoint( 0, 0, 0, 0, 0.0, 0.0)
	colorFunction.AddRGBPoint( 1000, 0, 0, 0, 0.0, 0.0)

	opacityFunction = vtkPiecewiseFunction()
	opacityFunction.AddPoint( 0, 0, 0.0, 0.0)
	opacityFunction.AddPoint( 1000, 0, 0.0, 0.0)

	return colorFunction, opacityFunction
