"""
DeformableTransformationTool

:Authors:
	Berend Klein Haneveld 2013
"""
import os
from TransformationTool import TransformationTool
from ParameterWidget import ParameterWidget
from ui.transformations import Transformation
from ui.widgets.StatusWidget import StatusWidget
from vtk import vtkTransform
from core.decorators import overrides
from core.worker import Operator
from core.elastix import ElastixCommand
from core.elastix import TransformixTransformation
from core.project import ProjectController
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtCore import Qt
from PySide.QtCore import Signal


class DeformableTransformationTool(TransformationTool):

	startedElastix = Signal(str)
	endedElastix = Signal()

	def __init__(self):
		super(DeformableTransformationTool, self).__init__()

	def setTransformation(self, transformation):
		self.transformation = transformation

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed, moving, multi):
		self.fixedWidget = fixed
		self.multiWidget = multi
		self.movingWidget = moving

		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Adjust the parameters for the transform. See the Elastix " +
			"website for more details on the available parameters.")

	@overrides(TransformationTool)
	def applyTransform(self):
		"""
		* Show progress bar dialog
		* Define folder for output (projectFolder/data/result-<id>/.)
		* Write parameter file to output folder
		* Call elastix to process the data
		* Load the new data into the moving widget / project
		"""
		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Please grab a cup of coffee while Elastix " +
			"performs the registration: this might take a while...")

		self.startedElastix.emit("Transforming data...")

		projectController = ProjectController.Instance()
		currentProject = projectController.currentProject
		path = currentProject.folder
		
		if not path:
			statusWidget.setText("Please create and save a project first so "
				"that the results of the registration can be saved to disk.")
			return

		# Determine filename + folder for new dataset (projectFolder/data/result-<id>/.)
		dataFolder = os.path.join(path, "data")
		filenames = os.listdir(dataFolder) if os.path.isdir(dataFolder) else []
		resultId = 0
		for filename in filenames:
			if os.path.isdir(os.path.join(dataFolder, filename)) and "result" in filename:
				resultId += 1
		outputFolder = os.path.join(dataFolder, "result-" + str(resultId))

		parameterFilePath = os.path.join(outputFolder, "Parameters.txt")
		initialTransformPath = os.path.join(outputFolder, "InitialTransformation.txt")

		# Iterate over the parameters to ensure that some parameters are adjusted
		# according to the data from the project
		for i in range(len(self.transformation)):
			param = self.transformation[i]
			if param.key() == "DefaultPixelValue":
				# Set the default pixel value to minimum scalar value
				scalarRange = self.movingWidget.imageData.GetScalarRange()
				param.setValue(scalarRange[0])
			if param.key() == "ResultImagePixelType":
				# Set the resulting image pixel type to the type of the input data
				pixelType = self.movingWidget.imageData.GetScalarTypeAsString()
				param.setValue(pixelType)

		self.transformation.saveToFile(parameterFilePath)
		transform = self.multiWidget.transformations.completeTransform()
		dataset = ProjectController.Instance().currentProject.movingData
		initialTransform = TransformixTransformation(dataset, transform).transformation()
		if initialTransform:
			initialTransform.saveToFile(initialTransformPath)
		else:
			initialTransformPath = None

		command = ElastixCommand(fixedData=currentProject.fixedData,
			movingData=currentProject.movingData,
			outputFolder=outputFolder,
			transformation=parameterFilePath,
			initialTransformation=initialTransformPath)

		self.operator = Operator()
		self.operator.addCommand(command)
		self.operator.queue.join()

		self.endedElastix.emit()

		# Assume that there is only one resulting dataset: result.0.mhd
		outputData = os.path.join(outputFolder, "result.0.mhd")
		if os.path.exists(outputData):
			statusWidget.setText("Thanks for your patience. The " +
				"transformed data will now be loaded. It can be found in the project folder.")

			transformation = Transformation(vtkTransform(), Transformation.TypeDeformable, outputData)
			self.multiWidget.transformations.append(transformation)
			projectController.loadMovingDataSet(outputData)
		else:
			statusWidget.setText("Something went wrong. Please see the project folder for the "
				+ "elastix log to see what went wrong.")
			from subprocess import call
			call(["open", outputFolder])

	@overrides(TransformationTool)
	def cancelTransform(self):
		pass

	@overrides(TransformationTool)
	def cleanUp(self):
		self.toolFinished.emit()

	@overrides(TransformationTool)
	def getParameterWidget(self):
		titleLabel = QLabel(self.transformation.name)

		paramWidget = ParameterWidget()
		paramWidget.parameterModel.setTransformation(self.transformation)

		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(titleLabel)
		layout.addWidget(paramWidget)

		widget = QWidget()
		widget.setLayout(layout)
		return widget
