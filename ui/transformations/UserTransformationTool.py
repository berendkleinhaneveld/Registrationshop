"""
UserTransformationTool (TransformationTool)

:Authors:
	Berend Klein Haneveld
"""
from TransformationTool import TransformationTool
from core.decorators import overrides
from ui.transformations import TransformBox
from ui.transformations import Transformation
from ui.widgets.StatusWidget import StatusWidget
from core.project import ProjectController
from vtk import vtkTransform
from vtk import vtkMatrix4x4
from PySide.QtGui import QLabel
from PySide.QtGui import QWidget
from PySide.QtGui import QLineEdit
from PySide.QtGui import QGridLayout
from PySide.QtGui import QDoubleValidator
from PySide.QtGui import QSizePolicy
from PySide.QtCore import Slot
from PySide.QtCore import Qt


class UserTransformationTool(TransformationTool):
	def __init__(self):
		super(UserTransformationTool, self).__init__()

		self.transformBox = TransformBox()
		self.transformBox.transformUpdated.connect(self.transformBoxUpdated)

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		self.movingWidget = moving
		self.renderWidget = multi
		currentProject = ProjectController.Instance().currentProject
		self.transformBox.setWidget(self.renderWidget)
		self.transformBox.setImageData(self.renderWidget.movingImageData)
		self.renderWidget.transformations.append(Transformation(vtkTransform(), Transformation.TypeUser, currentProject.movingData))

		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Use the box widget to transform the volume. "
			"For more specific control of the transformation, use the matrix values to specify the transform.")

	@overrides(TransformationTool)
	def cleanUp(self):
		self.transformBox.cleanUp()

		# Reset the transformation
		self.renderWidget.render()
		self.movingWidget.render()

		self.toolFinished.emit()

	def cancelTransform(self):
		# Remove the last transformation
		del self.renderWidget.transformations[-1]

	@overrides(TransformationTool)
	def applyTransform(self):
		pass

	@overrides(TransformationTool)
	def getParameterWidget(self):
		matrixLayout = QGridLayout()
		matrixLayout.setAlignment(Qt.AlignTop)
		matrixLayout.setContentsMargins(0, 0, 0, 0)
		matrixLayout.setSpacing(5)
		matrixLayout.addWidget(QLabel("Transformation matrix:"), 0, 0, 1, 4)
		self.m1Edits = [QLineEdit() for _ in range(4)]
		self.m2Edits = [QLineEdit() for _ in range(4)]
		self.m3Edits = [QLineEdit() for _ in range(4)]
		self.m4Edits = [QLineEdit() for _ in range(4)]
		self.initLineEdits(self.m1Edits, matrixLayout, 1, 0)
		self.initLineEdits(self.m2Edits, matrixLayout, 2, 0)
		self.initLineEdits(self.m3Edits, matrixLayout, 3, 0)
		self.initLineEdits(self.m4Edits, matrixLayout, 4, 0)
		expandingWidget = QWidget()
		expandingWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
		matrixLayout.addWidget(expandingWidget, 5, 0, 1, 4)
		
		matrixWidget = QWidget()
		matrixWidget.setLayout(matrixLayout)
		self.transformUpdated(self.renderWidget.transformations.completeTransform())

		return matrixWidget
	
	@Slot()
	def transformBoxUpdated(self, transform):
		transformation = self.renderWidget.transformations[-1]
		assert transformation.transformType == Transformation.TypeUser
		transformation.transform = transform
		# 'Replace' last element so that the update mechanism triggers
		self.renderWidget.transformations[-1] = transformation
		self.transformUpdated(transform)

	@Slot(object)
	def transformUpdated(self, transform):
		"""
		:type transform: vtkTransform
		"""
		self.movingWidget.render()

		matrix = transform.GetMatrix()
		values = []
		for x in range(4):
			for y in range(4):
				values.append(matrix.GetElement(x, y))
		self._updateText(self.m1Edits, values[0:4])
		self._updateText(self.m2Edits, values[4:8])
		self._updateText(self.m3Edits, values[8:12])
		self._updateText(self.m4Edits, values[12:16])
	
	def initLineEdits(self, lineEdits, layout, row, colOffset):
		colIndex = 0
		for lineEdit in lineEdits:
			lineEdit.setValidator(QDoubleValidator())
			lineEdit.setText("0.0")
			lineEdit.setAlignment(Qt.AlignRight)
			lineEdit.textEdited.connect(self.updateTransformFromText)
			layout.addWidget(lineEdit, row, colOffset + colIndex)
			colIndex += 1

	def updateTransformFromText(self, text):
		transform = vtkTransform()
	
		line1 = self._readArrayOfValues(self.m1Edits)
		line2 = self._readArrayOfValues(self.m2Edits)
		line3 = self._readArrayOfValues(self.m3Edits)
		line4 = self._readArrayOfValues(self.m4Edits)
		values = line1+line2+line3+line4
		matrix = vtkMatrix4x4()
		element = 0
		for x in range(4):
			for y in range(4):
				matrix.SetElement(x, y, values[element])
				element += 1
		transform.SetMatrix(matrix)
		transform.Modified()
		transform.Update()

		transformation = self.renderWidget.transformations[-1]
		assert transformation.transformType == Transformation.TypeUser
		transformation.transform = transform
		self.renderWidget.transformations[-1] = transformation
		self.transformBox.setTransform(transform)
		self.renderWidget.render()

	def _updateText(self, lineEdits, values):
		"""
		Update the text of the given QLineEdit objects to
		the values in values object.
		:type lineEdits: list (QLineEdit)
		:type values: list (float)
		"""
		assert len(lineEdits) == len(values)
		for index in range(len(lineEdits)):
			value = values[index]
			lineEdit = lineEdits[index]
			lineEdit.setText("%6.2f" % value)

	def _readArrayOfValues(self, lineEdits, default=0.0):
		values = []
		for translateEdit in lineEdits:
			try:
				value = float(translateEdit.text())
				values.append(value)
			except Exception:
				values.append(default)
		return values
