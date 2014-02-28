"""
TransformationHistoryWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QIcon
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QMessageBox
from PySide.QtCore import Qt
from core.AppVars import AppVars
from ui.widgets import ButtonContainer
from ui.transformations import TransformationModel
from ui.transformations import TransformationListView


class TransformationHistoryWidget(QWidget):
	"""
	TransformationHistoryWidget shows a list of applied transformations.
	"""
	def __init__(self):
		super(TransformationHistoryWidget, self).__init__()

		self.actionContainer = ButtonContainer()
		self.transformationModel = TransformationModel()

		self.transformationView = TransformationListView()
		self.transformationView.setRootIsDecorated(False)
		self.transformationView.setModel(self.transformationModel)
		self.transformationView.setAttribute(Qt.WA_MacShowFocusRect, False)
		self.transformationView.clicked.connect(self.clickedTransformation)

		self._transformCount = 0

		layout = QVBoxLayout()
		layout.setSpacing(0)
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.transformationView)
		layout.addWidget(self.actionContainer)
		self.setLayout(layout)

		removeButton = QPushButton()
		removeButton.setIcon(QIcon(AppVars.imagePath() + "RemoveButton.png"))
		removeButton.clicked.connect(self.removeButtonClicked)
		removeButton.setToolTip("Remove the last transformation")
		self.actionContainer.addButton(removeButton)

	def setMultiRenderWidget(self, widget):
		self.renderWidget = widget
		self.renderWidget.transformations.transformationChanged.connect(self.updateTransformations)

	def updateTransformations(self, transformations):
		"""
		Update the model. If the number of transformations is bigger
		than last time: clear the selection.
		"""
		if len(transformations) > self._transformCount:
			self.transformationView.clearSelection()
		self._transformCount = len(transformations)
		self.transformationModel.setTransformations(transformations)

	def removeButtonClicked(self):
		"""
		Remove the last transformation in the list.
		"""
		messageBox = QMessageBox()
		messageBox.setText("The last transformation is about to be removed.")
		messageBox.setInformativeText("Do you want to proceed?")
		messageBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		messageBox.setDefaultButton(QMessageBox.Ok)
		res = messageBox.exec_()
		if res == QMessageBox.Ok:
			self.transformationView.removeLastRow()

	def clickedTransformation(self, index):
		"""
		Activate the transformation from the complete list.
		"""
		self.renderWidget.transformations.activateTransformationAtIndex(index.row())
