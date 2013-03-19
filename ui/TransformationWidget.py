"""
TransformationWidget (QWidget)

Widget that displays a list of transformations

@author: Berend Klein Haneveld 2013
"""
from TransformationModel import TransformationModel
from core.AppVars import AppVars
from ButtonContainer import ButtonContainer
from TransformationListView import TransformationListView

try:
	from PySide.QtGui import QWidget
	from PySide.QtGui import QVBoxLayout
	from PySide.QtGui import QPushButton
	from PySide.QtGui import QIcon
except ImportError as e:
	raise e

class TransformationWidget(QWidget):
	"""
	Widget that controls the display of transformations in a list
	view. All actions of the view go through the controller.
	"""

	def __init__(self):
		"""
		Sets up the transformations widget
		"""
		super(TransformationWidget, self).__init__()
		
		self.transformations = []

		self.initUI()

	def initUI(self):
		"""
		Sets up the UI. Creates action button container
		and a list for displaying the transformations.
		"""
		# Create container for action buttons
		self.actionContainer = ButtonContainer()

		# Create the model for the transformations
		self.transformationModel = TransformationModel()
		
		# Create the view for the transformation model
		self.transformationsView = TransformationListView()
		self.transformationsView.setRootIsDecorated(False)
		self.transformationsView.setModel(self.transformationModel)

		# Create a main layout (vertical) for this widget
		self.layout = QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		
		# Add the widgets to the layout
		# Put actions underneath the main part of the widget
		# Just like in XCode/Finder
		self.layout.addWidget(self.transformationsView)
		self.layout.addWidget(self.actionContainer)
		
		# Set the layout
		self.setLayout(self.layout)
		
		# Add 'add' and 'remove' buttons to the container
		addButton = QPushButton()
		addButton.setIcon(QIcon(AppVars.imagePath() + "AddButton.png"))
		addButton.clicked.connect(self.addButtonClicked)
		
		removeButton = QPushButton()
		removeButton.setIcon(QIcon(AppVars.imagePath() + "RemoveButton.png"))
		removeButton.clicked.connect(self.removeButtonClicked)

		self.actionContainer.addButton(addButton)
		self.actionContainer.addButton(removeButton)

	def addButtonClicked(self):
		"""
		Tells the view to add a transformation to the end of the list.
		"""
		# TODO: instead of adding a transformation right away, show a window/
		# list of some default 'templates' of transformations.
		self.transformationsView.addTransformation()

	def removeButtonClicked(self):
		"""
		Tells the view to remove the selected transformation if there is one.
		"""
		self.transformationsView.removeSelectedTransformation()
