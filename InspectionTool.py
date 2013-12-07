"""
CompareWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QApplication
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtCore import QObject
from PySide.QtCore import Slot
from core.data.DataReader import DataReader
from core.data.DataTransformer import DataTransformer
from core.data.DataResizer import DataResizer
from ui.widgets.SliceViewerWidget import SliceViewerWidget
from ui.widgets.SliceCompareViewerWidget import SliceCompareViewerWidget
from vtk import vtkExtractVOI
from vtk import vtkImageMathematics
from vtk import vtkTransform


class CompareWidget(QWidget):
	"""
	CompareWidget is a widget that shows multiple slice windows.
	"""
	def __init__(self, widgets):
		super(CompareWidget, self).__init__()

		layout = QGridLayout()
		# layout.setSpacing(0)
		# layout.setContentsMargins(0, 0, 0, 0)
		for i in range(len(widgets)):
			widget = widgets[i]
			layout.addWidget(widget, 0, i)

		self.setLayout(layout)


class ComparisonController(QObject):
	"""
	ComparisonController is the controller for the three comparison
	widgets. The widgets themselves can be managed by any other class.
	"""
	def __init__(self):
		super(ComparisonController, self).__init__()

		blue = [0, 127, 255]
		orange = [255, 127, 0]
		blue = map(lambda x: x / 255.0, blue)
		orange = map(lambda x: x / 255.0, orange)
		self.fixedImageWidget = SliceViewerWidget()
		self.fixedImageWidget.color = blue
		self.movingImageWidget = SliceViewerWidget()
		self.movingImageWidget.color = orange
		self.diffImageWidget = SliceCompareViewerWidget()

		self.widgets = [self.fixedImageWidget, self.diffImageWidget, self.movingImageWidget]

		for widget in self.widgets:
			widget.slicePositionChanged.connect(self.slicerChanged)
			widget.mouseMoved.connect(self.mouseMoved)

	def syncCameras(self, viewUp=None):
		# Copy the camera settings
		sourceCam = self.fixedImageWidget.renderer.GetActiveCamera()
		if viewUp:
			sourceCam.SetViewUp(viewUp)
		self.copyCam(sourceCam, self.movingImageWidget.renderer.GetActiveCamera())
		self.copyCam(sourceCam, self.diffImageWidget.renderer.GetActiveCamera())

	def setInputData(self, fixedDataName, movingDataName, transform=None):
		"""
		Input exists out of filenames for fixed and moving dataset and
		an optional transform for the moving dataset.
		"""
		self.transform = transform
		if not self.transform:
			self.transform = vtkTransform()

		fixedDataReader = DataReader()
		fixImData = fixedDataReader.GetImageData(fixedDataName)

		dataResizer = DataResizer()
		fixedImageData = dataResizer.ResizeData(fixImData, maximum=5000000)

		movingDataReader = DataReader()
		movImData = movingDataReader.GetImageData(movingDataName)

		movDataResizer = DataResizer()
		movingImageData = movDataResizer.ResizeData(movImData, maximum=5000000)

		transformer = DataTransformer()
		transformedData = transformer.TransformImageData(movingImageData, self.transform, fixedImageData)

		# Calculate overlapping subextents from the fixed and moving data
		# fixedBounds = fixedImageData.GetBounds()
		fixedDimensions = fixedImageData.GetDimensions()
		# fixedWorldSize = [fixedBounds[1] - fixedBounds[0], fixedBounds[3] - fixedBounds[2], fixedBounds[5] - fixedBounds[4]]
		# movingBounds = transformedData.GetBounds()

		# subBounds = [0.0 for _ in range(6)]
		# subBounds[0] = max(fixedBounds[0], movingBounds[0])
		# subBounds[2] = max(fixedBounds[2], movingBounds[2])
		# subBounds[4] = max(fixedBounds[4], movingBounds[4])
		# subBounds[1] = min(fixedBounds[1], movingBounds[1])
		# subBounds[3] = min(fixedBounds[3], movingBounds[3])
		# subBounds[5] = min(fixedBounds[5], movingBounds[5])

		# fixedSubExtents = [0 for _ in range(6)]
		# fixedSubExtents[0] = int((fixedDimensions[0]-1) * ((bsubBounds[0] - fixedBounds[0]) / fixedWorldSize[0]))
		# fixedSubExtents[1] = int((fixedDimensions[0]-1) * ((subBounds[1] - fixedBounds[0]) / fixedWorldSize[0]))
		# fixedSubExtents[2] = int((fixedDimensions[1]-1) * ((subBounds[2] - fixedBounds[2]) / fixedWorldSize[1]))
		# fixedSubExtents[3] = int((fixedDimensions[1]-1) * ((subBounds[3] - fixedBounds[2]) / fixedWorldSize[1]))
		# fixedSubExtents[4] = int((fixedDimensions[2]-1) * ((subBounds[4] - fixedBounds[4]) / fixedWorldSize[2]))
		# fixedSubExtents[5] = int((fixedDimensions[2]-1) * ((subBounds[5] - fixedBounds[4]) / fixedWorldSize[2]))

		# TODO: quit if there is no overlap
		# fixedExtracter = vtkExtractVOI()
		# fixedExtracter.SetInputData(fixedImageData)
		# fixedExtracter.SetVOI(fixedSubExtents)
		# fixedExtracter.Update()

		# fixedSubVolume = fixedExtracter.GetOutput()

		# math = vtkImageMathematics()
		# math.SetOperationToSubtract()
		# math.SetInput1Data(fixedSubVolume)
		# math.SetInput2Data(transformedData)
		# math.Update()

		# diffImageData = math.GetOutput()

		self.fixedImageWidget.setImageData(fixedImageData)
		self.movingImageWidget.setImageData(transformedData)
		self.diffImageWidget.setFixedImageData(fixedImageData)
		self.diffImageWidget.setSlicerWidget(self.fixedImageWidget, self.movingImageWidget)

		if fixedDimensions[0] > fixedDimensions[1]:
			self.syncCameras((-1, 0, 0))
		else:
			self.syncCameras()

		self.fixedImageWidget.slicer.AddObserver("WindowLevelEvent", self.slicerModified)
		self.movingImageWidget.slicer.AddObserver("WindowLevelEvent", self.slicerModified)

	def slicerModified(self, obj, ev):
		window = obj.GetWindow()
		level = obj.GetLevel()
		for widget in self.widgets:
			if widget is not obj and widget is not self.diffImageWidget:
				target = widget.slicer
				target.SetWindowLevel(window, level)

		self.diffImageWidget.updateCompareView()
		self.diffImageWidget.render()

	def copyCam(self, source, target, transform=None):
		"""
		Copies some properties from the source camera to the target
		camera: Position, FocalPoint and ParallelScale.
		"""
		target.SetViewUp(source.GetViewUp())
		target.SetPosition(source.GetPosition())
		target.SetFocalPoint(source.GetFocalPoint())
		target.SetParallelScale(source.GetParallelScale())
		target.SetClippingRange(source.GetClippingRange())

	@Slot(object)
	def mouseMoved(self, position):
		for widget in self.widgets:
			widget.setLocatorPosition(position)

		for widget in self.widgets:
			widget.render()

	@Slot(object)
	def slicerChanged(self, slicerWidget):
		"""
		slicerWidget should be the widget in which is scrolled.
		"""
		source = slicerWidget  # vtkImagePlaneWidget
		targets = filter(lambda x: x != source, self.widgets)

		sourceSlicer = source.slicer
		for widget in targets:
			if not widget.slicer:
				continue
			targetSlicer = widget.slicer
			orig = targetSlicer.GetOrigin()
			point1 = targetSlicer.GetPoint1()
			point2 = targetSlicer.GetPoint2()
			targetSlicer.SetOrigin(orig[0], orig[1], sourceSlicer.GetOrigin()[2])
			targetSlicer.SetPoint1(point1[0], point1[1], sourceSlicer.GetPoint1()[2])
			targetSlicer.SetPoint2(point2[0], point2[1], sourceSlicer.GetPoint2()[2])

		self.fixedImageWidget.render()
		self.movingImageWidget.render()
		self.diffImageWidget.updateCompareView()
		self.diffImageWidget.render()


if __name__ == '__main__':
	app = QApplication([])

	# fixedDataName = "/Users/beer/Desktop/Datasets/Block1.mhd"
	# movingDataName = "/Users/beer/Desktop/Datasets/Block2.mhd"
	fixedDataName = "/Users/beer/Downloads/Datasets/LUMC_Kahler_scaled/Patient_1_(t1).mha"
	movingDataName = "/Users/beer/Downloads/Datasets/LUMC_Kahler_scaled/Patient_1_(t2).mha"

	# fixedDataName = "/Users/beer/Documents/Development/elastix/src/Testing/Data/3DCT_lung_baseline.mha"
	# movingDataName = "/Users/beer/Documents/Development/elastix/src/Testing/Data/3DCT_lung_followup.mha"
	# fixedDataName = "/Users/beer/Documents/Development/elastix/src/Testing/Data/3DCT_lung_baseline_mask.mha"
	# movingDataName = "/Users/beer/Documents/Development/elastix/src/Testing/Data/3DCT_lung_followup_mask.mha"
	
	controller = ComparisonController()
	controller.setInputData(fixedDataName, movingDataName)
	widget = CompareWidget(controller.widgets)
	widget.raise_()
	widget.show()
	controller.slicerChanged(controller.fixedImageWidget)
	app.exec_()
