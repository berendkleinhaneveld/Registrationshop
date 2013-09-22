"""
VolumeVisualizationMIP

:Authors:
	Berend Klein Haneveld
"""
from VolumeVisualization import VolumeVisualization
from VolumeVisualization import VisualizationTypeMIP
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from vtk import vtkVolumeMapper
from PySide.QtGui import QWidget
from PySide.QtGui import QSlider
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Qt
from core.decorators import overrides


class VolumeVisualizationMIP(VolumeVisualization):
	"""
	VolumeVisualization subclass for MIP visualization.
	"""
	def __init__(self):
		super(VolumeVisualizationMIP, self).__init__()

		self.visualizationType = VisualizationTypeMIP
		self.mapper = None

		# Create property and attach the transfer function
		self.volProp = vtkVolumeProperty()
		self.volProp.SetIndependentComponents(True)
		self.volProp.SetInterpolationTypeToLinear()

	@overrides(VolumeVisualization)
	def getParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this
		volume property can be adjusted.
		:rtype: QWidget
		"""
		self.windowSlider = QSlider(Qt.Horizontal)
		self.windowSlider.setMinimum(0)
		self.windowSlider.setMaximum(int(abs(self.maximum - self.minimum)))
		self.windowSlider.setValue(int(self.window))
		self.windowSlider.valueChanged.connect(self.valueChanged)
		self.windowLabel = QLabel(str(self.window))

		self.levelSlider = QSlider(Qt.Horizontal)
		self.levelSlider.setMinimum(int(self.minimum))
		self.levelSlider.setMaximum(int(self.maximum))
		self.levelSlider.setValue(int(self.level))
		self.levelSlider.valueChanged.connect(self.valueChanged)
		self.levelLabel = QLabel(str(self.level))

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

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Window"), 0, 0)
		layout.addWidget(self.windowSlider, 0, 1)
		layout.addWidget(self.windowLabel, 0, 2)
		layout.addWidget(QLabel("Level"), 1, 0)
		layout.addWidget(self.levelSlider, 1, 1)
		layout.addWidget(self.levelLabel, 1, 2)
		layout.addWidget(QLabel("Lower bound"), 2, 0)
		layout.addWidget(self.lowerBoundSlider, 2, 1)
		layout.addWidget(self.lowerBoundLabel, 2, 2)
		layout.addWidget(QLabel("Upper bound"), 3, 0)
		layout.addWidget(self.upperBoundSlider, 3, 1)
		layout.addWidget(self.upperBoundLabel, 3, 2)

		widget = QWidget()
		widget.setLayout(layout)

		return widget

	@overrides(VolumeVisualization)
	def setImageData(self, imageData):
		self.imageData = imageData
		if imageData is None:
			self.minimum = 0.0
			self.maximum = 1.0
			self.window = 1.0
			self.level = 0.5
			self.lowerBound = self.minimum
			self.upperBound = self.maximum
			return

		self.minimum, self.maximum = imageData.GetScalarRange()
		self.lowerBound = self.minimum
		self.upperBound = self.maximum
		self.window = abs(self.maximum - self.minimum)
		self.level = (self.maximum + self.minimum) / 2.0

	@overrides(VolumeVisualization)
	def configureMapper(self, mapper):
		self.mapper = mapper
		self.mapper.SetShaderType(1)
		# TODO: get the message to the multi render mapper

	@overrides(VolumeVisualization)
	def updateTransferFunction(self):
		self.colorFunction, self.opacityFunction = CreateRangeFunctions(self.imageData, self.window, self.level)
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
		self.lowerBound = self.lowerBoundSlider.value()
		self.upperBound = self.upperBoundSlider.value()
		self.level = self.levelSlider.value()
		self.window = self.windowSlider.value()

		self.lowerBoundLabel.setText(str(self.lowerBound))
		self.upperBoundLabel.setText(str(self.upperBound))
		self.levelLabel.setText(str(self.level))
		self.windowLabel.setText(str(self.window))

		lowerBound = (self.lowerBound - self.minimum) / (self.maximum - self.minimum)
		upperBound = (self.upperBound - self.minimum) / (self.maximum - self.minimum)
		self.mapper.SetLowerBound(lowerBound)
		self.mapper.SetUpperBound(upperBound)
		self.updateTransferFunction()


def CreateRangeFunctions(imageData, window, level):
	"""
	:type imageData: vktImageData
	:type color: array of length 3 (r, g, b)
	:rtype: vtkColorTransferFunction, vtkPiecewiseFunction
	"""
	minimum, maximum = imageData.GetScalarRange()

	minV = level - 0.5*window
	maxV = level + 0.5*window

	colorFunction = vtkColorTransferFunction()
	colorFunction.AddRGBSegment(minV, 0, 0, 0, maxV, 1, 1, 1)

	opacityFunction = vtkPiecewiseFunction()
	opacityFunction.AddSegment(minimum, 1.0, maximum, 1.0)

	return colorFunction, opacityFunction
