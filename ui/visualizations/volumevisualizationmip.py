"""
VolumeVisualizationMIP

:Authors:
	Berend Klein Haneveld
"""
from volumevisualization import VolumeVisualization
from volumevisualization import VisualizationTypeMIP
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

		# TODO: add two sliders with which to threshold the data
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
		self.lowerBoundSlider = QSlider(Qt.Horizontal)
		self.lowerBoundSlider.setMinimum(int(self.minimum))
		self.lowerBoundSlider.setMaximum(int(self.maximum))
		self.lowerBoundSlider.setValue(int(self.lowerBound))
		self.lowerBoundSlider.valueChanged.connect(self.valueChanged)

		self.upperBoundSlider = QSlider(Qt.Horizontal)
		self.upperBoundSlider.setMinimum(int(self.minimum))
		self.upperBoundSlider.setMaximum(int(self.maximum))
		self.upperBoundSlider.setValue(int(self.upperBound))
		self.upperBoundSlider.valueChanged.connect(self.valueChanged)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Lower bound"), 0, 0)
		layout.addWidget(self.lowerBoundSlider, 0, 1)
		layout.addWidget(QLabel("Upper bound"), 1, 0)
		layout.addWidget(self.upperBoundSlider, 1, 1)

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
		if mapper is not None and mapper.GetBlendMode() != vtkVolumeMapper.MAXIMUM_INTENSITY_BLEND:
			mapper.SetBlendModeToMaximumIntensity()

	@overrides(VolumeVisualization)
	def updateTransferFunction(self):
		self.colorFunction = vtkColorTransferFunction()
		self.colorFunction.AddRGBSegment(0.0, 1.0, 1.0, 1.0, 255.0, 1, 1, 1)

		self.opacityFunction = vtkPiecewiseFunction()
		self.opacityFunction.AddSegment(min(self.lowerBound, self.upperBound), 0.0,
										max(self.lowerBound, self.upperBound), 1.0)

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
		self.updateTransferFunction()
