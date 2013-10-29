"""
UserTransformationTool (TransformationTool)

:Authors:
	Berend Klein Haneveld
"""
from TransformationTool import TransformationTool
from TransformationList import TransformationList
from core.decorators import overrides
from ui.widgets.StatusWidget import StatusWidget
from ui.transformations import TransformBox
from vtk import vtkTransform
from vtk import vtkMatrix4x4
from PySide.QtGui import QLabel
from PySide.QtGui import QWidget
from PySide.QtGui import QLineEdit
from PySide.QtGui import QGridLayout
from PySide.QtGui import QDoubleValidator
from PySide.QtGui import QTabWidget
from PySide.QtCore import Slot
from PySide.QtCore import Qt


class UserTransformationTool(TransformationTool):
	def __init__(self):
		super(UserTransformationTool, self).__init__()

		self.transformBox = TransformBox()
		self.transformBox.transformUpdated.connect(self.transformUpdated)
		self._originalUpdateRate = 15  # Default

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		self.movingWidget = moving
		self.renderWidget = multi
		self._originalUpdateRate = self.renderWidget.rwi.GetDesiredUpdateRate()
		self.renderWidget.rwi.SetDesiredUpdateRate(5)
		self.transformBox.setWidget(self.renderWidget)
		self.transformBox.setImageData(self.renderWidget.movingImageData)

		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Use the box widget to transform the volume.")

	@overrides(TransformationTool)
	def cleanUp(self):
		self.transformBox.cleanUp()

		# Reset the transformation
		self.movingWidget.resetUserTransform()
		self.movingWidget.render()
		self.renderWidget.resetUserTransform()
		self.renderWidget.rwi.SetDesiredUpdateRate(self._originalUpdateRate)
		self.renderWidget.render()

	@overrides(TransformationTool)
	def applyTransform(self):
		self.movingWidget.applyUserTransform()
		self.renderWidget.applyUserTransform()

	@overrides(TransformationTool)
	def getParameterWidget(self):
		matrixWidget = QWidget()
		matrixLayout = QGridLayout()
		self.m1Edits = [QLineEdit() for x in range(4)]
		self.m2Edits = [QLineEdit() for x in range(4)]
		self.m3Edits = [QLineEdit() for x in range(4)]
		self.m4Edits = [QLineEdit() for x in range(4)]
		self.initLineEdits(self.m1Edits, matrixLayout, 0, 0)
		self.initLineEdits(self.m2Edits, matrixLayout, 1, 0)
		self.initLineEdits(self.m3Edits, matrixLayout, 2, 0)
		self.initLineEdits(self.m4Edits, matrixLayout, 3, 0)

		paramsWidget = QWidget()

		paramsLayout = QGridLayout()
		paramsLayout.addWidget(QLabel("x"), 0, 1)
		paramsLayout.addWidget(QLabel("y"), 0, 2)
		paramsLayout.addWidget(QLabel("z"), 0, 3)

		paramsLayout.addWidget(QLabel("Translation"), 1, 0)
		self.translateEdits = [QLineEdit() for x in range(3)]
		self.initLineEdits(self.translateEdits, paramsLayout, 1, 1)

		paramsLayout.addWidget(QLabel("Rotation"), 2, 0)
		self.rotationEdits = [QLineEdit() for x in range(3)]
		self.initLineEdits(self.rotationEdits, paramsLayout, 2, 1)
		
		paramsLayout.addWidget(QLabel("Scale"), 3, 0)
		self.scaleEdits = [QLineEdit() for x in range(3)]
		self.initLineEdits(self.scaleEdits, paramsLayout, 3, 1)
		
		matrixWidget.setLayout(matrixLayout)
		paramsWidget.setLayout(paramsLayout)

		self.tabWidget = QTabWidget()
		self.tabWidget.addTab(matrixWidget, "Matrix")
		self.tabWidget.addTab(paramsWidget, "Parameters")

		self.transformUpdated(self.renderWidget.getUserTransform())

		return self.tabWidget
	
	@Slot(object)
	def transformUpdated(self, transform):
		"""
		:type transform: vtkTransform
		"""
		# TODO: get the transform from the multi render widget when
		# transform is adjusted

		completeTransform = self.renderWidget.getFullTransform()
		transList = TransformationList()
		transList.append(completeTransform)
		shearTrans = transList.scalingTransform()
		self.movingWidget.setUserTransform(shearTrans)
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
	
		orientation = transform.GetOrientation()
		position = transform.GetPosition()
		scale = transform.GetScale()
		
		self._updateText(self.rotationEdits, orientation)
		self._updateText(self.translateEdits, position)
		self._updateText(self.scaleEdits, scale)

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

		if self.tabWidget.currentIndex() == 0:
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
		elif self.tabWidget.currentIndex() == 1:
			translate = self._readArrayOfValues(self.translateEdits)
			transform.Translate(translate)
			rotate = self._readArrayOfValues(self.rotationEdits)
			transform.RotateZ(rotate[2])
			transform.RotateY(rotate[1])
			transform.RotateX(rotate[0])
			scale = self._readArrayOfValues(self.scaleEdits, 1.0)
			transform.Scale(scale)

		transform.Modified()
		transform.Update()
		self.renderWidget.setUserTransform(transform)
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
