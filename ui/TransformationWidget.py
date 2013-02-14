"""
TransformationWidget (QWidget)

Widget that displays a list of transformations

@author: Berend Klein Haneveld 2013
"""

try:
	from PySide.QtGui import QWidget
	from PySide.QtGui import QVBoxLayout
	from PySide.QtGui import QPushButton
	from PySide.QtGui import QIcon
	from PySide.QtGui import QTextEdit
except ImportError:
	raise ImportError("Could not import PySide")

from core.AppVars import AppVars
from ButtonContainer import ButtonContainer

class TransformationWidget(QWidget):
	def __init__(self):
		"""
		Sets up the transformations widget
		"""
		super(TransformationWidget, self).__init__()
		
		self.initUI()
		pass

	def initUI(self):
		"""
		Sets up the UI. Creates action button container
		and a list for displaying the transformations.
		"""
		# Create container for action buttons
		self.actionContainer = ButtonContainer()
		
		# Create a main layout (vertical) for this widget
		self.layout = QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		
		# Add the widgets to the layout
		# Put actions underneath the main part of the widget
		# Just like in XCode/Finder
		self.layout.addWidget(QTextEdit())
		self.layout.addWidget(self.actionContainer)
		
		# Set the layout
		self.setLayout(self.layout)
		
		# Add a button to the container
		button = QPushButton()
		button.setIcon(QIcon(AppVars.imagePath() + "AddButton.png"))
		button.clicked.connect(self.empty)
		self.actionContainer.addButton(button)
		pass

	def empty(self):
		print "empty"