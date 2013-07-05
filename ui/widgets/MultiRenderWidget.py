"""
MultiRenderWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from libvtkGPUMultiVolumeRenderPython import vtkOpenGLGPUMultiVolumeRayCastMapper
from vtk import vtkRenderer
from vtk import vtkInteractorStyleTrackballCamera
from ui.widgets.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


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

	def __init__(self):
		super(MultiRenderWidget, self).__init__()

		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)

		self.rwi = QVTKRenderWindowInteractor(parent=self)
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)

		self.mapper = vtkOpenGLGPUMultiVolumeRayCastMapper()

		self.fixedImageData = None
		self.fixedVolProp = None
		self.movingImageData = None
		self.movingVolProp = None

		# self.datasetMix = 0.5 # Value between 0 and 1.0
		self.fixedOpacity = 1.0
		self.movingOpacity = 1.0

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

	def Update(self):
		self.rwi.Render()

	def setFixedData(self, imageData, volProp):
		"""
		:type imageData: vtkImageData
		:type volProp: VolumeProperty
		"""
		self.fixedImageData = imageData
		self.fixedVolProp = volProp

	def setMovingData(self, imageData, volProp):
		"""
		:type imageData: vtkImageData
		:type volProp: VolumeProperty
		"""
		self.movingImageData = imageData
		self.movingVolProp = volProp
