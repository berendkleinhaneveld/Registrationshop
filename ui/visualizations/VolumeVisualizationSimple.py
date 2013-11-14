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
from ui.widgets.SliderFloatWidget import SliderFloatWidget
from ui.widgets.ColorWidget import ColorChoiceWidget
from core.decorators import overrides
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtCore import Qt
from ColumnResizer import ColumnResizer


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
		colors = [[255, 139, 0], [0, 147, 255], [0, 255, 147], [213, 100, 255], [255, 75, 75]]
		self.colors = map(lambda x: [x[0] / 255.0, x[1] / 255.0, x[2] / 255.0], colors)
		self.color = self.colors[0]

	@overrides(VolumeVisualization)
	def getParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this
		volume property can be adjusted.
		:rtype: QWidget
		"""
		self.lowerBoundSlider = SliderFloatWidget()
		self.lowerBoundSlider.setName("Lower:")
		self.lowerBoundSlider.setRange([self.minimum, self.maximum])
		self.lowerBoundSlider.setValue(self.lowerBound)
		self.lowerBoundSlider.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		self.lowerBoundSlider.valueChanged.connect(self.valueChanged)

		self.upperBoundSlider = SliderFloatWidget()
		self.upperBoundSlider.setName("Upper:")
		self.upperBoundSlider.setRange([self.minimum, self.maximum])
		self.upperBoundSlider.setValue(self.upperBound)
		self.upperBoundSlider.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		self.upperBoundSlider.valueChanged.connect(self.valueChanged)

		self.colorChooser = ColorChoiceWidget()
		self.colorChooser.setName("Color:")
		self.colorChooser.setColors(self.colors)
		self.colorChooser.setColor(self.color)
		self.colorChooser.setMinimumHeight(self.upperBoundSlider.sizeHint().height())
		self.colorChooser.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		self.colorChooser.valueChanged.connect(self.valueChanged)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		layout.addWidget(self.lowerBoundSlider)
		layout.addWidget(self.upperBoundSlider)
		layout.addWidget(self.colorChooser)

		widget = QWidget()
		widget.setLayout(layout)

		self.columnResizer = ColumnResizer()
		self.columnResizer.addWidgetsFromLayout(self.lowerBoundSlider.layout(), 0)
		self.columnResizer.addWidgetsFromLayout(self.upperBoundSlider.layout(), 0)
		self.columnResizer.addWidgetsFromLayout(self.colorChooser.layout(), 0)

		self.otherColRes = ColumnResizer()
		self.otherColRes.addWidgetsFromLayout(self.lowerBoundSlider.layout(), 2)
		self.otherColRes.addWidgetsFromLayout(self.upperBoundSlider.layout(), 2)

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
	def setMapper(self, mapper):
		pass

	@overrides(VolumeVisualization)
	def shaderType(self):
		return 0

	@overrides(VolumeVisualization)
	def updateTransferFunction(self):
		r, g, b = self.color

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
		self.color = self.colorChooser.color

		self.updateTransferFunction()
