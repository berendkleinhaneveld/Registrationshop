#!/usr/bin/python
"""
Registrationshop
	
3D registration tool for medical purposes.
	
:Authors:
	Berend Klein Haneveld 2013
"""

import sys
import os.path

# PySide stuff
from PySide import QtCore
from PySide.QtGui import QMainWindow
from PySide.QtGui import QApplication
from PySide.QtGui import QAction
from PySide.QtGui import QIcon
from PySide.QtGui import QFileDialog
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QMenuBar
from PySide.QtGui import QWidget
from PySide.QtGui import QSizePolicy
from PySide.QtGui import QSplitter
from PySide.QtCore import Qt
from PySide.QtCore import Slot

# Import core stuff
from core.AppVars import AppVars
from core.project.ProjectController import ProjectController
from core.data.DataReader import DataReader
from core.AppResources import AppResources
# Import ui elements
from ui.widgets.RenderWidget import RenderWidget
from ui.widgets.MultiRenderWidget import MultiRenderWidget
from ui.widgets.TitleWidget import TitleWidget
from ui.widgets.RenderPropertyWidgets import RenderPropWidget
from ui.widgets.RenderPropertyWidgets import ResultPropWidget

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
			# TODO: when opening last project failed, remove from settings

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

	def createElements(self):
		"""
		Creates the widgets and docks of which the 
		main window is composed.
		"""
		self.mainWindow = QMainWindow()

		# Render widgets
		self.fixedDataWidget = RenderWidget()
		self.resultDataWidget = MultiRenderWidget()
		self.movingDataWidget = RenderWidget()

		# Render properties widgets
		spLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		spLeft.setHorizontalStretch(1)

		projectController = ProjectController.Instance()

		self.fixedPropWidget = RenderPropWidget(self.fixedDataWidget, parent=self)
		self.fixedPropWidget.setSizePolicy(spLeft)
		self.fixedPropWidget.setFileChangedSignal(projectController.changedFixedData)
		self.fixedPropWidget.setLoadDataSlot(self.loadFixedDataSetFile)

		self.resultPropWidget = ResultPropWidget(self)
		self.resultPropWidget.setSizePolicy(spLeft)

		self.movingPropWidget = RenderPropWidget(self.movingDataWidget, parent=self)
		self.movingPropWidget.setSizePolicy(spLeft)
		self.movingPropWidget.setFileChangedSignal(projectController.changedMovingData)
		self.movingPropWidget.setLoadDataSlot(self.loadMovingDataSetFile)

		projectController.changedFixedData.connect(self.fixedDataWidget.loadFile)
		projectController.changedMovingData.connect(self.movingDataWidget.loadFile)

		self.verticalSplitter = QSplitter()
		self.verticalSplitter.setOrientation(Qt.Vertical)

		fixedDataTitleWidget = TitleWidget("Fixed data")
		resultDataTitleWidget = TitleWidget("Mix / Result")#, border=True)
		movingDataTitleWidget = TitleWidget("Moving data")

		titleBoxLayout = QHBoxLayout()
		titleBoxLayout.setSpacing(0)
		titleBoxLayout.setContentsMargins(0, 0, 0, 0)
		titleBoxLayout.addWidget(fixedDataTitleWidget)
		titleBoxLayout.addWidget(resultDataTitleWidget)
		titleBoxLayout.addWidget(movingDataTitleWidget)

		titleBoxWidget = QWidget()
		titleBoxWidget.setLayout(titleBoxLayout)

		rendersLayout = QHBoxLayout()
		rendersLayout.setSpacing(1)
		rendersLayout.setContentsMargins(0, 0, 0, 0)
		rendersLayout.addWidget(self.fixedDataWidget)
		rendersLayout.addWidget(self.resultDataWidget)
		rendersLayout.addWidget(self.movingDataWidget)

		propsLayout = QHBoxLayout()
		propsLayout.setSpacing(1)
		propsLayout.setContentsMargins(0, 0, 0, 0)
		propsLayout.addWidget(self.fixedPropWidget)
		propsLayout.addWidget(self.resultPropWidget)
		propsLayout.addWidget(self.movingPropWidget)

		rendersWidget = QWidget()
		rendersWidget.setLayout(rendersLayout)
		
		rendersAndTitlesLayout = QVBoxLayout()
		rendersAndTitlesLayout.setSpacing(0)
		rendersAndTitlesLayout.setContentsMargins(0, 0, 0, 0)
		rendersAndTitlesLayout.addWidget(titleBoxWidget)
		rendersAndTitlesLayout.addWidget(rendersWidget)

		rendersAndTitlesWidget = QWidget()
		rendersAndTitlesWidget.setLayout(rendersAndTitlesLayout)

		propsWidget = QWidget()
		propsWidget.setMaximumHeight(300)
		propsWidget.setMinimumHeight(300)
		propsWidget.setLayout(propsLayout)

		self.verticalSplitter.addWidget(rendersAndTitlesWidget)
		self.verticalSplitter.addWidget(propsWidget)
		self.setCentralWidget(self.verticalSplitter)

	def createActions(self):
		"""
		Create actions that can be attached to buttons and menus.
		"""
		userTransformIconName = AppResources.imageNamed('UserTransformButton.png')
		landmarkTransformIconName = AppResources.imageNamed('LandmarkTransformButton.png')
		deformableTransformIconName = AppResources.imageNamed('DeformableTransformButton.png')

		# Dock toggle actions
		self.actionFreeTransformTool = QAction('Free transform', self, shortcut='Ctrl+1')
		self.actionFreeTransformTool.setIcon(QIcon(userTransformIconName))
		self.actionFreeTransformTool.triggered.connect(self.addFreeTransform)
		
		self.actionLandmarkTransformTool = QAction('Landmark transform', self, shortcut='Ctrl+2')
		self.actionLandmarkTransformTool.setIcon(QIcon(landmarkTransformIconName))
		self.actionLandmarkTransformTool.triggered.connect(self.addLandmarkTransform)

		self.actionDeformableTransformTool = QAction('Deformable transform', self, shortcut='Ctrl+3')
		self.actionDeformableTransformTool.setIcon(QIcon(deformableTransformIconName))
		self.actionDeformableTransformTool.triggered.connect(self.addDeformableTransform)

		self.actionLoadFixedData = QAction('Load fixed data', self, shortcut='Ctrl+Shift+F')
		self.actionLoadFixedData.triggered.connect(self.loadFixedDataSetFile)

		self.actionLoadMovingData = QAction('Load moving data', self, shortcut='Ctrl+Shift+M')
		self.actionLoadMovingData.triggered.connect(self.loadMovingDataSetFile)

		self.actionSaveProject = QAction('Save project', self, shortcut='Ctrl+S')
		self.actionSaveProject.triggered.connect(self.saveProject)

		self.actionSaveProjectAs = QAction('Save project as...', self, shortcut='Ctrl+Shift+S')
		self.actionSaveProjectAs.triggered.connect(self.saveProjectAs)

		self.actionOpenProject = QAction('Open project...', self, shortcut='Ctrl+O')
		self.actionOpenProject.triggered.connect(self.openProject)

		self.actionNewProject = QAction('New project', self, shortcut='Ctrl+N')
		self.actionNewProject.triggered.connect(self.newProject)

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

	def createToolbar(self):
		"""
		Creates the main toolbar and sets the toolbar buttons.
		"""
		# Add toolbar
		self.toolbar = self.addToolBar('Main tools')
		
		# Add the transform tool buttons to the toolbar
		self.toolbar.addAction(self.actionFreeTransformTool)
		self.toolbar.addAction(self.actionLandmarkTransformTool)
		self.toolbar.addAction(self.actionDeformableTransformTool)

		# Insert widget so that other toolbar items will be pushed to the right
		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.toolbar.addWidget(spacer)
		
		# TODO: add "don't panic" button

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

	# Events

	def resizeEvent(self, event):
		"""
		Saves the size and position of the window when it is resized so that
		it can be restored on subsequent launches.

		:param event: Resize event
		:type event: QResizeEvent
		"""
		width 	= self.width()
		height 	= self.height()

		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		RegistrationShop.settings.setValue("ui/window/origin/x", xPosition)
		RegistrationShop.settings.setValue("ui/window/origin/y", yPosition)
		RegistrationShop.settings.setValue("ui/window/width", width)
		RegistrationShop.settings.setValue("ui/window/height", height)

	def moveEvent(self, event):
		"""
		Saves the position of the window when it is moved so that it can be 
		restored on subsequent launches.

		:param event: Move event
		:type event: QMoveEvent
		"""
		xPosition = self.geometry().x()
		yPosition = self.geometry().y()

		RegistrationShop.settings.setValue("ui/window/origin/x", xPosition)
		RegistrationShop.settings.setValue("ui/window/origin/y", yPosition)

	def closeEvent(self, event):
		"""
		TODO: ask if app should really quit.

		:param event: Close event
		:type event: QCloseEvent
		"""
		pass
	
	# Private Functions

	def setApplicationPath(self):
		"""
		Finds the path to the application. This is done so that it
		can figure out where certain resources are located. 
		QCoreApplication::applicationDirPath() on OS X does not return the 
		desired path to the actual application but to the python executable 
		in /Library/FrameWorks. This is inconvenient because images can't be
		located that way.
		So instead os.path is used to find the location of this __file__.
		"""
		AppVars.setPath(os.path.dirname(os.path.abspath(__file__)))

	# Action callbacks
	@Slot()
	def addFreeTransform(self):
		print "Add free transform"

	@Slot()
	def addLandmarkTransform(self):
		print "Add landmark transform"

	@Slot()
	def addDeformableTransform(self):
		print "Add deformable transform"

	@Slot()
	def loadFixedDataSetFile(self):
		"""
		Open file dialog to search for data files. If valid data is given, it will
		pass the data file location on to the slicer and the project controller.
		"""
		dataReader = DataReader()
		extensions = dataReader.GetSupportedExtensionsAsString()
		fileName, other = QFileDialog.getOpenFileName(self, "Open fixed data set", "", "Images ("+extensions+")", options=QFileDialog.Directory)
		if len(fileName) > 0:
			projectController = ProjectController.Instance()
			projectController.loadFixedDataSet(fileName)

	@Slot()
	def loadMovingDataSetFile(self):
		"""
		Open file dialog to search for data files. If valid data is given, it will
		pass the data file location on to the slicer and the project controller.
		"""
		dataReader = DataReader()
		extensions = dataReader.GetSupportedExtensionsAsString()
		fileName, other = QFileDialog.getOpenFileName(self, "Open moving data set", "", "Images ("+extensions+")", options=QFileDialog.Directory)
		if len(fileName) > 0:
			projectController = ProjectController.Instance()
			projectController.loadMovingDataSet(fileName)

	@Slot()
	def saveProject(self):
		"""
		Save the project to the specified name in the current project. If no name
		is specified, then 'save project as' is called.
		"""
		projCont = ProjectController.Instance()
		
		if projCont.currentProject.folder is not None:
			# Save that project
			# print "Save project at", projCont.currentProject.folder
			saved = projCont.saveProject()
			if saved:
				# Save it in the settings that this was the last opened project
				RegistrationShop.settings.setValue("project/lastProject", projCont.currentProject.folder)
		else:
			self.saveProjectAs()

	@Slot()
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
			ProjectController.Instance().currentProject.folder = fileName
			# Call save project
			self.saveProject()

	@Slot()
	def openProject(self, folderName=None):
		"""
		If no project name is supplied, it will open a file dialog so 
		that the user can select a project file
		or project folder.

		:param folderName: Name of a folder with a project
		:type folderName: basestring
		"""
		fileName = ""
		if folderName:
			fileName = folderName
		else:
			fileName = QFileDialog.getExistingDirectory(self, "Open project", "", QFileDialog.ShowDirsOnly)
		
		if len(fileName) > 0:
			fullName = fileName + ProjectController.Instance().ProjectFile
			if os.path.isfile(fullName):
				loaded = ProjectController.Instance().loadProject(fileName)
				if loaded:
					RegistrationShop.settings.setValue("project/lastProject", fileName)
			else:
				print "Warning: Project file does not exist"

	@Slot()
	def newProject(self):
		"""
		Create new project by calling the project controller
		"""
		ProjectController.Instance().newProject()


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
