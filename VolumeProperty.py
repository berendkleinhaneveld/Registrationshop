"""
VolumeProperty

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from vtk import vtkVolumeMapper
from PySide.QtGui import QWidget
from PySide.QtGui import QSlider
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtCore import QObject
from decorators import overrides
import math

# Define Render Types
RenderTypeSimple = "Simple"
RenderTypeCT = "CT"
RenderTypeMIP = "MIP"

class VolumePropertyFactory(object):
	"""
	VolumePropertyFactory makes and creates proper VolumeProperty objects.
	"""
	
	@classmethod
	def CreateProperty(cls, renderType, mapper):
		if renderType == RenderTypeSimple:
			return SimpleVolumeProperty(mapper)
		elif renderType == RenderTypeCT:
			return CTVolumeProperty(mapper)
		elif renderType == RenderTypeMIP:
			return MIPVolumeProperty(mapper)

class VolumeProperty(QObject):
	"""
	VolumeProperty is an interface class for the different render types
	"""

	updatedTransferFunction = Signal()

	def __init__(self):
		super(VolumeProperty, self).__init__()

		self.volumeProperty = None
		self.renderType = None

	def GetParameterWidget(self):
		"""
		This method should be overridden in the subclasses.
		:rtype: QWidget
		"""
		raise NotImplementedError()

	def SetImageData(self, imageData):
		"""
		This method should be overridden in the subclasses.
		:type imageData: vtkImageData
		"""
		raise NotImplementedError()

	def UpdateTransferFunction(self):
		raise NotImplementedError()

	def valueChanged(self, value):
		raise NotImplementedError()

class CTVolumeProperty(VolumeProperty):
	"""
	VolumeProperty subclass for CT visualization
	"""
	def __init__(self, mapper):
		super(CTVolumeProperty, self).__init__()

		self.renderType = RenderTypeCT

		# Cloth, Skin, Muscle, Vascular stuff, Cartilage, Bones
		self.sections = [-3000.0, -964.384, -656.56, 20.144, 137.168, 233.84, 394.112, 6000.0]
		self.sectionsOpacity = [0.0, 0.0, 0.0, 0.0, 0.07, 0.1, 0.2]
		self.sectionNames = ["Air", "Cloth", "Skin", "Muscle", "Blood vessels", "Cartilage", "Bones"]

		# sectionColors should be specified for each boundary
		# Just like opacity should be tweaked. A section can have any slope / configuration
		self.sectionColors = [  (1.0, 1.0, 1.0),
								(0.0, 1.0, 0.0),
								(1.0, 0.9, 0.8),
								(1.0, 0.7, 0.6),
								(1.0, 0.2, 0.2),
								(1.0, 0.9, 0.7),
								(0.9, 1.0, 0.9)]

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

		self.mapper = mapper

	@overrides(VolumeProperty)
	def UpdateTransferFunction(self):
		if self.mapper.GetBlendMode() != vtkVolumeMapper.COMPOSITE_BLEND:
			self.mapper.SetBlendModeToComposite()

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

		self.updatedTransferFunction.emit()

	@overrides(VolumeProperty)
	def SetImageData(self, imageData):
		"""
		Nothing needs to be done for CT scans. The values of the sliders are
		not dependent on the imageData.
		:type imageData: vtkImageData
		"""
		pass
		
	@overrides(VolumeProperty)
	def GetParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this 
		volume property can be adjusted. 
		:rtype: QWidget
		"""
		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)

		self.sliders = []
		for index in range(0, 7):
			slider = QSlider(Qt.Horizontal)
			slider.setMinimum(0)
			slider.setMaximum(1000)
			slider.setValue(int(math.pow(self.sectionsOpacity[index], 1.0/3.0) * slider.maximum()))
			slider.valueChanged.connect(self.valueChanged)
			self.sliders.append(slider)
			layout.addWidget(QLabel(self.sectionNames[index]))
			layout.addWidget(slider)

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(VolumeProperty)
	def valueChanged(self, value):
		for index in range(0, len(self.sliders)):
			slider = self.sliders[index]
			sliderValue = float(slider.value()) / float(slider.maximum())
			# Use an square function for easier opacity adjustments
			convertedValue = math.pow(sliderValue, 3.0)
			self.sectionsOpacity[index] = convertedValue

		self.UpdateTransferFunction()

class MIPVolumeProperty(VolumeProperty):
	"""
	VolumeProperty subclass for MIP visualization.
	"""
	def __init__(self, mapper):
		super(MIPVolumeProperty, self).__init__()

		self.renderType = RenderTypeMIP

		# Create property and attach the transfer function
		self.volumeProperty = vtkVolumeProperty()
		self.volumeProperty.SetIndependentComponents(True);
		self.volumeProperty.SetInterpolationTypeToLinear();

		self.mapper = mapper

	@overrides(VolumeProperty)
	def GetParameterWidget(self):
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

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.lowerBoundSlider)
		layout.addWidget(self.upperBoundSlider)

		widget = QWidget()
		widget.setLayout(layout)

		return widget

	@overrides(VolumeProperty)
	def SetImageData(self, imageData):
		self.imageData = imageData

		if self.imageData is None:
			self.minimum = 0.0
			self.maximum = 1.0
			self.lowerBound = self.minimum
			self.upperBound = self.maximum
			return

		self.minimum, self.maximum = self.imageData.GetScalarRange()
		self.lowerBound = self.minimum
		self.upperBound = self.maximum

	@overrides(VolumeProperty)
	def UpdateTransferFunction(self):
		if self.mapper.GetBlendMode() != vtkVolumeMapper.MAXIMUM_INTENSITY_BLEND:
			self.mapper.SetBlendModeToMaximumIntensity()

		self.colorFunction = vtkColorTransferFunction()
		self.colorFunction.AddRGBSegment(0.0, 1.0, 1.0, 1.0, 255.0, 1, 1, 1)

		self.opacityFunction = vtkPiecewiseFunction()
		self.opacityFunction.AddSegment(min(self.lowerBound, self.upperBound), 0.0,
										max(self.lowerBound, self.upperBound), 1.0)

		self.volumeProperty.SetColor(self.colorFunction)
		self.volumeProperty.SetScalarOpacity(self.opacityFunction)

		self.updatedTransferFunction.emit()

	@overrides(VolumeProperty)
	def valueChanged(self, value):
		"""
		This method is called when the value of one of the sliders / fields is 
		adjusted. Argument value is unused. It is just there so that it can be 
		connected to the signals of the interface elements.

		:type value: int
		"""
		self.lowerBound = self.lowerBoundSlider.value()
		self.upperBound = self.upperBoundSlider.value()
		self.UpdateTransferFunction()

class SimpleVolumeProperty(VolumeProperty):
	"""
	VolumeProperty subclass for a simple visualization.
	"""
	def __init__(self, mapper):
		super(SimpleVolumeProperty, self).__init__()

		self.renderType = RenderTypeSimple

		# Create the volume property
		self.volumeProperty = vtkVolumeProperty()
		self.volumeProperty.SetIndependentComponents(True)
		self.volumeProperty.SetInterpolationTypeToLinear()
		self.volumeProperty.ShadeOn()
		self.volumeProperty.SetAmbient(0.1)
		self.volumeProperty.SetDiffuse(0.9)
		self.volumeProperty.SetSpecular(0.2)
		self.volumeProperty.SetSpecularPower(10.0)
		self.volumeProperty.SetScalarOpacityUnitDistance(0.8919)

		self.mapper = mapper

	@overrides(VolumeProperty)
	def GetParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this 
		volume property can be adjusted. 
		:rtype: QWidget
		"""
		self.simpleSlider = QSlider(Qt.Horizontal)
		self.simpleSlider.setMinimum(int(self.minimum))
		self.simpleSlider.setMaximum(int(self.maximum))
		self.simpleSlider.setValue(int(self.lowerBound))
		self.simpleSlider.valueChanged.connect(self.valueChanged)

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.simpleSlider)

		widget = QWidget()
		widget.setLayout(layout)

		return widget

	@overrides(VolumeProperty)
	def SetImageData(self, imageData):
		self.imageData = imageData

		if self.imageData is None:
			self.minimum = 0.0
			self.maximum = 1.0
			self.lowerBound = self.minimum
			return

		self.minimum, self.maximum = self.imageData.GetScalarRange()
		self.lowerBound = self.minimum

	@overrides(VolumeProperty)
	def UpdateTransferFunction(self):

		if self.mapper.GetBlendMode() != vtkVolumeMapper.COMPOSITE_BLEND:
			self.mapper.SetBlendModeToComposite()

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

		self.updatedTransferFunction.emit()

	@overrides(VolumeProperty)
	def valueChanged(self, value):
		"""
		This method is called when the value of one of the sliders / fields is 
		adjusted. Argument value is unused. It is just there so that it can be 
		connected to the signals of the interface elements.

		:type value: int
		"""
		self.lowerBound = self.simpleSlider.value()
		self.UpdateTransferFunction()
