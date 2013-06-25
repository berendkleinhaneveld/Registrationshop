"""
RenderWidget

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkVolume
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkOpenGLGPUVolumeRayCastMapper
from vtk import vtkVolumeProperty
from vtk import vtkPiecewiseFunction
from vtk import vtkColorTransferFunction
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.DataReader import DataReader
from core.ImageDataResizer import ImageDataResizer

# Define Render Types
RenderTypeSimple = "RenderTypeSimple"
RenderTypeCT = "RenderTypeCT"
RenderTypeMIP = "RenderTypeMIP"

class RenderWidget(QWidget):
	"""
	RenderWidget for rendering volumes. It has a few render types which can be
	set and adjusted.
	"""

	def __init__(self):
		super(RenderWidget, self).__init__()

		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)

		self.rwi = QVTKRenderWindowInteractor(parent=self)
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)

		# -964.384 cloth
		# -656.56 skin
		# 20.144 Muscle
		# 137.168 Vascular stuff
		# 233.84 (Brittle) Bones
		# 394.112 Bones
		self.sections = [-3000.0, -964.384, -656.56, 20.144, 137.168, 233.84, 394.112, 6000.0]
		self.sectionsOpacity = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

		# sectionColors should be specified for each boundary
		# Just like opacity should be tweaked. A section can have any slope / configuration
		self.sectionColors = [  (1.0, 1.0, 1.0),
								(1.0, 0.0, 0.0),
								(0.0, 1.0, 0.0),
								(1.0, 0.7, 0.6),
								(1.0, 0.2, 0.2),
								(1.0, 0.9, 0.7),
								(0.9, 1.0, 0.9)]

		self.renderType = None
		self.imageData = None

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

	def Update(self):
		if self.renderType == RenderTypeSimple:
			self.UpdateTransferFunctionSimple()
		elif self.renderType == RenderTypeCT:
			self.UpdateTransferFunctionFromSections()
		elif self.renderType == RenderTypeMIP:
			self.UpdateTransferFunctionMIP()
		self.rwi.Render()

	def SetRenderType(self, renderType):
		if renderType == RenderTypeSimple:
			self.switchToSimple()
		elif renderType == RenderTypeCT:
			self.switchToCT()
		elif renderType == RenderTypeMIP:
			self.switchToMIP()

	def switchToSimple(self):
		self.renderType = RenderTypeSimple
		# Create property and attach the transfer function
		self.volumeProperty = vtkVolumeProperty()
		self.volumeProperty.SetIndependentComponents(True)
		self.volumeProperty.SetInterpolationTypeToLinear()
		self.volumeProperty.ShadeOn()
		self.volumeProperty.SetAmbient(0.1)
		self.volumeProperty.SetDiffuse(0.9)
		self.volumeProperty.SetSpecular(0.2)
		self.volumeProperty.SetSpecularPower(10.0)
		self.volumeProperty.SetScalarOpacityUnitDistance(0.8919)

		self.UpdateTransferFunctionSimple()

		self.mapper.SetBlendModeToComposite()
		self.volume.SetProperty(self.volumeProperty)
		self.rwi.Render()

	def switchToCT(self):
		self.renderType = RenderTypeCT
		# Create property and attach the transfer function
		self.volumeProperty = vtkVolumeProperty()
		self.volumeProperty.SetIndependentComponents(True)
		self.volumeProperty.SetInterpolationTypeToLinear()
		self.volumeProperty.ShadeOn()
		self.volumeProperty.SetAmbient(0.1)
		self.volumeProperty.SetDiffuse(0.9)
		self.volumeProperty.SetSpecular(0.2)
		self.volumeProperty.SetSpecularPower(10.0)
		self.volumeProperty.SetScalarOpacityUnitDistance(0.8919)

		self.UpdateTransferFunctionFromSections()

		self.mapper.SetBlendModeToComposite()
		self.volume.SetProperty(self.volumeProperty)
		self.rwi.Render()

	def switchToMIP(self):
		self.renderType = RenderTypeMIP
		# Create property and attach the transfer function
		self.volumeProperty = vtkVolumeProperty()
		self.volumeProperty.SetIndependentComponents(True);
		self.volumeProperty.SetInterpolationTypeToLinear();

		self.UpdateTransferFunctionMIP()

		self.mapper.SetBlendModeToMaximumIntensity()
		self.volume.SetProperty(self.volumeProperty)
		self.rwi.Render()

	def loadFile(self, fileName):
		# Cleanup the last loaded dataset
		if self.imageData is not None:
			self.renderer.RemoveViewProp(self.volume)

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		self.imageResizer = ImageDataResizer()
		self.imageData = self.imageResizer.ResizeData(imageData, maximum=28000000)

		# Find max and min
		self.minimum, self.maximum = self.imageData.GetScalarRange()
		self.lowerBound = self.minimum
		self.mipMin = self.minimum
		self.mipMax = self.maximum

		self.volume = vtkVolume()
		self.mapper = vtkOpenGLGPUVolumeRayCastMapper()
		self.mapper.SetBlendModeToComposite()
		self.mapper.SetInput(self.imageData)
		if self.renderType is None:
			self.SetRenderType(RenderTypeSimple)
			self.renderType = RenderTypeSimple
		else:
			# this might not be needed
			self.SetRenderType(self.renderType)
		
		self.volume.SetMapper(self.mapper)

		self.renderer.AddViewProp(self.volume)
		self.renderer.ResetCamera()

	def UpdateTransferFunctionFromSections(self):
		# Transfer functions and properties
		self.colorFunction = vtkColorTransferFunction()
		for x in range(0,len(self.sections)-1):
			r = self.sectionColors[x][0]
			g = self.sectionColors[x][1]
			b = self.sectionColors[x][2]
			self.colorFunction.AddRGBPoint(self.sections[x], r, g, b)
			self.colorFunction.AddRGBPoint(self.sections[x+1]-0.05, r, g, b)

		self.opacityFunction = vtkPiecewiseFunction()
		for x in range(0,len(self.sections)-1):
			self.opacityFunction.AddPoint(self.sections[x], self.sectionsOpacity[x])
			self.opacityFunction.AddPoint(self.sections[x+1]-0.05, self.sectionsOpacity[x])

		self.volumeProperty.SetColor(self.colorFunction)
		self.volumeProperty.SetScalarOpacity(self.opacityFunction)

	def UpdateTransferFunctionMIP(self):
		self.colorFunction = vtkColorTransferFunction()
		self.colorFunction.AddRGBSegment(0.0, 1.0, 1.0, 1.0, 255.0, 1, 1, 1)

		self.opacityFunction = vtkPiecewiseFunction()
		self.opacityFunction.AddSegment(min(self.mipMin, self.mipMax), 0.0,
										max(self.mipMin, self.mipMax), 1.0)

		self.volumeProperty.SetColor(self.colorFunction)
		self.volumeProperty.SetScalarOpacity(self.opacityFunction)

	def UpdateTransferFunctionSimple(self):
		# Transfer functions and properties
		self.colorFunction = vtkColorTransferFunction()
		self.colorFunction.AddRGBPoint(self.minimum, 1, 1, 1,)
		self.colorFunction.AddRGBPoint(self.lowerBound, 1, 1, 1)
		self.colorFunction.AddRGBPoint(self.lowerBound+1, 1, 1, 1)
		self.colorFunction.AddRGBPoint(self.maximum, 1, 1, 1)

		self.opacityFunction = vtkPiecewiseFunction()
		self.opacityFunction.AddPoint(self.minimum, 0)
		self.opacityFunction.AddPoint(self.lowerBound, 0)
		self.opacityFunction.AddPoint(self.lowerBound+1, 1)
		self.opacityFunction.AddPoint(self.maximum, 1)

		self.volumeProperty.SetColor(self.colorFunction)
		self.volumeProperty.SetScalarOpacity(self.opacityFunction)

if __name__ == '__main__':
	import sys
	from PySide.QtGui import QApplication
	app = QApplication(sys.argv)

	viewer = RenderWidget()

	viewer.rwi.Start()
	viewer.raise_()
	viewer.show()
	sys.exit(app.exec_())
