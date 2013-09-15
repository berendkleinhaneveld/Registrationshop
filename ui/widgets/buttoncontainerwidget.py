"""
ButtonContainer (QWidget)

Container class that holds buttons in a row.
Buttons are modified to be square buttons and
they are displayed as flat buttons.

:Authors:
	Berend Klein Haneveld 2013
"""

from PySide import QtCore
from PySide.QtGui import QWidget
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QPalette
from PySide.QtGui import QBrush
from PySide.QtGui import QLinearGradient
from PySide.QtGui import QColor
from PySide.QtCore import Qt


class ButtonContainer(QWidget):
	Height = 22

	def __init__(self, orientation=Qt.Horizontal):
		"""
		Sets up the button container.
		"""
		super(ButtonContainer, self).__init__()

		self.orientation = orientation

		self.initUI()

		# Keep track of the number of buttons
		self._buttonCount = 0

	def initUI(self):
		"""
		Initializes UI. Creates a horizontal layout
		to which buttons can be added.
		"""
		gradient = QLinearGradient()
		gradient.setStart(0, 0)
		gradient.setFinalStop(0, self.Height)
		# TODO: get colors from theme
		color1 = QColor(230, 230, 230, 255)
		color2 = QColor(177, 177, 177, 255)
		gradient.setColorAt(0, color1)
		gradient.setColorAt(1, color2)
		brush = QBrush(gradient)

		palette = QPalette()
		palette.setBrush(QPalette.Background, brush)

		self.setAutoFillBackground(True)
		self.setPalette(palette)

		# Use a horizontal layout in which to keep
		# buttons. Initialize with an empty QWidget to
		# make the buttons align to the left
		if self.orientation == Qt.Horizontal:
			self.layout = QHBoxLayout()
		else:
			self.layout = QVBoxLayout()
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

		:type button: QPushButton
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

	def sizeOfButtons(self):
		return self._buttonCount * ButtonContainer.Height

	def sizeOfContainer(self):
		if self._buttonCount == 0:
			return 0
		return ButtonContainer.Height

	def maximumWidth(self):
		"""
		:rtype: int
		"""
		if self.orientation == Qt.Horizontal:
			return 0
		else:
			return self.sizeOfContainer()

	def minimumWidth(self):
		"""
		:rtype: int
		"""
		if self.orientation == Qt.Horizontal:
			return self.sizeOfButtons()
		else:
			return self.sizeOfContainer()

	def maximumHeight(self):
		"""
		:rtype: int
		"""
		if self.orientation == Qt.Horizontal:
			return self.sizeOfContainer()
		else:
			return 0

	def minimumHeight(self):
		"""
		:rtype: int
		"""
		if self.orientation == Qt.Horizontal:
			return self.sizeOfContainer()
		else:
			return self.sizeOfButtons()

	def sizeHint(self):
		"""
		:rtype: QtCore.QSize
		"""
		width = 150
		height = ButtonContainer.Height
		if self._buttonCount == 0:
			height = 0
		if self.orientation == Qt.Horizontal:
			sizeHint = QtCore.QSize(width, height)
		else:
			sizeHint = QtCore.QSize(height, width)
		return sizeHint
