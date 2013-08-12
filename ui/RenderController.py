"""
RenderController

Class that controls the volume property and settings
for the render widget.
The render parameter widget gets its parameters from
the controller and when a parameter is changed it will
pass the change over to the controller which will then 
apply it. The controller will then notify the render 
widget that it should update.

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtCore import QObject
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from PySide.QtGui import QWidget
from VolumeProperty import RenderTypeCT
from VolumeProperty import RenderTypeSimple
from VolumeProperty import RenderTypeMIP
from VolumeProperty import VolumeProperty
from VolumeProperty import VolumePropertyFactory
from VolumeProperty import VolumePropertyObjectWrapper
from core.data.DataReader import DataReader
from core.data.DataResizer import DataResizer

class RenderController(QObject):
	"""
	RenderController
	"""
	# Emitted when data is loaded by the project controller.
	# RenderWidget should connect
	dataChanged = Signal(object)
	# Emitted when the volume property is loaded by the project controller.
	# RenderWidget, RenderParameterWidget(Vis) should connect
	volumePropertyChanged = Signal(object)
	# Emitted when the slices are loaded by the project controller.
	# RenderWidget, RenderParameterWidget(Slices) should connect
	slicesChanged = Signal(object)
	
	# Emitted when the volume property gets updated by the parameter widgets.
	# RenderWidget should connect
	volumePropertyUpdated = Signal(object)
	# Emitted when the visibility of the slices is changed by the slice parameter widget.
	# RenderWidget should connect
	slicesUpdated = Signal(object)

	def __init__(self, renderWidget):
		"""
		Set the renderWidget for direct control instead of Signal/Slot messages.
		:type renderWidget: RenderWidget
		"""
		super(RenderController, self).__init__()

		self.renderWidget = renderWidget
		self.renderTypes = [RenderTypeSimple, RenderTypeCT, RenderTypeMIP]
		self.renderType = None
		self.imageData = None
		self.volumeProperty = None
		self.volumeProperties = [] # Keep track of used volume properties
		self.slices = [False, False, False]
		
	@Slot(basestring)
	def setFile(self, fileName):
		"""
		:type fileName: str
		"""
		# Clear out the old render types
		self.volumeProperties = []

		if fileName is None:
			self.imageData = None
			self.volumeProperty = None
			self.renderWidget.setData(self.imageData)
			self.renderWidget.setVolumeProperty(self.volumeProperty)
			self.dataChanged.emit(self.imageData)
			self.volumePropertyChanged.emit(self.volumeProperty)
			return

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		imageResizer = DataResizer()
		self.imageData = imageResizer.ResizeData(imageData, maximum=18000000)
		self.renderWidget.setData(self.imageData)
		self.dataChanged.emit(self.imageData)

		# Set the render type
		self.setRenderType(self.renderType)

	@Slot(object)
	def setRenderSettings(self, renderSettings):
		"""
		Apply the settings from the provided RenderSettings object.
		"""
		if renderSettings is not None:
			properties = renderSettings.getProperties()
			self.volumeProperties = properties[0]
			self.renderType = properties[1]
			self.slices = properties[2]
		else:
			self.volumeProperties = []
			self.renderType = None
			self.slices = [False, False, False]
			
		self.setRenderType(self.renderType)
		self.renderWidget.setSlices(self.slices)
		self.renderWidget.setVolumeProperty(self.volumeProperty)
		self.slicesChanged.emit(self.slices)
		self.volumePropertyChanged.emit(self.volumeProperty)

	def getRenderSettings(self):
		"""
		Return a RenderSettings object with all the right properties set.
		:rtype: RenderSettings
		"""
		renderSettings = RenderSettings()
		renderSettings.setProperties(self.volumeProperties, self.renderType, self.slices)
		return renderSettings

	def setRenderType(self, renderType):
		"""
		Swithes the renderer to the given render type. Previously used render 
		types are saved so that switching back to a previously used render type 
		will produce the same visualization as before.

		:type renderType: str
		"""
		self.renderType = renderType
		if self.renderType is None:
			self.renderType = RenderTypeSimple

		if self.imageData is None:
			return

		foundPreviouslyUsedProperty = False
		for volProp in self.volumeProperties:
			if volProp.renderType == self.renderType:
				self.volumeProperty = volProp
				self.volumeProperty.updateTransferFunction()
				foundPreviouslyUsedProperty = True
				break

		if not foundPreviouslyUsedProperty:
			self.volumeProperty = VolumePropertyFactory.CreateProperty(self.renderType)
			self.volumeProperty.setImageData(self.imageData)
			self.volumeProperty.updateTransferFunction()
			self.volumeProperties.append(self.volumeProperty)

		self.renderWidget.setVolumeProperty(self.volumeProperty)
		self.volumePropertyChanged.emit(self.volumeProperty)

	def getParameterWidget(self):
		"""
		:rtype: QWidget
		"""
		if self.volumeProperty is not None:
			return self.volumeProperty.getParameterWidget()

		return QWidget()

	def setSliceVisibility(self, sliceIndex, visibility):
		"""
		:type sliceIndex: int
		:type visibility: bool
		"""
		self.slices[sliceIndex] = visibility
		self.renderWidget.setSlices(self.slices)
		self.slicesUpdated.emit(self.slices)
	
	def updateVolumeProperty(self):
		"""
		Should be called by all interface elements that adjust the 
		volume property. This makes sure that the render widget takes
		notice and renders accordingly.
		"""
		self.renderWidget.setVolumeProperty(self.volumeProperty)
		self.volumePropertyUpdated.emit(self.volumeProperty)



class RenderSettings(object):
	"""
	RenderSettings is an object that stores information about the render 
	settings of a render widget.

	Already supports:
	* volumeProperty
	* renderType
	* slice visibility

	TODO:
	* slice location
	* camera location / orientation
	"""
	def __init__(self):
		super(RenderSettings, self).__init__()

		# All the render properties for different types
		self.volumeProperties = None
		# Current render type
		self.renderType = None
		# Visibility of the slices
		self.slices = None

	def setProperties(self, volumeProperties, renderType, slices):
		"""
		Creates an array of the given volume properties with 
		wrapped properties. So pure python objects instead of 
		vtk objects.
		:type volumeProperties: [] with VolumeProperty objects
		"""
		self.volumeProperties = []
		for index in range(len(volumeProperties)):
			volProp = VolumePropertyObjectWrapper(volumeProperties[index])
			self.volumeProperties.append(volProp)

		self.renderType = renderType
		self.slices = slices

	def getProperties(self):
		"""
		:rtype: [], str
		"""
		volumeProperties = []

		for index in range(len(self.volumeProperties)):
			volProp = self.volumeProperties[index].getVolumeProperty()
			volumeProperties.append(volProp)
			
		return volumeProperties, self.renderType, self.slices

