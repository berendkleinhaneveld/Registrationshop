"""
MultiRenderController

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtCore import QObject
from PySide.QtCore import Slot
from PySide.QtCore import Signal
from PySide.QtGui import QWidget
from core.vtkObjectWrapper import vtkCameraWrapper
from core.data import DataReader
from core.data import DataResizer
from ui.visualizations import MultiVisualizationTypeMIDA
from ui.visualizations import MultiVisualizationTypeMIP
from ui.visualizations import MultiVisualizationTypeMix
from ui.visualizations import MultiVolumeVisualizationFactory


class MultiRenderController(QObject):
	"""
	MultiRenderController
	"""

	fixedDataChanged = Signal(object)
	movingDataChanged = Signal(object)
	visualizationChanged = Signal(object)
	visualizationUpdated = Signal(object)
	slicesChanged = Signal(object)
	slicesUpdated = Signal(object)

	maxVoxelSize = 9000000

	def __init__(self, mulitRenderWidget):
		super(MultiRenderController, self).__init__()

		self.multiRenderWidget = mulitRenderWidget
		self.visualizationTypes = [MultiVisualizationTypeMix, MultiVisualizationTypeMIP, MultiVisualizationTypeMIDA]
		self.visualizationType = None  # str
		self.fixedImageData = None  # vtkImageData
		self.movingImageData = None  # vtkImageData
		self.fixedVisualization = None  # VolumeVisualization
		self.movingVisualization = None  # VolumeVisualization
		self.visualization = None  # MultiVolumeVisualization
		self.visualizations = dict()  # Dict of MultiVolumeVisualizations, visType as keys
		self.slices = [False, False, False]

	@Slot(basestring)
	def setFixedFile(self, fileName):
		"""
		:type fileName: str
		"""
		if fileName is None:
			self.fixedImageData = None
			self.fixedVisualization = None
			self.visualization = None
			self.visualizations = dict()
			self.visualizationType = None
			self.multiRenderWidget.setFixedData(self.fixedImageData)
			self.multiRenderWidget.setVolumeVisualization(self.fixedVisualization)
			self.fixedDataChanged.emit(self.fixedImageData)
			self.visualizationChanged.emit(self.visualization)
			return

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		imageResizer = DataResizer()
		self.fixedImageData = imageResizer.ResizeData(imageData, maximum=self.maxVoxelSize)
		self.multiRenderWidget.setFixedData(self.fixedImageData)
		self.fixedDataChanged.emit(self.fixedImageData)

		# Set the visualization type
		self.setVisualizationType(self.visualizationType)

	@Slot(basestring)
	def setMovingFile(self, fileName):
		if fileName is None:
			self.movingImageData = None
			self.movingVisualization = None
			self.multiRenderWidget.setMovingData(self.movingImageData)
			self.multiRenderWidget.setVolumeVisualization(self.visualization)
			self.movingDataChanged.emit(self.movingImageData)
			self.visualizationChanged.emit(self.movingVisualization)
			return

		# Read image data
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)

		# Resize the image data
		imageResizer = DataResizer()
		self.movingImageData = imageResizer.ResizeData(imageData, maximum=self.maxVoxelSize)
		self.multiRenderWidget.setMovingData(self.movingImageData)
		self.movingDataChanged.emit(self.movingImageData)

		# Set the visualization type
		self.setVisualizationType(self.visualizationType)

	@Slot(object)
	def setRenderSettings(self, renderSettings):
		if renderSettings is not None:
			self.slices = renderSettings["slices"]
			self.multiRenderWidget.setSlices(self.slices)
			cameraWrapper = renderSettings["camera"]
			cameraWrapper.applyToObject(self.multiRenderWidget.renderer.GetActiveCamera())
			self.updateVisualization()
			self.slicesChanged.emit(self.slices)
		else:
			self.slices = [False, False, False]

	def getRenderSettings(self):
		settings = dict()
		settings["slices"] = self.slices
		camera = self.multiRenderWidget.renderer.GetActiveCamera()
		settings["camera"] = vtkCameraWrapper(camera)
		return settings

	def setVisualizationType(self, visualizationType):
		"""
		Swithes the renderer to the given render type. Previously used render
		types are saved so that switching back to a previously used render type
		will produce the same visualization as before.

		:type shaderType: str
		"""
		self.visualizationType = visualizationType
		if self.visualizationType is None or \
			visualizationType not in self.visualizationTypes:
			self.visualizationType = MultiVisualizationTypeMix

		if self.fixedImageData is None and self.movingImageData is None:
			return

		if self.visualizationType in self.visualizations:
			self.visualization = self.visualizations[self.visualizationType]
			self.visualization.updateTransferFunctions()
		else:
			self.visualization = MultiVolumeVisualizationFactory.CreateProperty(self.visualizationType)
			self.visualization.setImageData(self.fixedImageData, self.movingImageData)
			self.visualization.updateTransferFunctions()
			self.visualizations[self.visualizationType] = self.visualization

		self.multiRenderWidget.setVolumeVisualization(self.visualization)
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
		self.multiRenderWidget.setSlices(self.slices)
		self.slicesUpdated.emit(self.slices)

	def updateVisualization(self):
		"""
		Should be called by all interface elements that adjust the
		volume property. This makes sure that the render widget takes
		notice and renders accordingly.
		"""
		if self.visualization:
			if self.fixedVisualization:
				self.visualization.setFixedVisualization(self.fixedVisualization)
			if self.movingVisualization:
				self.visualization.setMovingVisualization(self.movingVisualization)
		self.multiRenderWidget.setVolumeVisualization(self.visualization)
		self.visualizationUpdated.emit(self.visualization)

	@Slot(object)
	def setFixedVisualization(self, visualization):
		"""
		"""
		self.fixedVisualization = visualization
		self.updateVisualization()

	@Slot(object)
	def setMovingVisualization(self, visualization):
		"""
		"""
		self.movingVisualization = visualization
		self.updateVisualization()
