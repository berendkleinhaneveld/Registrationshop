"""
UserTransformationTool (TransformationTool)

:Authors:
	Berend Klein Haneveld
"""
from ui.TransformationTool import TransformationTool
from core.decorators import overrides
from vtk import vtkBoxWidget
from vtk import vtkTransform
from PySide.QtGui import QLabel
from PySide.QtGui import QWidget
from PySide.QtGui import QLineEdit
from PySide.QtGui import QGridLayout
from PySide.QtGui import QDoubleValidator


class UserTransformationTool(TransformationTool):
	def __init__(self):
		super(UserTransformationTool, self).__init__()

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		self.renderWidget = multi
		self.setImageData(self.renderWidget.movingImageData)

	@overrides(TransformationTool)
	def cleanUp(self):
		# Hide the transformation box
		self.transformBox.EnabledOff()
		self.cleanUpCallbacks()

		# Reset the transformation
		self.renderWidget.resetUserTransform()

	def applyTransform(self):
		self.renderWidget.applyUserTransform()

	def setImageData(self, movingImageData):
		self.transformBox = vtkBoxWidget()
		self.transformBox.SetInteractor(self.renderWidget.rwi)
		self.transformBox.SetPlaceFactor(1.01)
		self.transformBox.SetInputData(movingImageData)
		self.transformBox.SetDefaultRenderer(self.renderWidget.renderer)
		self.transformBox.InsideOutOn()
		self.transformBox.PlaceWidget()

		self.AddObserver(self.transformBox, "InteractionEvent", self.transformCallback)
		self.transformBox.GetSelectedFaceProperty().SetOpacity(0.3)
		self.transformBox.EnabledOn()

	def transformCallback(self, arg1, arg2):
		transform = vtkTransform()
		arg1.GetTransform(transform)
		self.renderWidget.setUserTransform(transform)
		self.transformUpdated(transform)

	@overrides(TransformationTool)
	def getParameterWidget(self):
		layout = QGridLayout()
		layout.addWidget(QLabel("Translation"), 0, 0)

		self.translateEdits = [QLineEdit() for x in range(3)]
		self.initLineEdits(self.translateEdits, layout, 0, 1)

		layout.addWidget(QLabel("Rotation"), 1, 0)
		self.rotationEdits = [QLineEdit() for x in range(3)]
		self.initLineEdits(self.rotationEdits, layout, 1, 1)
		
		layout.addWidget(QLabel("Scale"), 2, 0)
		self.scaleEdits = [QLineEdit() for x in range(3)]
		self.initLineEdits(self.scaleEdits, layout, 2, 1)
		
		self.transformUpdated(self.renderWidget.getUserTransform())

		widget = QWidget()
		widget.setLayout(layout)
		return widget

	def initLineEdits(self, lineEdits, layout, row, colOffset):
		colIndex = 0
		for lineEdit in lineEdits:
			lineEdit.setValidator(QDoubleValidator())
			lineEdit.setText("0.0")
			lineEdit.textEdited.connect(self.updateTransformFromText)
			layout.addWidget(lineEdit, row, colOffset + colIndex)
			colIndex += 1

	def updateTransformFromText(self, text):
		transform = vtkTransform()

		translate = self.readArrayOfValues(self.translateEdits)
		transform.Translate(translate)
		rotate = self.readArrayOfValues(self.rotationEdits)
		transform.RotateZ(rotate[2])
		transform.RotateY(rotate[1])
		transform.RotateX(rotate[0])
		scale = self.readArrayOfValues(self.scaleEdits, 1.0)
		transform.Scale(scale)
		transform.Modified()
		transform.Update()
		self.renderWidget.setUserTransform(transform)
		# TODO: fix 'latency' of update...

	def readArrayOfValues(self, lineEdits, default=0.0):
		values = []
		for translateEdit in lineEdits:
			try:
				value = float(translateEdit.text())
				values.append(value)
			except Exception:
				values.append(default)
		return values

	def transformUpdated(self, transform):
		"""
		:type transform: vtkTransform
		"""
		# TODO: get the transform from the multi render widget when
		# transform is adjusted
		orientation = transform.GetOrientation()
		position = transform.GetPosition()
		scale = transform.GetScale()
		
		self.updateText(self.rotationEdits, orientation)
		self.updateText(self.translateEdits, position)
		self.updateText(self.scaleEdits, scale)

	def updateText(self, lineEdits, values):
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
