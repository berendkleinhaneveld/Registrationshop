"""
TransformationHistoryWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QIcon
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QPushButton
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

		layout = QVBoxLayout()
		layout.setSpacing(0)
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.transformationView)
		layout.addWidget(self.actionContainer)
		self.setLayout(layout)

		removeButton = QPushButton()
		removeButton.setIcon(QIcon(AppVars.imagePath() + "RemoveButton.png"))
		removeButton.clicked.connect(self.removeButtonClicked)
		self.actionContainer.addButton(removeButton)

	def setMultiRenderWidget(self, widget):
		self.renderWidget = widget
		self.renderWidget.transformations.transformationChanged.connect(self.updateTransformations)

	def updateTransformations(self, transformations):
		self.transformationModel.setTransformations(transformations)

	def removeButtonClicked(self):
		self.transformationView.removeSelectedRow()
