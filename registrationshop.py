#!/usr/bin/python

"""
Registrationshop

3D registration tool for medical purposes.

author: Berend Klein Haneveld
"""

import sys
try:
	from PySide import QtGui, QtCore
	from PySide.QtGui import *
except ImportError:
	raise ImportError("Could not import PySide")

from core.ProjectController import ProjectController
from UAHCore.UAHViewer.BaseViewer import *
from UAHCore.UAHViewer.slicer import *

# 'define' some strings
APPNAME = "Registrationshop"
ORGNAME = "TU Delft"
ORGDOMAIN = "tudelft.nl"
UIPACKAGE = "ui"
COREPACKAGE = "core"

ADD = lambda x, y: x + y
MAX = 2000

class RegistrationshopMainWindow(QtGui.QMainWindow):
	"""docstring for RegistrationshopMainWindow"""
	def __init__(self):
		super(RegistrationshopMainWindow, self).__init__()

		self._settings = QtCore.QSettings()
		self.setUnifiedTitleAndToolBarOnMac(True)
		self.projectController = ProjectController()
		self.initUI()


	def initUI(self):

		# Create another window in which two dock widgets will reside
		# so that the transformation dock widget can take the whole height
		# of the window
		self.mainWindow = QMainWindow()

		# Create 3 BaseViewer objects: main, fixed and moving
		self.mainViewer = BaseViewer(BaseViewer.TypeBasic)
		self.fixedViewer = BaseViewer(BaseViewer.TypeSlice)
		self.movingViewer = BaseViewer(BaseViewer.TypeSlice)

		self.mainViewer.setToolTip("Main view")
		self.fixedViewer.setToolTip("Fixed data set view")
		self.movingViewer.setToolTip("Moving data set view")


#		file1 = "/Users/beer/Dropbox/University/Registrationshop/Data/datasets/CT.mhd"
#		file2 = "/Users/beer/Dropbox/University/Registrationshop/Data/datasets/MRI.mhd"
#
#		self.imageReader1 = vtkMetaImageReader()
#		self.imageReader1.SetFileName(file1)
#		self.imageData = self.imageReader1.GetOutput() # vtkImageData
#
#		self.imageReader2 = vtkMetaImageReader()
#		self.imageReader2.SetFileName(file2)
#		self.imageData2 = self.imageReader2.GetOutput()
#
#		self.fixedSlicer = Slicer(self.fixedViewer.rwi, self.fixedViewer.ren)
#		self.fixedSlicer.set_input(self.imageData)
#		self.fixedSlicer.set_perspective()
#		self.fixedSlicer.reset_to_default_view(2)
#		self.fixedSlicer.reset_camera()
#
#		self.movingSlicer = Slicer(self.movingViewer.rwi, self.fixedViewer.ren)
#		self.movingSlicer.set_input(self.imageData2)
#		self.movingSlicer.set_perspective()
#		self.movingSlicer.reset_to_default_view(2)
#		self.movingSlicer.reset_camera()



#		self.imageMapper = vtkImageMapper()
#		self.imageMapper.SetInput(self.imageData)
#		self.imageActor = vtkActor2D()
#		self.imageActor.SetMapper(self.imageMapper)
#		self.baseViewer.ren.AddActor2D(self.imageActor)

		# TODO: saveState and loadState for saving dock stuff

		# If I want to sync them up: create a SyncSliceViewers object and add the slice viewers
		# sync = SyncSliceViewers(self.mainWindow)
		# sync.add_slice_viewer(self.viewer1)
		# sync.add_slice_viewer(self.viewer2)
		# sync.link()
		# And then connect the signals and slots of the slice viewers

		self.mainWindow.setCentralWidget(self.mainViewer)
		self.mainWindow.setWindowFlags(QtCore.Qt.Widget)
		self.setCentralWidget(self.mainWindow)

		# Toolbox on the left side of the window
		self.dockTransformations = QDockWidget()
		self.dockTransformations.setWindowTitle("Transformations")
		self.dockTransformations.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
		self.dockTransformations.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.dockTransformations.setHidden(self._settings.value(UIPACKAGE + "/transformationHidden", False))

		# Toolbox on the bottom of the window
		self.dockDataSets = QDockWidget()
		self.dockDataSets.setWindowTitle("Data sets")
		self.dockDataSets.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
		self.dockDataSets.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.dockDataSets.setHidden(self._settings.value(UIPACKAGE + "/dataSetsHidden", False))

		# Toolbox on the right side of the window
		self.dockVisualParameters = QDockWidget()
		self.dockVisualParameters.setWindowTitle("Visualization Parameters")
		self.dockVisualParameters.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
		self.dockVisualParameters.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.dockVisualParameters.setHidden(self._settings.value(UIPACKAGE + "/visualParametersHidden", False))

		self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockTransformations)
		self.mainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockVisualParameters)
		self.mainWindow.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockDataSets)

		# Create widgets for fixed and moving image data sets
#		self.movingWidget = QWidget()
#		self.changeColorOfWidget(self.movingWidget, QColor(50, 50, 50))
		loadTargetButton = QPushButton("Load moving data set", self.movingViewer)
		loadTargetButton.clicked.connect(self.loadMovingDataSet)

#		self.fixedWidget = QWidget()
#		self.changeColorOfWidget(self.fixedWidget, QColor(150, 150, 150))
		loadFixedButton = QPushButton("Load fixed data set", self.fixedViewer)
		loadFixedButton.clicked.connect(self.loadFixedDataSet)

		# Create a splitter area in order to provide some control
		self.dataSetsWidget = QSplitter()
		self.dataSetsWidget.setMinimumHeight(160)
		self.dataSetsWidget.addWidget(self.movingViewer)
		self.dataSetsWidget.addWidget(self.fixedViewer)

		self.dockDataSets.setWidget(self.dataSetsWidget)

		self.transformationWidget = QSplitter()
		self.transformationWidget.setOrientation(QtCore.Qt.Vertical)
		self.transformationWidget.setMinimumWidth(160)
		self.transformationWidget.addWidget(QTextEdit())
		self.transformationWidget.addWidget(QTextEdit())
		self.dockTransformations.setWidget(self.transformationWidget)

		self.visParameters = QListWidget()
		self.visParameters.setMinimumWidth(160)
		self.dockVisualParameters.setWidget(self.visParameters)

		# Create actions for the main window
#		self.createActions()
		# Create the menu structure
#		self.createMenus()

		# Create toolbar
		self.createPanelActions()
		self.createToolBar()

		# Main window size
		xPosition = self._settings.value(UIPACKAGE + "/window/origin/x", 0)
		yPosition = self._settings.value(UIPACKAGE + "/window/origin/y", 0)
		width = self._settings.value(UIPACKAGE + "/window/width", 800)
		height = self._settings.value(UIPACKAGE + "/window/height", 600)
		self.setGeometry(xPosition, yPosition, width, height)
		# TODO: make it failsafe with multiple screen setup

		self.setWindowTitle(APPNAME)

#		self.setWindowState(QtCore.Qt.WindowActive)
		self.raise_()
		self.show()

	def loadFixedDataSet(self):
		fileName, other = QFileDialog.getOpenFileName(self, "Open fixed data set", "", "Images (*.mhd)")
		if len(fileName) > 0:
			print "Name:", fileName
			self.projectController.loadFixedDataSet(fileName)

	def loadMovingDataSet(self):
		fileName, other = QFileDialog.getOpenFileName(self, "Open moving data set", "", "Images (*.mhd)")
		if len(fileName) > 0:
			print "Name:", fileName
			self.projectController.loadMovingDataSet(fileName)


	def resizeEvent(self, ev):
		"""
		@type ev: QResizeEvent
		"""
		width = self.width()
		height = self.height()

		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		self._settings.setValue(UIPACKAGE + "/window/origin/x", xPosition)
		self._settings.setValue(UIPACKAGE + "/window/origin/y", yPosition)
		self._settings.setValue(UIPACKAGE + "/window/width", width)
		self._settings.setValue(UIPACKAGE + "/window/height", height)

	def moveEvent(self, ev):
		"""
		@type ev: QMoveEvent
		"""
		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		self._settings.setValue(UIPACKAGE + "/window/origin/x", xPosition)
		self._settings.setValue(UIPACKAGE + "/window/origin/y", yPosition)

	# Kind of overidden?
	def closeEvent(self, event):
#		reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure you want to quit?",
#										   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

#		if reply == QtGui.QMessageBox.Yes:
#			event.accept()
#		else:
#			event.ignore()
#		print "Quit the application"
		pass

	def changeColorOfWidget(self, widget, color):
		"""
		Changes the background color of the provided widget.

		@type widget: QWidget
		@type color: QColor
		"""
		widget.setAutoFillBackground(True)
		palette = widget.palette()
		palette.setColor(widget.backgroundRole(), color)
		widget.setPalette(palette)

	def createMenus(self):
		# Add menu's
		self.menuBar = QtGui.QMenuBar()

		# File menu
		self.menuItemFile = self.menuBar.addMenu("&File")
		self.menuItemFile.addAction(self.newProjectAction)
		self.menuItemFile.addSeparator()
		self.menuItemFile.addAction(self.openProjectAction)
		self.menuItemFile.addAction(self.openRecentAction)
		self.menuItemFile.addSeparator()
		self.menuItemFile.addAction(self.saveProjectAction)
		self.menuItemFile.addAction(self.saveAsProjectAction)
#		self.menuItemFile.addAction(self.exitAction)

		# Edit menu
		self.menuItemEdit = self.menuBar.addMenu("&Edit")

	def createActions(self):
		self.exitAction = QtGui.QAction('&Exit', self, shortcut='Ctrl+Q')
		self.newProjectAction = QtGui.QAction('&New', self, shortcut='Ctrl+N')
		self.newProjectAction.triggered.connect(self.someFunction)

		self.openProjectAction = QtGui.QAction('&Open...', self, shortcut='Ctrl+O')
		self.openProjectAction.triggered.connect(self.someFunction)
		self.openRecentAction = QtGui.QAction('&Open Recent', self)
		self.openRecentAction.setDisabled(True)

		self.saveProjectAction = QtGui.QAction('&Save', self, shortcut='Ctrl+S')
		self.saveProjectAction.triggered.connect(self.someFunction)

		self.saveAsProjectAction = QtGui.QAction('&Save As...', self, shortcut='Ctrl+Shift+S')
		self.saveAsProjectAction.triggered.connect(self.someFunction)
#		self.exitAction. ='Quit the application', triggered=self.close())


	def createToolBar(self):
		# Add toolbar
		self.toolbar = self.addToolBar('Main tools')

		# Add the toolbar actions
		self.toolbar.addSeparator()
		self.toolbar.addAction(self.toggleLeftBar)
		self.toolbar.addAction(self.toggleBottomBar)
		self.toolbar.addAction(self.toggleRightBar)

	def createPanelActions(self):
		self.toggleLeftBar = QtGui.QAction('&Toggle left bar', self, shortcut='Ctrl+0')
		self.toggleLeftBar.setIcon(QIcon('resources/images/ToolbarLeft.png'))
		self.toggleLeftBar.triggered.connect(self.toggleSidePanel)
		self.toggleLeftBar.setCheckable(True)
		self.toggleLeftBar.setChecked(not(self.dockTransformations.isHidden()))

		self.toggleRightBar = QtGui.QAction('&Toggle right bar', self, shortcut='Ctrl+Alt+0')
		self.toggleRightBar.setIcon(QIcon('resources/images/ToolbarRight.png'))
		self.toggleRightBar.triggered.connect(self.toggleRightSidePanel)
		self.toggleRightBar.setCheckable(True)
		self.toggleRightBar.setChecked(not(self.dockVisualParameters.isHidden()))

		self.toggleBottomBar = QtGui.QAction('&Toggle bottom bar', self, shortcut='Ctrl+Shift+0')
		self.toggleBottomBar.setIcon(QIcon('resources/images/ToolbarBottom.png'))
		self.toggleBottomBar.triggered.connect(self.toggleBottomPanel)
		self.toggleBottomBar.setCheckable(True)
		self.toggleBottomBar.setChecked(not(self.dockDataSets.isHidden()))

	# TODO: find out how to make 1 general function for this (maybe tags or something)
	def toggleSidePanel(self):
		self.dockTransformations.setHidden(not(self.dockTransformations.isHidden()))
		self._settings.setValue(UIPACKAGE + "/transformationHidden", self.dockTransformations.isHidden())

	def toggleRightSidePanel(self):
		self.dockVisualParameters.setHidden(not(self.dockVisualParameters.isHidden()))
		self._settings.setValue(UIPACKAGE + "/visualParametersHidden", self.dockVisualParameters.isHidden())

	def toggleBottomPanel(self):
		self.dockDataSets.setHidden(not(self.dockDataSets.isHidden()))
		self._settings.setValue(UIPACKAGE + "/dataSetsHidden", self.dockDataSets.isHidden())

def main():

	app = QtGui.QApplication(sys.argv)
	app.setObjectName(APPNAME)
	app.setApplicationName(APPNAME)
	app.setOrganizationName(ORGNAME)
	app.setOrganizationDomain(ORGDOMAIN)

	mainWindow = RegistrationshopMainWindow()
	sys.exit(app.exec_())
	

if __name__ == '__main__':
	main()