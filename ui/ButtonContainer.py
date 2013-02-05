"""
ButtonContainer (QWidget)

Container class that holds buttons in a row.
Buttons are modified to be square buttons and
they are displayed as flat buttons.

@author: Berend Klein Haneveld 2013
"""

try:
	from PySide import QtCore
	from PySide.QtGui import QWidget
	from PySide.QtGui import QHBoxLayout
except ImportError:
	raise ImportError("Could not import PySide")

class ButtonContainer(QWidget):
	Height = 24
	
	def __init__(self):
		"""
		Sets up the button container.
		"""
		super(ButtonContainer, self).__init__()
		
		self.initUI()

		# Keep track of the number of buttons
		self._buttonCount = 0
		pass

	def initUI(self):
		"""
		Initializes UI. Creates a horizontal layout
		to which buttons can be added.
		"""
		# Use a horizontal layout in which to keep
		# buttons. Initialize with an empty QWidget to 
		# make the buttons align to the left
		self.layout = QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.addWidget(QWidget())
		self.setLayout(self.layout)
		pass

	# Public methods

	def addButton(self, button):
		"""
		Adds a button to the container. The button is styled and
		resized to fit in the container widget.
		Assumes that the button has no name and has an 
		icon (preferably in the right size)

		@type button: QPushButton
		"""
		# Make sure that the button won't disturb the layout
		button.setMaximumHeight(ButtonContainer.Height)
		button.setMaximumWidth(ButtonContainer.Height)
		button.setFlat(True)
		
		# Insert button into the horizontal layout. Make sure
		# that the empty QWidget stays on the right
		self.layout.insertWidget(self._buttonCount, button)
		
		# TODO: Style the buttons or make some kind of seperator
		
		self._buttonCount += 1
		pass

	# Overwritten from QWidget
	
	def minimumWidth(self):
		"""
		@rtype: int
		"""
		return self._buttonCount * ButtonContainer.Height
		
	def maximumHeight(self):
		"""
		@rtype: int
		"""
		if self._buttonCount == 0:
			return 0
		
		return ButtonContainer.Height
		
	def minimumHeight(self):
		"""
		@rtype: int
		"""
		if self._buttonCount == 0:
			return 0
		
		return ButtonContainer.Height
	
	def sizeHint(self):
		"""
		@rtype: QtCore.QSize
		"""
		width = 150
		height = ButtonContainer.Height
		if self._buttonCount == 0:
			height = 0
		sizeHint = QtCore.QSize(width, height)
		return sizeHint
	