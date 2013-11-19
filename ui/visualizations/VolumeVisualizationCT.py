"""
VolumeVisualizationCT

:Authors:
	Berend Klein Haneveld
"""
import math
from VolumeVisualization import VolumeVisualization
from VolumeVisualization import VisualizationTypeCT
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from PySide.QtGui import QWidget
from PySide.QtGui import QSlider
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Qt
from core.decorators import overrides


class VolumeVisualizationCT(VolumeVisualization):
	"""
	VolumeVisualization subclass for CT visualization
	"""
	def __init__(self):
		super(VolumeVisualizationCT, self).__init__()

		self.visualizationType = VisualizationTypeCT

		# Cloth, Skin, Muscle, Vascular stuff, Cartilage, Bones
		self.sections = [-3000.0, -964.384, -656.56, 20.144, 137.168, 233.84, 394.112, 6000.0]
		self.sectionsOpacity = [0.0, 0.0, 0.0, 0.0, 0.07, 0.1, 0.2]
		self.sectionNames = ["Air:", "Cloth:", "Skin:", "Muscle:", "Blood vessels:", "Cartilage:", "Bones:"]

		# sectionColors should be specified for each boundary
		# Just like opacity should be tweaked. A section can have any slope / configuration
		self.sectionColors = [(1.0, 1.0, 1.0),
							(0.0, 1.0, 0.0),
							(1.0, 0.9, 0.8),
							(1.0, 0.7, 0.6),
							(1.0, 0.2, 0.2),
							(1.0, 0.9, 0.7),
							(0.9, 1.0, 0.9)]

		# Create property and attach the transfer function
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
		# Transfer functions and properties
		self.colorFunction = vtkColorTransferFunction()
		for x in range(len(self.sections)-1):
			r = self.sectionColors[x][0]
			g = self.sectionColors[x][1]
			b = self.sectionColors[x][2]
			self.colorFunction.AddRGBPoint(self.sections[x], r, g, b)
			self.colorFunction.AddRGBPoint(self.sections[x+1]-0.05, r, g, b)

		self.opacityFunction = vtkPiecewiseFunction()
		for x in range(len(self.sections)-1):
			self.opacityFunction.AddPoint(self.sections[x], self.sectionsOpacity[x])
			self.opacityFunction.AddPoint(self.sections[x+1]-0.05, self.sectionsOpacity[x])

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
		pass

	@overrides(VolumeVisualization)
	def getParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this
		volume property can be adjusted.
		:rtype: QWidget
		"""
		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setAlignment(Qt.AlignTop)

		self.sliders = []
		for index in range(7):
			slider = QSlider(Qt.Horizontal)
			slider.setMinimum(0)
			slider.setMaximum(1000)
			slider.setValue(int(math.pow(self.sectionsOpacity[index], 1.0/3.0) * slider.maximum()))
			slider.valueChanged.connect(self.valueChanged)
			self.sliders.append(slider)
			label = QLabel(self.sectionNames[index])
			label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
			layout.addWidget(label, index, 0)
			layout.addWidget(slider, index, 1)

		try:
			from ColumnResizer import ColumnResizer
			columnResizer = ColumnResizer()
			columnResizer.addWidgetsFromLayout(layout, 0)
		except Exception, e:
			print e

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(VolumeVisualization)
	def valueChanged(self, value):
		"""
		Parameter 'value' is unused. This is a callback for all the
		interactive widgets in the parameter widget.
		"""
		for index in range(len(self.sliders)):
			slider = self.sliders[index]
			sliderValue = float(slider.value()) / float(slider.maximum())
			# Use an square function for easier opacity adjustments
			convertedValue = math.pow(sliderValue, 3.0)
			self.sectionsOpacity[index] = convertedValue

		self.updateTransferFunction()
