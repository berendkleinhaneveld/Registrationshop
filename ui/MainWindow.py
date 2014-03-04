"""
MainWindow.py
"""

from PySide.QtGui import QMainWindow
from PySide import QtCore


class MainWindow(QMainWindow):
	"""
	Simple base class to start of other applications or tools.
	Has some methods that keep track of size and location of
	window.
	"""

	# Singletons
	settings = QtCore.QSettings()

	def __init__(self, args):
		super(MainWindow, self).__init__()
		self.args = args
		self._storesSizeAndPosition = True

	def restoreState(self):
		"""
		Restores the window size and position of the last time the
		application was run. If the application is started for the first time
		it applies some 'sane' initial values.
		"""
		if not self._storesSizeAndPosition:
			return
			
		xPosition = int(MainWindow.settings.value("ui/window/origin/x", 5))
		yPosition = int(MainWindow.settings.value("ui/window/origin/y", 20))
		width = int(MainWindow.settings.value("ui/window/width", 800))
		height = int(MainWindow.settings.value("ui/window/height", 600))

		self.setGeometry(xPosition, yPosition, width, height)

	# Events

	def resizeEvent(self, event):
		"""
		Saves the size and position of the window when it is resized so that
		it can be restored on subsequent launches.

		:param event: Resize event
		:type event: QResizeEvent
		"""
		if not self._storesSizeAndPosition:
			return

		width = self.width()
		height = self.height()

		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		MainWindow.settings.setValue("ui/window/origin/x", xPosition)
		MainWindow.settings.setValue("ui/window/origin/y", yPosition)
		MainWindow.settings.setValue("ui/window/width", width)
		MainWindow.settings.setValue("ui/window/height", height)

	def moveEvent(self, event):
		"""
		Saves the position of the window when it is moved so that it can be
		restored on subsequent launches.

		:param event: Move event
		:type event: QMoveEvent
		"""
		if not self._storesSizeAndPosition:
			return

		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		MainWindow.settings.setValue("ui/window/origin/x", xPosition)
		MainWindow.settings.setValue("ui/window/origin/y", yPosition)

	def closeEvent(self, event):
		"""
		:param event: Close event
		:type event: QCloseEvent
		"""
		pass
