"""
SlicerWidget

Class that shows a slicer with controls for loading data, etc.

@author: Berend Klein Haneveld 2013
"""

try:
	from PySide.QtGui import QWidget
	from PySide.QtGui import QPushButton
	from PySide.QtGui import QIcon
	from PySide.QtGui import QVBoxLayout
	from PySide.QtGui import QTextEdit
	from PySide.QtGui import QFileDialog
except ImportError:
	raise ImportError("Could not import PySide")

from core.AppVars import AppVars
from ButtonContainer import ButtonContainer

class SlicerWidget(QWidget):
	def __init__(self):
		"""
		Sets up the slicer widget.
		"""
		super(SlicerWidget, self).__init__()
		
		self.initUI()
		pass

	def initUI(self):
		"""
		Sets up the UI. Creates vertical layout and adds
		a list widget.
		"""
		# Create container for action buttons
		self.actionButtons = ButtonContainer()
		button = QPushButton()
		button.setIcon(QIcon(AppVars.imagePath() + "AddButton.png"))
		button.clicked.connect(self.loadFile)
		self.actionButtons.addButton(button)

		# Create a main layout (vertical) for this widget
		self.layout = QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		
		# Put actions underneath the main part of the widget
		# Just like in XCode/Finder
		self.layout.addWidget(QTextEdit())
		self.layout.addWidget(self.actionButtons)
		
		self.setLayout(self.layout)
		pass

	def loadFile(self):
		fileName, other = QFileDialog.getOpenFileName(self, "Open fixed data set", "", "Images (*.mhd)")
		if len(fileName) > 0:
			print "Name:", fileName
			# self.projectController.loadFixedDataSet(fileName)