"""
ResetVisualizationDialog

:Authors:
	Berend Klein Haneveld 2013
"""

from PySide.QtGui import QDialog
from PySide.QtGui import QLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Slot


class ResetVisualizationDialog(QDialog):
	"""
	Custom dialog that asks the user if the visualizations should
	be reset before loading the new data.
	"""
	def __init__(self, parent):
		super(ResetVisualizationDialog, self).__init__(parent)
		self.result = None

		noButton = QPushButton("No")
		noButton.clicked.connect(self._noButtonClicked)
		yesButton = QPushButton("Yes")
		yesButton.clicked.connect(self._yesButtonClicked)

		layout = QGridLayout()
		layout.setSizeConstraint(QLayout.SetFixedSize)
		layout.addWidget(QLabel("A new dataset is loaded. Should the \nvisualization parameters be reset?"), 0, 0, 1, 2)
		layout.addWidget(noButton, 1, 0)
		layout.addWidget(yesButton, 1, 1)

		self.setLayout(layout)

	@Slot()
	def _noButtonClicked(self):
		self.result = False
		self.accept()

	@Slot()
	def _yesButtonClicked(self):
		self.result = True
		self.accept()
