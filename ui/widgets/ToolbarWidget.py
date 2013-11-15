"""
ToolbarWidget

:Authors:
	Berend Klein Haneveld
"""
import sys
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QToolButton
from PySide.QtGui import QPushButton
from PySide.QtGui import QMainWindow
from PySide.QtGui import QFont
from PySide.QtGui import QAction
from PySide.QtGui import QSizePolicy
from PySide.QtGui import QIcon
from PySide.QtCore import Qt
from PySide.QtCore import QSize


class ToolbarWidget(QWidget):
	"""
	ToolbarWidget
	"""

	def __init__(self):
		super(ToolbarWidget, self).__init__()

		# Make sure the widget expands over the whole toolbar
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		# Create main layout that will contain the layouts for each section
		self.mainLayout = QHBoxLayout()
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout.setSpacing(0)

		# Layout on the left side
		self.leftLayout = QHBoxLayout()
		self.leftLayout.setContentsMargins(0, 0, 0, 0)
		self.leftLayout.setSpacing(0)
		self.leftLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

		# Layout in the center
		self.centerLayout = QHBoxLayout()
		self.centerLayout.setContentsMargins(0, 0, 0, 0)
		self.centerLayout.setSpacing(0)
		self.centerLayout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

		# Layout on the right side
		self.rightLayout = QHBoxLayout()
		self.rightLayout.setContentsMargins(0, 0, 0, 0)
		self.rightLayout.setSpacing(0)
		self.rightLayout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

		self.setLayout(self.mainLayout)

		self.leftWidget = QWidget()
		self.leftWidget.setLayout(self.leftLayout)
		self.centerWidget = QWidget()
		self.centerWidget.setLayout(self.centerLayout)
		self.rightWidget = QWidget()
		self.rightWidget.setLayout(self.rightLayout)

		self.mainLayout.addWidget(self.leftWidget)
		self.mainLayout.addWidget(self.centerWidget)
		self.mainLayout.addWidget(self.rightWidget)

	def setText(self, text):
		self.label.setText(text)

	def addActionLeft(self, action):
		toolButton = CreateFlatButton(action)
		self.addLeftItem(toolButton)

	def addActionCenter(self, action):
		toolButton = CreateFlatButton(action)
		self.addCenterItem(toolButton)

	def addActionRight(self, action):
		toolButton = CreateFlatButton(action)
		self.addRightItem(toolButton)

	def addLeftItem(self, widget):
		self.leftLayout.addWidget(widget)

	def addCenterItem(self, widget):
		self.centerLayout.addWidget(widget)

	def addRightItem(self, widget):
		self.rightLayout.addWidget(widget)


def CreateFlatButton(action):
	"""
	Create a custom flat button and style
	it so that it will look good on all platforms.
	"""

	toolButton = QToolButton()
	toolButton.setIcon(action.icon())
	toolButton.setText(action.text())
	toolButton.setAutoRaise(True)
	toolButton.setIconSize(QSize(32, 32))
	toolButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
	if sys.platform.startswith('darwin'):
		# Bug for Mac: QToolButtons do not react to setAutoRaise so
		# can't be made flat when they are not used inside a toolbar.
		# Setting a custom style sheet with border to none fixes this.
		# But then it looses all its highlight and pressed visual cues
		# so some extra styling needs to be done to provide some nice
		# visual feedback on hover and pressed states.
		toolButton.setStyleSheet("QToolButton {"
			"border: none;"
			"} "
			"QToolButton:hover {"
			"background-color: qradialgradient(cx: 0.5, cy: 0.5,"
			"fx: 0.5, fy: 0.5,"
			"radius: 0.5, "
			"stop: 0 rgba(255, 255, 255, 100), "
			"stop: 1 rgba(0, 0, 0, 0));"
			"}"
			"QToolButton:pressed {"
			"background-color: qradialgradient(cx: 0.5, cy: 0.5,"
			"fx: 0.5, fy: 0.5,"
			"radius: 0.5, "
			"stop: 0 rgba(255, 255, 255, 200), "
			"stop: 1 rgba(0, 0, 0, 0));"
			"}")
	font = QFont()
	font.setPixelSize(10)
	toolButton.setFont(font)

	# Connect the clicked signal to the action trigger
	def pushed():
		toolButton.action.triggered.emit()
	setattr(toolButton, "pushed", pushed)
	toolButton.clicked.connect(toolButton.pushed)
	setattr(toolButton, "action", action)

	return toolButton


if __name__ == '__main__':
	import os
	from PySide.QtGui import QApplication
	from PySide.QtGui import QVBoxLayout

	app = QApplication([])
	mainWindow = QMainWindow()
	mainWindow.setUnifiedTitleAndToolBarOnMac(True)
	toolbar = mainWindow.addToolBar("Main")
	toolbar.setMovable(False)

	dirPath = os.path.dirname(__file__)
	basePath = os.path.join(dirPath, "../../resources/images/")
	icon = QIcon(basePath + "UserTransformButton.png")

	toolButtonLeft1 = CreateFlatButton(QAction(icon, "Left", mainWindow))
	toolButtonLeft2 = CreateFlatButton(QAction(icon, "2nd left", mainWindow))
	toolButtonRight = CreateFlatButton(QAction(icon, "Right", mainWindow))

	toolButtonCenter = QPushButton()
	toolButtonCenter.setIcon(QIcon(basePath + "LandmarkTransformButton.png"))
	toolButtonCenter.setText("Center")
	toolButtonCenter.setMinimumWidth(200)

	barWidget = ToolbarWidget()

	barWidget.addLeftItem(toolButtonLeft1)
	barWidget.addLeftItem(toolButtonLeft2)
	barWidget.addCenterItem(toolButtonCenter)
	barWidget.addRightItem(toolButtonRight)
	toolbar.addWidget(barWidget)

	layout = QVBoxLayout()
	layout.setSpacing(0)
	layout.setContentsMargins(0, 0, 0, 0)
	layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
	layout.addWidget(QLabel("Test toolbar widget"))

	widget = QWidget()
	widget.setLayout(layout)

	mainWindow.setCentralWidget(widget)
	mainWindow.setGeometry(100, 100, 500, 300)
	mainWindow.show()
	app.exec_()
