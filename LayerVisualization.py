
"""
LayerVisualization

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkRenderer
from vtk import vtkVolume
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkOpenGLGPUVolumeRayCastMapper
from vtk import *
from PySide.QtCore import Qt
from PySide.QtGui import QPushButton
from PySide.QtGui import QIcon
from PySide.QtGui import QGridLayout
from PySide.QtGui import QFileDialog
from PySide.QtGui import QSlider
from PySide.QtGui import QWidget
from ui.ButtonContainer import ButtonContainer
from core.AppVars import AppVars
from core.DataReader import DataReader
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from core.ImageDataResizer import ImageDataResizer

class LayerVisualization(QWidget):
	"""
	LayerVisualization
	"""

	def __init__(self):
		super(LayerVisualization, self).__init__()
		
		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)

		self.rwi = QVTKRenderWindowInteractor(parent=self)
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)

		# Create container for action buttons
		self.actionButtons = ButtonContainer(Qt.Horizontal)
		button = QPushButton()
		button.setIcon(QIcon(AppVars.imagePath() + "AddButton.png"))
		button.clicked.connect(self.loadFile)
		self.actionButtons.addButton(button)

		self.slider = QSlider(Qt.Horizontal)
		self.slider.setMinimum(0)
		self.slider.setMaximum(1000)
		self.slider.valueChanged.connect(self.valueChanged)

		# Interface stuff
		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		layout.addWidget(self.actionButtons, 1, 0)

		self.setLayout(layout)

	def valueChanged(self):
		sliderValue = float(self.slider.value()) / float(self.slider.maximum())
		self.lowerBound = self.minimum + (self.maximum - self.minimum) * sliderValue
		self.UpdateTransferFunction()
		self.rwi.Render()

	def loadFile(self):
		extensions = DataReader().GetSupportedExtensionsAsString()
		fileName, other = QFileDialog.getOpenFileName(self, "Open fixed data set", "", "Images ("+extensions+")")
		if len(fileName) == 0:
			return

		# Replace load data button with slider
		layout = self.layout()
		layout.removeWidget(self.actionButtons)
		layout.addWidget(self.slider, 1, 0)
		self.setLayout(layout)

		# TODO: clear old data
		dataReader = DataReader()
		self.imageData = dataReader.GetImageData(fileName)

		imageResizer = ImageDataResizer()
		self.imageData = imageResizer.ResizeData(self.imageData, maximum=19000000)

		self.minimum, self.maximum = GetMaxAndMinValue(self.imageData)
		self.lowerBound = self.minimum

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

		self.UpdateTransferFunction()

		self.volume = vtkVolume()
		self.mapper = vtkOpenGLGPUVolumeRayCastMapper()
		self.mapper.SetBlendModeToComposite()
		self.mapper.SetInput(self.imageData)
		self.volume.SetProperty(self.volumeProperty)
		self.volume.SetMapper(self.mapper)

		self.renderer.AddViewProp(self.volume)
		self.renderer.ResetCamera()

	def UpdateTransferFunction(self):
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

def GetMaxAndMinValue(imageData):
	min = max = 0
	
	stepSize = 5
	dimensions = imageData.GetDimensions()
	for z in xrange(0, dimensions[2]-1, stepSize):
		for y in xrange(0, dimensions[1]-1, stepSize):
			for x in xrange(0, dimensions[0]-1, stepSize):
				value = imageData.GetScalarComponentAsFloat(x, y, z, 0)
				if value < min:
					min = value
				elif value > max:
					max = value

	return min, max

if __name__ == '__main__':
	import sys
	from PySide.QtGui import QApplication
	app = QApplication(sys.argv)

	viewer = LayerVisualization()

	viewer.rwi.GetRenderWindow().SetSize(1024,768)
	viewer.rwi.Start()
	viewer.raise_()
	viewer.show()
	sys.exit(app.exec_())
