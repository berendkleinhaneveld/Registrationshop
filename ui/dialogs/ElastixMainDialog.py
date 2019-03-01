"""
ElastixMainDialog

:Authors:
	Berend Klein Haneveld
"""
from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QGridLayout
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QRadioButton
from PySide2.QtWidgets import QGroupBox
from PySide2.QtWidgets import QPushButton
from PySide2.QtCore import Qt
from PySide2.QtCore import Slot
from core.AppResources import AppResources


class ElastixMainDialog(QDialog):
	"""
	ElastixMainDialog
	"""

	def __init__(self, parent):
		super(ElastixMainDialog, self).__init__(parent)
		self.transformation = None

		self.transformations = AppResources.elastixTemplates()
		self.radioButtons = []
		for transformation in self.transformations:
			self.radioButtons.append(QRadioButton(transformation.name))
		self.radioButtons.append(QRadioButton("Load custom parameter file..."))
		self.radioButtons[0].setChecked(True)

		self.nextButton = QPushButton("Next")
		self.nextButton.clicked.connect(self.next)
		self.cancelButton = QPushButton("Cancel")
		self.cancelButton.clicked.connect(self.cancel)

		groupLayout = QVBoxLayout()
		for radioButton in self.radioButtons:
			groupLayout.addWidget(radioButton)

		self.groupBox = QGroupBox("Choose parameter file")
		self.groupBox.setLayout(groupLayout)

		self.setModal(True)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.groupBox, 0, 0, 1, 2)
		layout.addWidget(self.cancelButton, 1, 0)
		layout.addWidget(self.nextButton, 1, 1)
		self.setLayout(layout)

	@Slot()
	def next(self):
		selectedIndex = 0
		for index in range(len(self.radioButtons)):
			radioButton = self.radioButtons[index]
			if radioButton.isChecked():
				selectedIndex = index
		if selectedIndex == len(self.transformations):
			# load custom transformation
			self.accept()
		else:
			# load choosen transformation
			self.transformation = self.transformations[selectedIndex]
			self.accept()

	@Slot()
	def cancel(self):
		self.reject()
