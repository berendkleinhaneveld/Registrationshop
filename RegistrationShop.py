#!/usr/bin/python
"""
Registrationshop
	
3D registration tool for medical purposes.
	
@author: Berend Klein Haneveld 2013
"""

import sys
import os.path
try:
	from PySide import QtCore
	from PySide.QtCore import Qt
	from PySide.QtGui import QMainWindow
	from PySide.QtGui import QApplication
	from PySide.QtGui import QDockWidget
	from PySide.QtGui import QAction
	from PySide.QtGui import QIcon
	from PySide.QtGui import QFileDialog
	from PySide.QtGui import QMenuBar
	from PySide.QtGui import QProgressBar
	from PySide.QtGui import QWidget
	from PySide.QtGui import QSizePolicy
except ImportError, e:
	raise e

# Import ui elements
from core.AppVars import AppVars
from core.ProjectController import ProjectController
from ui.TransformationWidget import TransformationWidget
from ui.VisualizationParametersWidget import VisualizationParametersWidget
from ui.DataSetsWidget import DataSetsWidget
from ui.SlicerWidget import SlicerWidget
from ui.ParameterWidget import ParameterWidget

# Define settings parameters
APPNAME = "RegistrationShop"
ORGNAME = "TU Delft"
ORGDOMAIN = "tudelft.nl"

class RegistrationShop(QMainWindow):
	"""
	Main class that starts up the application.
	Creates UI and starts project/plugin managers.
	"""
	# Singletons
	settings = QtCore.QSettings()

	def __init__(self, arg):
		"""
		Sets app specific properties.
		Initializes the UI.
		"""
		super(RegistrationShop, self).__init__()
		self.arg = arg
		self.setApplicationPath()
		# Make sure there is a project controller instance
		ProjectController.Instance()

		# Initialize the user interface
		self.initUI()
		
		lastProject = RegistrationShop.settings.value("project/lastProject", None)
		if lastProject:
			# Open the last saved project
			self.openProject(lastProject)
		
		pass

	# UI setup methods

	def initUI(self):
		"""
		Initializes the UI. Makes sure previous state of
		application is restored.
		"""
		# Create actions and elements
		self.createElements()
		self.createActions()
		self.createMenus()
		self.createToolbar()
		self.restoreState()

		# Set some window/application properties
		self.setUnifiedTitleAndToolBarOnMac(True)
		self.setWindowTitle(APPNAME)
		self.setWindowState(Qt.WindowActive)
		self.raise_()
		self.show()
		pass

	def createElements(self):
		"""
		Creates the widgets and docks of which the 
		main window is composed.
		"""
		self.mainSlicer = SlicerWidget("Registration results data set")
		self.mainSlicer.setShowsActionBar(False)
		ProjectController.Instance().changedResultsDataSetFileName.connect(self.mainSlicer.setFileName)

		# Initialize the main window
		self.mainWindow = QMainWindow()
		self.mainWindow.setCentralWidget(self.mainSlicer)
		self.mainWindow.setWindowFlags(Qt.Widget)
		self.setCentralWidget(self.mainWindow)
		
		# Toolbox on the left side of the window
		self.dockTransformations = QDockWidget()
		self.dockTransformations.setWindowTitle("Transformations")
		self.dockTransformations.setAllowedAreas(Qt.AllDockWidgetAreas)
		self.dockTransformations.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.dockTransformations.setHidden(RegistrationShop.settings.value("ui/dock/transformation/hidden", False))

		self.dockParameters = QDockWidget()
		self.dockParameters.setWindowTitle("Parameters")
		self.dockParameters.setAllowedAreas(Qt.AllDockWidgetAreas)
		self.dockParameters.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.dockParameters.setHidden(RegistrationShop.settings.value("ui/dock/transformation/hidden", False))
		
		# Toolbox on the bottom of the window
		self.dockDataSets = QDockWidget()
		self.dockDataSets.setWindowTitle("Data sets")
		self.dockDataSets.setAllowedAreas(Qt.AllDockWidgetAreas)
		self.dockDataSets.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.dockDataSets.setHidden(RegistrationShop.settings.value("ui/dock/dataSets/hidden", False))
		
		# Toolbox on the right side of the window
		self.dockVisualParameters = QDockWidget()
		self.dockVisualParameters.setWindowTitle("Visualization Parameters")
		self.dockVisualParameters.setAllowedAreas(Qt.AllDockWidgetAreas)
		self.dockVisualParameters.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.dockVisualParameters.setHidden(RegistrationShop.settings.value("ui/dock/visualParameters/hidden", False))
		
		# Add the dock widgets to their main windows. The one of the left is added to
		# the top most 'main window' so that it stretches out across the whole left side
		self.addDockWidget(Qt.LeftDockWidgetArea, self.dockTransformations)
		self.addDockWidget(Qt.LeftDockWidgetArea, self.dockParameters)
		self.mainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockVisualParameters)
		self.mainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockDataSets)
		
		# Create the dock widgets
		self.transformationWidget = TransformationWidget()
		self.parameterWidget = ParameterWidget()
		self.visualizationParamWidget = VisualizationParametersWidget()
		self.dataSetsWidget = DataSetsWidget()
		
		# Assign the dock widgets to their docks
		self.dockTransformations.setWidget(self.transformationWidget)
		self.dockParameters.setWidget(self.parameterWidget)
		self.dockVisualParameters.setWidget(self.visualizationParamWidget)
		self.dockDataSets.setWidget(self.dataSetsWidget)

		# TODO: this doesn't look good: way too deep...
		self.transformationWidget.transformationsView.selectedTransformation.connect(
			self.parameterWidget.parameterModel.setTransformation)
		
		# Create statusbar and hide it immediately
		self.progressbar = QProgressBar()
		self.progressbar.setRange(0, 0)
		self.progressbar.setHidden(True)

		self.statusbar = self.statusBar()
		self.statusbar.setHidden(True)
		self.statusbar.addWidget(self.progressbar)

		pass

	def createActions(self):
		"""
		Create actions that can be attached to buttons and menus.
		"""
		# Dock toggle actions
		self.actionToggleLeftBar = QAction('Toggle left bar', self, shortcut='Ctrl+0')
		self.actionToggleLeftBar.setIcon(QIcon(AppVars.imagePath() + 'ToolbarLeft.png'))
		self.actionToggleLeftBar.triggered.connect(self.toggleLeftSidePanel)
		self.actionToggleLeftBar.setCheckable(True)
		self.actionToggleLeftBar.setChecked(not(self.dockTransformations.isHidden()))
		
		self.actionToggleRightBar = QAction('Toggle right bar', self, shortcut='Ctrl+Alt+0')
		self.actionToggleRightBar.setIcon(QIcon(AppVars.imagePath() + 'ToolbarRight.png'))
		self.actionToggleRightBar.triggered.connect(self.toggleRightSidePanel)
		self.actionToggleRightBar.setCheckable(True)
		self.actionToggleRightBar.setChecked(not(self.dockVisualParameters.isHidden()))

		self.actionToggleBottomBar = QAction('Toggle bottom bar', self, shortcut='Ctrl+Shift+0')
		self.actionToggleBottomBar.setIcon(QIcon(AppVars.imagePath() + 'ToolbarBottom.png'))
		self.actionToggleBottomBar.triggered.connect(self.toggleBottomPanel)
		self.actionToggleBottomBar.setCheckable(True)
		self.actionToggleBottomBar.setChecked(not(self.dockDataSets.isHidden()))

		self.actionLoadFixedData = QAction('Load fixed data', self, shortcut='Ctrl+Shift+F')
		# self.actionLoadFixedData.setIcon(QIcon(AppVars.imagePath() + 'AddButton.png'))
		self.actionLoadFixedData.triggered.connect(self.loadFixedDataSetFile)

		self.actionLoadMovingData = QAction('Load moving data', self, shortcut='Ctrl+Shift+M')
		# self.actionLoadMovingData.setIcon(QIcon(AppVars.imagePath() + 'AddButton.png'))
		self.actionLoadMovingData.triggered.connect(self.loadMovingDataSetFile)

		self.actionSaveProject = QAction('Save', self, shortcut='Ctrl+S')
		self.actionSaveProject.triggered.connect(self.saveProject)

		self.actionSaveProjectAs = QAction('Save as...', self, shortcut='Ctrl+Shift+S')
		self.actionSaveProjectAs.triggered.connect(self.saveProjectAs)

		self.actionOpenProject = QAction('Open...', self, shortcut='Ctrl+O')
		self.actionOpenProject.triggered.connect(self.openProject)

		self.actionNewProject = QAction('New', self, shortcut='Ctrl+N')
		self.actionNewProject.triggered.connect(self.newProject)

		self.actionRegister = QAction('Register', self, shortcut='Ctrl+R')
		self.actionRegister.triggered.connect(self.register)

		pass

	def createMenus(self):
		"""
		Creates menus from actions.
		"""
		self.menuBar = QMenuBar()
		self.menuItemFile = self.menuBar.addMenu('&File')
		self.menuItemFile.addAction(self.actionNewProject)
		self.menuItemFile.addAction(self.actionOpenProject)
		# TODO: Open recent >
		self.menuItemFile.addAction(self.actionSaveProject)
		self.menuItemFile.addAction(self.actionSaveProjectAs)

		self.menuItemProject = self.menuBar.addMenu('&Project')
		self.menuItemProject.addAction(self.actionLoadFixedData)
		self.menuItemProject.addAction(self.actionLoadMovingData)
		self.menuItemProject.addSeparator()
		self.menuItemProject.addAction(self.actionRegister)
		# self.menuItemProject.addSeparator()

		pass

	def createToolbar(self):
		"""
		Creates the main toolbar and sets the toolbar buttons.
		"""
		# Add toolbar
		self.toolbar = self.addToolBar('Main tools')
		
		# Add the toolbar actions

		# Align the dock buttons to the right with a spacer widget
		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.toolbar.addWidget(spacer)
		# Add the dock buttons to the toolbar
		self.toolbar.addAction(self.actionToggleLeftBar)
		self.toolbar.addAction(self.actionToggleBottomBar)
		self.toolbar.addAction(self.actionToggleRightBar)
		# TODO: add don't panic button
		pass

	def restoreState(self):
		"""
		Restores the window size and position of the last time the
		application was run. If the application is started for the first time
		it applies some 'sane' initial values.
		"""
		xPosition 	= int(RegistrationShop.settings.value("ui/window/origin/x", 0))
		yPosition 	= int(RegistrationShop.settings.value("ui/window/origin/y", 0))
		width 		= int(RegistrationShop.settings.value("ui/window/width", 800))
		height 		= int(RegistrationShop.settings.value("ui/window/height", 600))

		self.setGeometry(xPosition, yPosition, width, height)
		pass

	# Events 

	def resizeEvent(self, ev):
		"""
		Saves the size and position of the window when it is resized so that
		it can be restored on subsequent launches.

		@type ev: QResizeEvent
		"""
		width 	= self.width()
		height 	= self.height()

		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		RegistrationShop.settings.setValue("ui/window/origin/x", xPosition)
		RegistrationShop.settings.setValue("ui/window/origin/y", yPosition)
		RegistrationShop.settings.setValue("ui/window/width", width)
		RegistrationShop.settings.setValue("ui/window/height", height)

	def moveEvent(self, ev):
		"""
		Saves the position of the window when it is moved so that it can be 
		restored on subsequent launches.

		@type ev: QMoveEvent
		"""
		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		RegistrationShop.settings.setValue("ui/window/origin/x", xPosition)
		RegistrationShop.settings.setValue("ui/window/origin/y", yPosition)

	def closeEvent(self, ev):
		"""
		TODO: ask if app should really quit.
		@type ev: QCloseEvent
		"""
		pass
	
	# Private Functions
	def setApplicationPath(self):
		"""
		Tries to find the path to the application. This is done so that it
		can figure out where certain resources are located. 
		QCoreApplication::applicationDirPath() on OS X does not return the 
		desired path to the actual application but to the python executable 
		in /Library/FrameWorks. This is inconvenient because images can't be
		located that way.
		This method assumes that the application path is passed on to arg[0].
		Otherwise it will not set a path and will depend that the image's relative
		paths will work.
		"""
		# Check to see if we can deduce the application path from the
		# sys arguments
		if isinstance(self.arg[0], basestring) and self.arg[0].endswith("RegistrationShop.py"):
			# Assume that first argument is the entry point
			path = self.arg[0]
			# Find index of the application name
			start = path.rfind("RegistrationShop.py")
			if start > -1:
				AppVars.setPath(path[:start])
		pass

	# Action callbacks
	
	def toggleLeftSidePanel(self):
		"""
		Toggles the visibility of the transformation panel on the left. Makes sure that
		the state of the toolbar button is updated and saves the state in the settings.
		"""
		self.dockTransformations.setHidden(not(self.dockTransformations.isHidden()))
		self.dockParameters.setHidden(self.dockTransformations.isHidden())
		self.actionToggleLeftBar.setChecked(not(self.dockTransformations.isHidden()))
		RegistrationShop.settings.setValue("ui/dock/transformation/hidden", self.dockTransformations.isHidden())
		pass
	
	def toggleRightSidePanel(self):
		"""
		Toggles the visibility of the visualization parameters panel on the right. Makes sure that
		the state of the toolbar button is updated and saves the state in the settings.
		"""
		self.dockVisualParameters.setHidden(not(self.dockVisualParameters.isHidden()))
		self.actionToggleRightBar.setChecked(not(self.dockVisualParameters.isHidden()))
		RegistrationShop.settings.setValue("ui/dock/visualParameters/hidden", self.dockVisualParameters.isHidden())
		pass
	
	def toggleBottomPanel(self):
		"""
		Toggles the visibility of the datasets panel on the bottom. Makes sure that
		the state of the toolbar button is updated and saves the state in the settings.
		"""
		self.dockDataSets.setHidden(not(self.dockDataSets.isHidden()))
		self.actionToggleBottomBar.setChecked(not(self.dockDataSets.isHidden()))
		RegistrationShop.settings.setValue("ui/dock/dataSets/hidden", self.dockDataSets.isHidden())
		pass

	def loadFixedDataSetFile(self):
		"""
		Open file dialog to search for data files. If valid data is given, it will
		pass the data file location on to the slicer and the project controller.
		"""
		fileName, other = QFileDialog.getOpenFileName(self, "Open fixed data set", "", "Images (*.mhd *.vti)")
		if len(fileName) > 0:
			projectController = ProjectController.Instance()
			projectController.loadFixedDataSet(fileName)
		pass

	def loadMovingDataSetFile(self):
		"""
		Open file dialog to search for data files. If valid data is given, it will
		pass the data file location on to the slicer and the project controller.
		"""
		fileName, other = QFileDialog.getOpenFileName(self, "Open moving data set", "", "Images (*.mhd *.vti)")
		if len(fileName) > 0:
			projectController = ProjectController.Instance()
			projectController.loadMovingDataSet(fileName)
		pass

	def saveProject(self):
		"""
		Save the project to the specified name in the current project. If no name
		is specified, then 'save project as' is called.
		"""
		projCont = ProjectController.Instance()
		
		if projCont.currentProject().name() is not None:
			# Save that project
			print "Save project at", projCont.currentProject().name()
			saved = projCont.saveProject()
			if saved:
				# Save it in the settings that this was the last opened project
				RegistrationShop.settings.setValue("project/lastProject", projCont.currentProject().name())
		else:
			self.saveProjectAs()

	def saveProjectAs(self):
		"""
		Opens a file dialog so that the user can select a folder
		in which to save the project.
		"""
		# Open file dialog
		fileName = QFileDialog.getExistingDirectory(self, "Select project folder", "", QFileDialog.ShowDirsOnly)
		if len(fileName) > 0:
			# TODO: check for existing project!

			# Set filename of project
			ProjectController.Instance().currentProject().setName(fileName)
			# Call save project
			self.saveProject()

		pass

	def openProject(self, projectName=None):
		"""
		If no project name is supplied, it will open a file dialog so 
		that the user can select a project file
		or project folder.
		"""
		fileName = ""
		if projectName:
			fileName = projectName
		else:
			fileName = QFileDialog.getExistingDirectory(self, "Open project", "", QFileDialog.ShowDirsOnly)
		
		if len(fileName) > 0:
			fullName = fileName + ProjectController.Instance().ProjectFile
			if os.path.isfile(fullName):
				loaded = ProjectController.Instance().loadProject(fileName)
				if loaded:
					RegistrationShop.settings.setValue("project/lastProject", fileName)
			else:
				print "Project file does not exist"
		pass

	def newProject(self):
		"""
		Create new project by calling the project controller
		"""
		ProjectController.Instance().newProject()
		pass

	def register(self):
		"""
		Temporary method to test if registration works...
		"""
		# self.statusbar.setHidden(False)
		# self.progressbar.setHidden(False)

		ProjectController.Instance().register()
		
		# self.statusbar.setHidden(True)
		# self.progressbar.setHidden(True)
		pass

def main():
	app = QApplication(sys.argv)
	app.setObjectName(APPNAME)
	app.setApplicationName(APPNAME)
	app.setOrganizationName(ORGNAME)
	app.setOrganizationDomain(ORGDOMAIN)

	mainWindow = RegistrationShop(sys.argv)
	sys.exit(app.exec_())
		
if __name__ == '__main__':
	main()
