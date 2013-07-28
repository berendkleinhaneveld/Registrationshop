"""
RenderWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkVolume
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkOpenGLGPUVolumeRayCastMapper
from vtk import vtkVersion
from vtk import vtkOrientationMarkerWidget
from vtk import vtkAxesActor
from vtk import vtkImagePlaneWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from VolumeProperty import VolumePropertyFactory
from VolumeProperty import RenderTypeSimple
from VolumeProperty import RenderTypeCT
from VolumeProperty import RenderTypeMIP
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.data.DataReader import DataReader
from core.data.DataResizer import DataResizer

VTK_MAJOR_VERSION = vtkVersion.GetVTKMajorVersion()

class RenderWidget(QWidget):
	"""
	RenderWidget for rendering volumes. It has a few render types which can be
	set and adjusted.
	"""

	loadedData = Signal()
	updated = Signal()

	def __init__(self):
		super(RenderWidget, self).__init__()

		self.renderTypes = [RenderTypeSimple, RenderTypeCT, RenderTypeMIP]

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

		self.renderType = None
		self.renderVolumeProperty = None
		self.imageData = None
		self.volumeProperties = [] # Keep track of used volume properties
		self.volume = None
		self.mapper = vtkOpenGLGPUVolumeRayCastMapper()

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

	def Update(self):
		self.rwi.Render()
		self.updated.emit()

	def SetRenderType(self, renderType):
		"""
		Swithes the renderer to the given render type. Previously used render 
		types are saved so that switching back to a previously used render type 
		will produce the same visualization as before.

		:type renderType: str
		"""
		self.renderType = renderType
		if self.renderType is None:
			self.renderType = RenderTypeSimple

		if self.volume is not None:
			self.renderer.RemoveViewProp(self.volume)

		self.volume = vtkVolume()
		if VTK_MAJOR_VERSION <= 5:
			self.mapper.SetInput(self.imageData)
		else:
			self.mapper.SetInputData(self.imageData)

		foundPreviouslyUsedProperty = False
		for volProp in self.volumeProperties:
			if volProp.renderType == renderType:
				self.renderVolumeProperty = volProp
				foundPreviouslyUsedProperty = True
				break

		if not foundPreviouslyUsedProperty:
			self.renderVolumeProperty = VolumePropertyFactory.CreateProperty(self.renderType, self.mapper)
			self.renderVolumeProperty.SetImageData(self.imageData)
			self.volumeProperties.append(self.renderVolumeProperty)

		self.renderVolumeProperty.UpdateTransferFunction()

		self.volume.SetProperty(self.renderVolumeProperty.volumeProperty)
		self.volume.SetMapper(self.mapper)
		self.renderer.AddViewProp(self.volume)

	def GetParameterWidget(self):
		"""
		:rtype QWidget
		"""
		if self.renderVolumeProperty is not None:
			return self.renderVolumeProperty.GetParameterWidget()

		return QWidget()

	def showSlice(self, index, value):
		"""
		:type index: int
		:type value: bool
		"""
		if value:
			self.imagePlaneWidgets[index].On()
		else:
			self.imagePlaneWidgets[index].Off()

	@Slot(basestring)
	def loadFile(self, fileName):
		"""
		:type fileName: str
		"""
		# Cleanup the last loaded dataset
		if self.imageData is not None:
			self.renderer.RemoveViewProp(self.volume)

		# Clear out the old render types
		self.volumeProperties = []

		if fileName is None:
			self.imageData = None
			self.loadedData.emit()
			self.Update()
			return

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		imageResizer = DataResizer()
		self.imageData = imageResizer.ResizeData(imageData, maximum=18000000)

		for index in range(3):
			if VTK_MAJOR_VERSION <= 5:
				self.imagePlaneWidgets[index].SetInput(self.imageData)
			else:
				self.imagePlaneWidgets[index].SetInputData(self.imageData)
			self.imagePlaneWidgets[index].SetPlaneOrientation(index)

		# Set the render type
		self.SetRenderType(self.renderType)

		self.renderer.ResetCamera()
		self.loadedData.emit()
		self.Update()
	
	def exportSettings(self):
		"""
		Create RenderWidgetSettings object from current state.
		The returned object can be converted into a yaml object.
		:rtype: RenderWidgetSettings
		"""
		pass

	def loadSettings(self, settings):
		"""
		Read from settings the value for parameters.
		:type settings: RenderWidgetSettings
		"""
		pass


class RenderSettings(object):
	"""
	RenderSettings is an object that stores information about the render 
	settings of a render widget.
	"""
	def __init__(self):
		super(RenderSettings, self).__init__()
		

if __name__ == '__main__':
	import sys
	from PySide.QtGui import QApplication
	app = QApplication(sys.argv)

	viewer = RenderWidget()
	viewer.loadFile("/Users/beer/RegistrationShop/Data/Medical/Noeska/CT.mhd")

	viewer.rwi.Start()
	viewer.raise_()
	viewer.show()
	sys.exit(app.exec_())
