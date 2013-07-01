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
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.DataReader import DataReader
from VolumeProperty import VolumePropertyFactory
from VolumeProperty import RenderTypeSimple
from VolumeProperty import RenderTypeCT
from VolumeProperty import RenderTypeMIP
from core.ImageDataResizer import ImageDataResizer

VTK_MAJOR_VERSION = vtkVersion.GetVTKMajorVersion()

class RenderWidget(QWidget):
	"""
	RenderWidget for rendering volumes. It has a few render types which can be
	set and adjusted.
	"""

	loadedData = Signal()

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

		self.renderType = None
		self.renderVolumeProperty = None
		self.imageData = None
		self.volumeProperties = [] # Keep track of used volume properties
		self.volume = None
		self.mapper = vtkOpenGLGPUVolumeRayCastMapper()

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

	def Update(self):
		self.rwi.Render()

	def SetRenderType(self, renderType):
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
		if self.renderVolumeProperty is not None:
			return self.renderVolumeProperty.GetParameterWidget()

		return QWidget()

	@Slot(basestring)
	def loadFile(self, fileName):
		# Cleanup the last loaded dataset
		if self.imageData is not None:
			self.renderer.RemoveViewProp(self.volume)

		if fileName is None:
			return

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		self.imageResizer = ImageDataResizer()
		self.imageData = self.imageResizer.ResizeData(imageData, maximum=28000000)

		# Set the render type
		self.SetRenderType(self.renderType)

		self.renderer.ResetCamera()
		self.loadedData.emit()
		self.Update()
	

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
