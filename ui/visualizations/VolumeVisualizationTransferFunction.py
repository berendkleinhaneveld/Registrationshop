"""
VolumeVisualizationTransferFunction

:Authors:
	Berend Klein Haneveld
"""
from VolumeVisualization import VolumeVisualization
from VolumeVisualization import VisualizationTypeTransferFunction
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from core.decorators import overrides
from ui.widgets.transferfunction import TransferFunctionWidget
from ui.widgets.transferfunction import TransferFunction


class VolumeVisualizationTransferFunction(VolumeVisualization):
	"""
	VolumeVisualization subclass for a simple visualization.
	"""
	def __init__(self):
		super(VolumeVisualizationTransferFunction, self).__init__()

		self.visualizationType = VisualizationTypeTransferFunction

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

		self.transferFunction = TransferFunction()

		self.minimum = 0
		self.maximum = 1
		self.histogramWidget = None
		self.imageData = None

	@overrides(VolumeVisualization)
	def getParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this
		volume property can be adjusted.
		:rtype: QWidget
		"""
		self.histogramWidget = TransferFunctionWidget()
		self.histogramWidget.transferFunction = self.transferFunction
		self.histogramWidget.valueChanged.connect(self.valueChanged)
		if self.imageData:
			self.histogramWidget.setImageData(self.imageData)

		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.histogramWidget, 0, 0, 1, 3)

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(VolumeVisualization)
	def setImageData(self, imageData):
		if imageData is None:
			self.minimum = 0.0
			self.maximum = 1.0
			self.imageData = None
			return

		self.imageData = imageData
		self.minimum, self.maximum = imageData.GetScalarRange()
		self.transferFunction.setRange([self.minimum, self.maximum])

	@overrides(VolumeVisualization)
	def setMapper(self, mapper):
		pass

	@overrides(VolumeVisualization)
	def shaderType(self):
		return 0

	@overrides(VolumeVisualization)
	def updateTransferFunction(self):
		if self.histogramWidget:
			self.histogramWidget.transferFunction.updateTransferFunction()
			self.colorFunction = self.histogramWidget.transferFunction.colorFunction
			self.opacityFunction = self.histogramWidget.transferFunction.opacityFunction
		else:
			# Transfer functions and properties
			self.colorFunction = vtkColorTransferFunction()
			self.colorFunction.AddRGBPoint(self.minimum, 0, 0, 0)
			self.colorFunction.AddRGBPoint(self.maximum, 0, 0, 0)

			self.opacityFunction = vtkPiecewiseFunction()
			self.opacityFunction.AddPoint(self.minimum, 0)
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
		self.updateTransferFunction()
