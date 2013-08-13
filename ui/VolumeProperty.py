"""
VolumeProperty

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from vtk import vtkVolumeMapper
from vtk import vtkMath
from PySide.QtGui import QWidget
from PySide.QtGui import QSlider
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Qt
from PySide.QtCore import Signal
from PySide.QtCore import QObject
from core.decorators import overrides
from core.vtkObjectWrapper import vtkPiecewiseFunctionWrapper
from core.vtkObjectWrapper import vtkColorTransferFunctionWrapper
from core.vtkObjectWrapper import vtkVolumePropertyWrapper
import math
import yaml

# Define Render Types
RenderTypeSimple = "Simple"
RenderTypeGray = "Gray scale"
RenderTypeCT = "CT"
RenderTypeMIP = "MIP"

VolumePropKey = "VolumeProperty"
RenderTypeKey = "RenderTypeKey"
ColorFuncKey = "ColorFuncKey"
TransFuncKey = "TransFuncKey"

# Factory

class VolumePropertyFactory(object):
	"""
	VolumePropertyFactory makes and creates proper VolumeProperty objects.
	"""
	
	@classmethod
	def CreateProperty(cls, renderType):
		if renderType == RenderTypeSimple:
			return SimpleVolumeProperty()
		elif renderType == RenderTypeCT:
			return CTVolumeProperty()
		elif renderType == RenderTypeMIP:
			return MIPVolumeProperty()
		else:
			assert False

# Volume properties

class VolumeProperty(QObject):
	"""
	VolumeProperty is an interface class for the different render types
	"""

	updatedTransferFunction = Signal()

	def __init__(self):
		super(VolumeProperty, self).__init__()

		self.volumeProperty = None
		self.renderType = None

	def getParameterWidget(self):
		"""
		This method should be overridden in the subclasses.
		:rtype: QWidget
		"""
		raise NotImplementedError()

	def setImageData(self, imageData):
		"""
		This method should be overridden in the subclasses.
		:type imageData: vtkImageData
		"""
		raise NotImplementedError()

	def configureMapper(self, mapper):
		raise NotImplementedError()

	def updateTransferFunction(self):
		raise NotImplementedError()

	def valueChanged(self, value):
		raise NotImplementedError()

class CTVolumeProperty(VolumeProperty):
	"""
	VolumeProperty subclass for CT visualization
	"""
	def __init__(self):
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

	@overrides(VolumeProperty)
	def configureMapper(self, mapper):
		if mapper is not None and mapper.GetBlendMode() != vtkVolumeMapper.COMPOSITE_BLEND:
			mapper.SetBlendModeToComposite()

	@overrides(VolumeProperty)
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

		self.volumeProperty.SetColor(self.colorFunction)
		self.volumeProperty.SetScalarOpacity(self.opacityFunction)

		self.updatedTransferFunction.emit()

	@overrides(VolumeProperty)
	def setImageData(self, imageData):
		"""
		Nothing needs to be done for CT scans. The values of the sliders are
		not dependent on the imageData.
		:type imageData: vtkImageData
		"""
		pass
		
	@overrides(VolumeProperty)
	def getParameterWidget(self):
		"""
		Returns a widget with sliders / fields with which properties of this 
		volume property can be adjusted. 
		:rtype: QWidget
		"""
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)

		self.sliders = []
		for index in range(7):
			slider = QSlider(Qt.Horizontal)
			slider.setMinimum(0)
			slider.setMaximum(1000)
			slider.setValue(int(math.pow(self.sectionsOpacity[index], 1.0/3.0) * slider.maximum()))
			slider.valueChanged.connect(self.valueChanged)
			self.sliders.append(slider)
			layout.addWidget(QLabel(self.sectionNames[index]), index, 0)
			layout.addWidget(slider, index, 1)

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(VolumeProperty)
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

class MIPVolumeProperty(VolumeProperty):
	"""
	VolumeProperty subclass for MIP visualization.
	"""
	def __init__(self):
		super(MIPVolumeProperty, self).__init__()

		self.renderType = RenderTypeMIP

		# TODO: add two sliders with which to threshold the data
		# Create property and attach the transfer function
		self.volumeProperty = vtkVolumeProperty()
		self.volumeProperty.SetIndependentComponents(True);
		self.volumeProperty.SetInterpolationTypeToLinear();

	@overrides(VolumeProperty)
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

	@overrides(VolumeProperty)
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

	@overrides(VolumeProperty)
	def configureMapper(self, mapper):
		if mapper is not None and mapper.GetBlendMode() != vtkVolumeMapper.MAXIMUM_INTENSITY_BLEND:
			mapper.SetBlendModeToMaximumIntensity()

	@overrides(VolumeProperty)
	def updateTransferFunction(self):
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
		self.updateTransferFunction()

class SimpleVolumeProperty(VolumeProperty):
	"""
	VolumeProperty subclass for a simple visualization.
	"""
	def __init__(self):
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

		self.minimum = 0
		self.maximum = 1
		self.lowerBound = 0
		self.upperBound = 1
		self.hue = 0 # 0-360

	@overrides(VolumeProperty)
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

		self.hueSlider = QSlider(Qt.Horizontal)
		self.hueSlider.setMinimum(0)
		self.hueSlider.setMaximum(360)
		self.hueSlider.setValue(self.hue)
		self.hueSlider.valueChanged.connect(self.valueChanged)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Lower boundary"), 0, 0)
		layout.addWidget(self.lowerBoundSlider, 0, 1)
		layout.addWidget(QLabel("Upper boundary"), 1, 0)
		layout.addWidget(self.upperBoundSlider, 1, 1)
		layout.addWidget(QLabel("Hue"), 2, 0)
		layout.addWidget(self.hueSlider, 2, 1)

		widget = QWidget()
		widget.setLayout(layout)

		return widget

	@overrides(VolumeProperty)
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

	@overrides(VolumeProperty)
	def configureMapper(self, mapper):
		if mapper is not None and mapper.GetBlendMode() != vtkVolumeMapper.COMPOSITE_BLEND:
			mapper.SetBlendModeToComposite()

	@overrides(VolumeProperty)
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
		self.lowerBound = min(self.lowerBoundSlider.value(), self.upperBoundSlider.value())
		self.upperBound = max(self.lowerBoundSlider.value(), self.upperBoundSlider.value())
		self.hue = self.hueSlider.value()
		self.updateTransferFunction()


# Property wrappers

class VolumePropertyObjectWrapper(object):
	"""
	VolumePropertyObjectWrapper wraps around a volume property. It wraps
	all the vtk attributes in their own wrappers.
	"""
	standardAttributes = ["renderType", "sectionsOpacity", "lowerBound", "upperBound", "minimum", "maximum", "hue"]

	def __init__(self, volumeProperty=None):
		super(VolumePropertyObjectWrapper, self).__init__()

		if volumeProperty is not None:
			self.setVolumeProperty(volumeProperty)
		
	def setVolumeProperty(self, volumeProperty):
		for attribute in VolumePropertyObjectWrapper.standardAttributes:
			if hasattr(volumeProperty, attribute) and getattr(volumeProperty, attribute) is not None:
				setattr(self, attribute, getattr(volumeProperty, attribute))

		if hasattr(volumeProperty, "volumeProperty"):
			self.volumeProperty = vtkVolumePropertyWrapper(volumeProperty.volumeProperty)
		if hasattr(volumeProperty, "opacityFunction"):
			self.opacityFunction = vtkPiecewiseFunctionWrapper(volumeProperty.opacityFunction)
		if hasattr(volumeProperty, "colorFunction"):
			self.colorFunction = vtkColorTransferFunctionWrapper(volumeProperty.colorFunction)

	def getVolumeProperty(self):
		volProp = VolumePropertyFactory.CreateProperty(self.renderType)

		for attribute in VolumePropertyObjectWrapper.standardAttributes:
			if hasattr(self, attribute) and getattr(self, attribute) is not None:
				setattr(volProp, attribute, getattr(self, attribute))
				# print attribute + ": " + str(getattr(self, attribute))

		if hasattr(self, "volumeProperty") and self.volumeProperty is not None:
			volProp.volumeProperty = self.volumeProperty.originalObject()
		if hasattr(self, "opacityFunction") and self.opacityFunction is not None:
			volProp.opacityFunction = self.opacityFunction.originalObject()
		if hasattr(self, "colorFunction") and self.colorFunction is not None:
			volProp.colorFunction = self.colorFunction.originalObject()

		return volProp

