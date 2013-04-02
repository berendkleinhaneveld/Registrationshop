"""
VisualizationParametersWidget

:Authors:
	Berend Klein Haneveld 2013
"""

try:
	from PySide.QtGui import QWidget
	from PySide.QtGui import QVBoxLayout
	from PySide.QtGui import QTextEdit
except ImportError, e:
	raise e

from ButtonContainer import ButtonContainer

class VisualizationParametersWidget(QWidget):
	"""
	Widget that holds the parameters for the main visualization
	"""

	def __init__(self):
		"""
		Sets up the visualization parameters widget.
		"""
		super(VisualizationParametersWidget, self).__init__()
		
		self.initUI()
		pass

	def initUI(self):
		"""
		Sets up the UI. Creates vertical layout and adds
		a list widget.
		"""
		# Create container for action buttons
		self.actionButtons = ButtonContainer()
		
		self.layout = QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		
		# Add the widgets to the layout
		# Put actions underneath the main part of the widget
		# Just like in XCode/Finder/Settings
		self.layout.addWidget(QTextEdit())
		self.layout.addWidget(self.actionButtons)
		
		self.setLayout(self.layout)
		pass
		
