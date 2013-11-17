"""
PickerTypeDialog

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QDialog
from PySide.QtGui import QGridLayout
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QRadioButton
from PySide.QtGui import QGroupBox
from PySide.QtGui import QButtonGroup
from PySide.QtGui import QPushButton
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from ui.transformations.LandmarkTransformationTool import SurfaceType
from ui.transformations.LandmarkTransformationTool import TwoStepType


class PickerTypeDialog(QDialog):
	"""
	PickerTypeDialog
	"""

	def __init__(self, parent):
		super(PickerTypeDialog, self).__init__(parent)

		self.pickerType = None

		self.pickerTypes = [(SurfaceType, "Surface picker"),
			(TwoStepType, "Two step picker")]

		self.radioButtons = []
		for picker in self.pickerTypes:
			self.radioButtons.append(QRadioButton(picker[1]))
		# self.radioButtons[0].setChecked(True)
		self.buttonGroup = QButtonGroup()
		ind = 0
		for button in self.radioButtons:
			self.buttonGroup.addButton(button)
			self.buttonGroup.setId(button, ind)
			ind += 1

		self.nextButton = QPushButton("Choose")
		self.nextButton.clicked.connect(self.choose)
		self.cancelButton = QPushButton("Cancel")
		self.cancelButton.clicked.connect(self.cancel)

		groupLayout = QVBoxLayout()
		for radioButton in self.radioButtons:
			groupLayout.addWidget(radioButton)
		
		self.groupBox = QGroupBox("Choose picker type:")
		self.groupBox.setLayout(groupLayout)

		self.setModal(True)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.groupBox, 0, 0, 1, 2)
		layout.addWidget(self.cancelButton, 1, 0)
		layout.addWidget(self.nextButton, 1, 1)
		self.setLayout(layout)

	@Slot()
	def choose(self):
		selectedIndex = self.buttonGroup.checkedId()
		if selectedIndex >= 0:
			# load choosen picker type
			self.pickerType = self.pickerTypes[selectedIndex][0]
			self.accept()

	@Slot()
	def cancel(self):
		self.reject()
