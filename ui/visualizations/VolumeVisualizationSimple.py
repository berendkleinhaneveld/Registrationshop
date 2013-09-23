"""
VolumeVisualizationSimple

:Authors:
	Berend Klein Haneveld
"""
from VolumeVisualization import VolumeVisualization
from VolumeVisualization import VisualizationTypeSimple
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from vtk import vtkMath
from PySide.QtGui import QWidget
from PySide.QtGui import QSlider
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Qt
from core.decorators import overrides


class VolumeVisualizationSimple(VolumeVisualization):
	"""
	VolumeVisualization subclass for a simple visualization.
	"""
	def __init__(self):
		super(VolumeVisualizationSimple, self).__init__()

		self.visualizationType = VisualizationTypeSimple

		# Create the volume property
		self.volProp = vtkVolumeProperty()
		self.volProp.SetIndependentComponents(True)
		self.volProp.SetInterpolationTypeToLinear()
		self.volProp.ShadeOn()
		self.volProp.SetAmbient(0.1)
		self.volProp.SetDiffuse(0.9)
		self.volProp.SetSpecular(0.2)
		self.volProp.SetSpecularPower(10.0)
		self.volProp.SetScalarOpacityUnitDistance(0.8919)

		self.minimum = 0
		self.maximum = 1
		self.lowerBound = 0
		self.upperBound = 1
		self.hue = 0  # 0-360

	@overrides(VolumeVisualization)
	def getParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this
		volume property can be adjusted.
		:rtype: QWidget
		"""
		self.lowerBoundSlider = QSlider(Qt.Horizontal)
		self.lowerBoundSlider.setMinimum(int(self.minimum))
		self.lowerBoundSlider.setMaximum(int(self.maximum))
		self.lowerBoundSlider.setValue(int(self.lowerBound))
		self.lowerBoundSlider.valueChanged.connect(self.valueChanged)
		self.lowerBoundLabel = QLabel(str(self.lowerBound))

		self.upperBoundSlider = QSlider(Qt.Horizontal)
		self.upperBoundSlider.setMinimum(int(self.minimum))
		self.upperBoundSlider.setMaximum(int(self.maximum))
		self.upperBoundSlider.setValue(int(self.upperBound))
		self.upperBoundSlider.valueChanged.connect(self.valueChanged)
		self.upperBoundLabel = QLabel(str(self.upperBound))

		self.hueSlider = QSlider(Qt.Horizontal)
		self.hueSlider.setMinimum(0)
		self.hueSlider.setMaximum(360)
		self.hueSlider.setValue(self.hue)
		self.hueSlider.valueChanged.connect(self.valueChanged)
		self.hueLabel = QLabel(str(self.hue))

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Lower threshold"), 0, 0)
		layout.addWidget(self.lowerBoundSlider, 0, 1)
		layout.addWidget(self.lowerBoundLabel, 0, 2)
		layout.addWidget(QLabel("Upper threshold"), 1, 0)
		layout.addWidget(self.upperBoundSlider, 1, 1)
		layout.addWidget(self.upperBoundLabel, 1, 2)
		layout.addWidget(QLabel("Hue"), 2, 0)
		layout.addWidget(self.hueSlider, 2, 1)
		layout.addWidget(self.hueLabel, 2, 2)

		widget = QWidget()
		widget.setLayout(layout)

		return widget

	@overrides(VolumeVisualization)
	def setImageData(self, imageData):
		if imageData is None:
			self.minimum = 0.0
			self.maximum = 1.0
			self.lowerBound = self.minimum
			self.upperBound = self.maximum
			return

		self.minimum, self.maximum = imageData.GetScalarRange()
		self.lowerBound = self.minimum
		self.upperBound = self.maximum

	@overrides(VolumeVisualization)
	def configureMapper(self, mapper):
		mapper.SetShaderType(0)

	@overrides(VolumeVisualization)
	def updateTransferFunction(self):
		r = g = b = 0.0
		saturation = 1.0
		value = 1.0
		hue = self.hue / 360.0
		r, g, b = vtkMath.HSVToRGB(hue, saturation, value)
		# r,g,b = [self.hue / 360.0 for i in range(3)]

		# Transfer functions and properties
		self.colorFunction = vtkColorTransferFunction()
		self.colorFunction.AddRGBPoint(self.minimum, r, g, b)
		self.colorFunction.AddRGBPoint(self.lowerBound, r, g, b)
		self.colorFunction.AddRGBPoint(self.lowerBound+1, r, g, b)
		self.colorFunction.AddRGBPoint(self.maximum, r, g, b)

		self.opacityFunction = vtkPiecewiseFunction()
		self.opacityFunction.AddPoint(self.minimum, 0)
		self.opacityFunction.AddPoint(self.lowerBound, 0)
		self.opacityFunction.AddPoint(self.lowerBound+1, 1)
		self.opacityFunction.AddPoint(self.upperBound-1, 1)
		self.opacityFunction.AddPoint(self.upperBound, 0)
		self.opacityFunction.AddPoint(self.maximum, 0)

		self.volProp.SetColor(self.colorFunction)
		self.volProp.SetScalarOpacity(self.opacityFunction)

		self.updatedTransferFunction.emit()

	@overrides(VolumeVisualization)
	def valueChanged(self, value):
		"""
		This method is called when the value of one of the sliders / fields is
		adjusted. Argument value is unused. It is just there so that it can be
		connected to the signals of the interface elements.

		:type value: int
		"""
		self.lowerBound = min(self.lowerBoundSlider.value(), self.upperBoundSlider.value())
		self.upperBound = max(self.lowerBoundSlider.value(), self.upperBoundSlider.value())
		self.hue = self.hueSlider.value()

		self.lowerBoundLabel.setText(str(self.lowerBound))
		self.upperBoundLabel.setText(str(self.upperBound))
		self.hueLabel.setText(str(self.hue))

		self.updateTransferFunction()
