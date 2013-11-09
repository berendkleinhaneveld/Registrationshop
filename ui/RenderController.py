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
from ui.visualizations import VisualizationTypeCT
from ui.visualizations import VisualizationTypeSimple
from ui.visualizations import VisualizationTypeMIP
from ui.visualizations import VisualizationTypeMIDA
from ui.visualizations import VisualizationTypeTransferFunction
from ui.visualizations import VolumeVisualizationFactory
from ui.visualizations import VolumeVisualizationWrapper
from core.vtkObjectWrapper import vtkCameraWrapper
from core.data import DataReader
from core.data import DataResizer


class RenderController(QObject):
	"""
	RenderController
	"""
	# Emitted when data is loaded by the project controller.
	# RenderWidget should connect
	dataChanged = Signal(object)
	# Emitted when the volume property is loaded by the project controller.
	# RenderWidget, RenderParameterWidget(Vis) should connect
	visualizationChanged = Signal(object)
	# Emitted when the volume property gets updated by the parameter widgets.
	# RenderWidget should connect
	visualizationUpdated = Signal(object)
	# Emitted when the slices are loaded by the project controller.
	# RenderWidget, RenderParameterWidget(Slices) should connect
	slicesChanged = Signal(object)
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
		self.visualizationTypes = [VisualizationTypeSimple, VisualizationTypeCT, VisualizationTypeTransferFunction, VisualizationTypeMIP, VisualizationTypeMIDA]
		self.visualizationType = None
		self.imageData = None
		self.visualization = None
		self.visualizations = dict()  # Keep track of used volume properties
		self.slices = [False, False, False]

	@Slot(basestring)
	def setFile(self, fileName):
		"""
		:type fileName: str
		"""
		# Clear out the old render types
		self.visualizations = dict()

		if fileName is None:
			self.imageData = None
			self.visualization = None
			self.renderWidget.setData(self.imageData)
			self.renderWidget.setVolumeVisualization(self.visualization)
			self.dataChanged.emit(self.imageData)
			self.visualizationChanged.emit(self.visualization)
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
		self.setVisualizationType(self.visualizationType)

	@Slot(object)
	def setRenderSettings(self, renderSettings):
		"""
		Apply the settings from the provided RenderSettings object.
		"""
		if renderSettings is not None:
			self.visualizations = dict()
			visualizations = renderSettings["visualizations"]
			for key in visualizations:
				self.visualizations[key] = visualizations[key].getVolumeVisualization()
			self.visualizationType = renderSettings["visualizationType"]
			self.slices = renderSettings["slices"]
			cameraWrapped = renderSettings["camera"]
			cameraWrapped.applyToObject(self.renderWidget.renderer.GetActiveCamera())
		else:
			self.visualizations = dict()
			self.visualizationType = None
			self.slices = [False, False, False]

		self.setVisualizationType(self.visualizationType)
		self.renderWidget.setSlices(self.slices)
		self.renderWidget.setVolumeVisualization(self.visualization)

		self.visualizationChanged.emit(self.visualization)
		self.slicesChanged.emit(self.slices)

	def getRenderSettings(self):
		"""
		Return a RenderSettings object with all the right properties set.
		:rtype: RenderSettings
		"""
		visualizations = dict()
		for key in self.visualizations:
			volProp = VolumeVisualizationWrapper(self.visualizations[key])
			visualizations[key] = volProp

		settings = dict()
		settings["visualizations"] = visualizations
		settings["visualizationType"] = self.visualizationType
		settings["slices"] = self.slices

		camera = self.renderWidget.renderer.GetActiveCamera()
		settings["camera"] = vtkCameraWrapper(camera)

		return settings

	def setVisualizationType(self, visualizationType):
		"""
		Swithes the renderer to the given render type. Previously used render
		types are saved so that switching back to a previously used render type
		will produce the same visualization as before.

		:type visualizationType: str
		"""
		self.visualizationType = visualizationType
		if self.visualizationType is None:
			self.visualizationType = VisualizationTypeSimple

		if self.imageData is None:
			return

		if self.visualizationType in self.visualizations:
			self.visualization = self.visualizations[self.visualizationType]
			self.visualization.updateTransferFunction()
		else:
			self.visualization = VolumeVisualizationFactory.CreateProperty(self.visualizationType)
			self.visualization.setImageData(self.imageData)
			self.visualization.updateTransferFunction()
			self.visualizations[self.visualizationType] = self.visualization

		self.renderWidget.setVolumeVisualization(self.visualization)
		self.visualizationChanged.emit(self.visualization)

	def getParameterWidget(self):
		"""
		:rtype: QWidget
		"""
		if self.visualization is not None:
			return self.visualization.getParameterWidget()

		return QWidget()

	def setSliceVisibility(self, sliceIndex, visibility):
		"""
		:type sliceIndex: int
		:type visibility: bool
		"""
		self.slices[sliceIndex] = visibility
		self.renderWidget.setSlices(self.slices)
		self.slicesUpdated.emit(self.slices)

	def updateVisualization(self):
		"""
		Should be called by all interface elements that adjust the
		volume property. This makes sure that the render widget takes
		notice and renders accordingly.
		"""
		self.renderWidget.setVolumeVisualization(self.visualization)
		self.visualizationUpdated.emit(self.visualization)
