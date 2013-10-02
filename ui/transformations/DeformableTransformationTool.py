"""
DeformableTransformationTool

:Authors:
	Berend Klein Haneveld 2013
"""
import os
from TransformationTool import TransformationTool
from core.decorators import overrides
from ParameterWidget import ParameterWidget
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

	@overrides(TransformationTool)
	def applyTransform(self):
		"""
		# DONE
		* Show progress bar dialog
		* Define location for output
		* Write transformation to output folder
		* Call elastix to process the data
		# TODO
		* Load the new data into the moving widget / project (or
			maybe ask the user whether he wants to import it)
		* Maybe construct an extra entry in ProjectController for
			the transformed data. So that the reference to the old
			data is not lost.
		"""
		self.startedElastix.emit("Transforming data...")

		currentProject = ProjectController.Instance().currentProject
		path = currentProject.folder
		
		transformationPath = os.path.join(path, "data/Transformation.txt")
		initialTransformPath = os.path.join(path, "data/InitialTransformation.txt")
		outputFolder = os.path.join(path, "data")

		self.transformation.saveToFile(transformationPath)
		transform = self.multiWidget.getFullTransform()
		dataset = ProjectController.Instance().currentProject.movingData
		initialTransform = TransformixTransformation(dataset, transform)
		parameters = initialTransform.transformation()
		parameters.saveToFile(initialTransformPath)

		command = ElastixCommand(fixedData=currentProject.fixedData,
			movingData=currentProject.movingData,
			outputFolder=outputFolder,
			transformation=transformationPath,
			initialTransformation=initialTransformPath)

		self.operator = Operator()
		self.operator.addCommand(command)
		self.operator.queue.join()

		self.endedElastix.emit()

		outputData = os.path.join(outputFolder, "result.0.mhd")
		if os.path.exists(outputData):
			projectController = ProjectController.Instance()
			projectController.loadMovingDataSet(outputData)

	@overrides(TransformationTool)
	def cleanUp(self):
		pass

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
