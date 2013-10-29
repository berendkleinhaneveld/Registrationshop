"""
VolumeVisualizationRamp

:Authors:
	Berend Klein Haneveld
"""
from VolumeVisualization import VolumeVisualization
from VolumeVisualization import VisualizationTypeRamp
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtCore import Qt
from core.decorators import overrides


class VolumeVisualizationRamp(VolumeVisualization):
	"""VolumeVisualizationRamp is a volume property that just maps values
	on a ramp from 0 to 1."""
	def __init__(self):
		super(VolumeVisualizationRamp, self).__init__()

		self.visualizationType = VisualizationTypeRamp

		self.volProp = vtkVolumeProperty()
		self.volProp.SetIndependentComponents(True)
		self.volProp.SetInterpolationTypeToLinear()
		self.volProp.ShadeOn()
		self.volProp.SetAmbient(0.1)
		self.volProp.SetDiffuse(0.9)
		self.volProp.SetSpecular(0.2)
		self.volProp.SetSpecularPower(10.0)
		self.volProp.SetScalarOpacityUnitDistance(0.8919)

	@overrides(VolumeVisualization)
	def setMapper(self, mapper):
		pass

	@overrides(VolumeVisualization)
	def shaderType(self):
		return 0

	@overrides(VolumeVisualization)
	def updateTransferFunction(self):
		# Transfer function and property
		self.colorFunction = vtkColorTransferFunction()
		self.colorFunction.AddRGBSegment(self.minimum, 0.0, 0.0, 0.0, self.maximum, 1.0, 1.0, 1.0)

		self.opacityFunction = vtkPiecewiseFunction()
		self.opacityFunction.AddSegment(self.minimum, 0.0, self.maximum, 1.0)

		self.volProp.SetColor(self.colorFunction)
		self.volProp.SetScalarOpacity(self.opacityFunction)

		self.updatedTransferFunction.emit()

	@overrides(VolumeVisualization)
	def setImageData(self, imageData):
		"""
		Nothing needs to be done for CT scans. The values of the sliders are
		not dependent on the imageData.
		:type imageData: vtkImageData
		"""
		self.minimum, self.maximum = imageData.GetScalarRange()

	@overrides(VolumeVisualization)
	def getParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this
		volume property can be adjusted.
		:rtype: QWidget
		"""
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(VolumeVisualization)
	def valueChanged(self, value):
		"""
		Parameter 'value' is unused. This is a callback for all the
		interactive widgets in the parameter widget.
		"""
		self.updateTransferFunction()
