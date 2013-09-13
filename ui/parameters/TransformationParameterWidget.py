"""
TransformationParameterWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
# from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QScrollArea
from PySide.QtCore import Qt
from PySide.QtCore import Slot


class TransformationParameterWidget(QWidget):
	"""
	TransformationParameterWidget
	"""

	def __init__(self):
		super(TransformationParameterWidget, self).__init__()

		self.cancelButton = QPushButton("Cancel")
		self.cancelButton.clicked.connect(self.cancelButtonClicked)
		self.applyButton = QPushButton("Apply")
		self.applyButton.clicked.connect(self.applyButtonClicked)

		self.scrollLayout = QGridLayout()
		self.scrollLayout.setAlignment(Qt.AlignTop)

		self.scrollArea = QScrollArea()
		self.scrollArea.setLayout(self.scrollLayout)

		self.showControls(False)

		self.transformationWidget = None
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.scrollArea, 0, 0, 1, 2)
		layout.addWidget(self.cancelButton, 1, 0)
		layout.addWidget(self.applyButton, 1, 1)
		self.setLayout(layout)

	def setTransformationTool(self, transformationTool):
		self.transformationTool = transformationTool

		self.cleanUpTransformWidget()

		self.transformationWidget = self.transformationTool.getParameterWidget()
		self.scrollLayout.addWidget(self.transformationWidget)
		self.showControls(True)

	@Slot()
	def cancelButtonClicked(self):
		self.showControls(False)
		self.cleanUpTransformWidget()
		self.transformationTool.cleanUp()
		self.transformationTool = None

	@Slot()
	def applyButtonClicked(self):
		"""
		Applies the transform and hides the apply / cancel buttons
		"""
		# TODO: apply transformation
		self.showControls(False)
		self.cleanUpTransformWidget()
		self.transformationTool.cleanUp()
		self.transformationTool = None

	def showControls(self, show):
		self.scrollArea.setVisible(show)
		self.applyButton.setVisible(show)
		self.cancelButton.setVisible(show)

	def cleanUpTransformWidget(self):
		item = self.scrollLayout.takeAt(0)
		if item:
			item.widget().deleteLater()
