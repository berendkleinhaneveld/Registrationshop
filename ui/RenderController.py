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
from ui.visualizations import VisualizationTypeSimple
from ui.visualizations import VisualizationTypeMIP
from ui.visualizations import VolumeVisualizationFactory
from ui.visualizations import VolumeVisualizationWrapper
from core.vtkObjectWrapper import vtkCameraWrapper
from core.data import DataReader


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
	# RenderParameterWidget(Slices) should connect
	slicesChanged = Signal(object)
	# Emitted when the clipping box is loaded by the project controller.
	# RenderParameterWidget(Slices) should connect
	clippingBoxChanged = Signal(bool)
	# Emitted when clipping planes are loaded by the project controller.
	# RenderParameterWidget(Slices) should connect
	clippingPlanesChanged = Signal(bool)

	def __init__(self, renderWidget, tag):
		"""
		Set the renderWidget for direct control instead of Signal/Slot messages.
		:type renderWidget: RenderWidget
		"""
		super(RenderController, self).__init__()

		self.renderWidget = renderWidget
		self.visualizationTypes = [VisualizationTypeSimple, VisualizationTypeMIP]
		self.visualizationType = None
		self.imageData = None
		self.visualization = None
		self.visualizations = dict()  # Keep track of used volume properties
		self.slices = [False, False, False]
		self.clippingBox = False
		self.clippingPlanes = True
		self.tag = tag

	@Slot(basestring)
	def setFile(self, fileName):
		"""
		:type fileName: str
		"""
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
		self.imageData = dataReader.GetImageData(fileName)

		# Give the image data to the widget
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
			self.clippingBox = renderSettings["clippingBox"]
			self.clippingPlanes = renderSettings["clippingPlanes"]

			cameraWrapped = renderSettings["camera"]
			cameraWrapped.applyToObject(self.renderWidget.renderer.GetActiveCamera())
		else:
			self.visualizations = dict()
			self.visualizationType = None
			self.slices = [False, False, False]
			self.clippingBox = False
			self.clippingPlanes = True

		self.setVisualizationType(self.visualizationType)
		self.renderWidget.setSlices(self.slices)
		self.renderWidget.setVolumeVisualization(self.visualization)
		self.renderWidget.showClippingBox(self.clippingBox)
		self.renderWidget.showClippingPlanes(self.clippingPlanes)

		self.visualizationChanged.emit(self.visualization)
		self.slicesChanged.emit(self.slices)
		self.clippingBoxChanged.emit(self.clippingBox)
		self.clippingPlanesChanged.emit(self.clippingPlanes)

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
		settings["clippingBox"] = self.clippingBox
		settings["clippingPlanes"] = self.clippingPlanes

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
			if self.visualizationType == VisualizationTypeSimple:
				if self.tag == "fixed":
					self.visualization.color = self.visualization.colors[0]
				elif self.tag == "moving":
					self.visualization.color = self.visualization.colors[1]
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

	def showClippingBox(self, visibility):
		"""
		:type visibility: bool
		"""
		self.clippingBox = visibility
		self.renderWidget.showClippingBox(self.clippingBox)

	def showClippingPlanes(self, visibility):
		"""
		:type visibility: bool
		"""
		self.clippingPlanes = visibility
		self.renderWidget.showClippingPlanes(self.clippingPlanes)

	def updateVisualization(self):
		"""
		Should be called by all interface elements that adjust the
		volume property. This makes sure that the render widget takes
		notice and renders accordingly.
		"""
		self.renderWidget.setVolumeVisualization(self.visualization)
		self.visualizationUpdated.emit(self.visualization)

	def resetClippingBox(self):
		self.renderWidget.resetClippingBox()

	def resetVisualizations(self):
		# Clear out the old render types
		self.visualizations = dict()
		self.setVisualizationType(None)
