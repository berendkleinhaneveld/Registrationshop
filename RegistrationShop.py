#!/usr/local/bin/python
"""
Registrationshop

3D registration tool for medical purposes.

:Authors:
	Berend Klein Haneveld 2013
"""

import sys
import os.path

# Add external relative folders to sys path
rootDir = os.path.dirname(os.path.realpath(__file__))
resizerPath = "./external/columnresizer/src/"
relPaths = [resizerPath]
for path in relPaths:
	sys.path.append(os.path.join(rootDir, path))

# PySide stuff
from PySide.QtGui import QMainWindow
from PySide.QtGui import QApplication
from PySide.QtGui import QAction
from PySide.QtGui import QIcon
from PySide.QtGui import QFileDialog
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QGridLayout
from PySide.QtGui import QWidget
from PySide.QtGui import QSizePolicy
from PySide.QtGui import QSplitter
from PySide.QtCore import Qt
from PySide.QtCore import Slot

# Import core stuff
from core import AppVars
from core import AppResources
from core.project import ProjectController
from core.data import DataReader
from core.data import DataTransformer
from core.data import DataWriter
from core.elastix import ParameterList
# Import ui elements
from ui import MainWindow
from ui import WindowDialog
from ui import RenderController
from ui import MultiRenderController
from ui.dialogs import FileTypeDialog
from ui.dialogs import ElastixMainDialog
from ui.dialogs import ResetVisualizationDialog
from ui.widgets import RenderWidget
from ui.widgets import MultiRenderWidget
from ui.widgets import TitleWidget
from ui.widgets import RenderPropWidget
from ui.widgets import MultiRenderPropWidget
from ui.widgets import LandmarkWidget
from ui.widgets import StatusWidget
from ui.widgets.ToolbarWidget import ToolbarWidget
from ui.transformations import UserTransformationTool
from ui.transformations import LandmarkTransformationTool
from ui.transformations import DeformableTransformationTool
from InspectionTool import CompareWidget
from InspectionTool import ComparisonController


# Define settings parameters
APPNAME = "RegistrationShop"
ORGNAME = "TU Delft"
ORGDOMAIN = "tudelft.nl"


class RegistrationShop(MainWindow, WindowDialog):
	"""
	Main class that starts up the application.
	Creates UI and starts project/plugin managers.
	"""

	def __init__(self, args):
		"""
		Sets app specific properties.
		Initializes the UI.
		"""
		super(RegistrationShop, self).__init__(args)

		self.setApplicationPath()
		# Instantiate the project controller
		ProjectController.Instance()

		# Initialize the user interface
		self.initUI()

		lastProject = RegistrationShop.settings.value("project/lastProject", None)
		if lastProject:
			self.openProject(lastProject)

	def initialize(self):
		# Initialize the render window interactors only after calling show()
		# otherwise OpenGL errors will occur on OS X
		self.fixedDataWidget.rwi.Initialize()
		self.movingDataWidget.rwi.Initialize()
		self.multiDataWidget.rwi.Initialize()

	# UI setup methods

	def initUI(self):
		"""
		Initializes the UI. Makes sure previous state of
		application is restored.
		"""
		# Create actions and elements
		self.createElements()
		self.connectElements()
		self.createActions()
		self.createMenus()
		self.createToolbar()
		self.restoreState()

		# Set some window/application properties
		self.setUnifiedTitleAndToolBarOnMac(True)
		self.setWindowTitle(APPNAME)
		self.setWindowState(Qt.WindowActive)

	def createElements(self):
		"""
		Creates the widgets and docks of which the
		main window is composed.
		"""
		self.mainWindow = QMainWindow()
		projectController = ProjectController.Instance()
		self.transformTool = None

		# Render widgets
		self.fixedDataWidget = RenderWidget()
		self.movingDataWidget = RenderWidget()
		self.multiDataWidget = MultiRenderWidget()

		self.fixedRenderController = RenderController(self.fixedDataWidget, "fixed")
		self.movingRenderController = RenderController(self.movingDataWidget, "moving")
		self.multiRenderController = MultiRenderController(self.multiDataWidget)

		# Give references of the render controllers to the project controller
		projectController.fixedRenderController = self.fixedRenderController
		projectController.movingRenderController = self.movingRenderController
		projectController.multiRenderController = self.multiRenderController

		# Render properties widgets
		sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(1)

		self.fixedPropWidget = RenderPropWidget(self.fixedRenderController, parent=self)
		self.fixedPropWidget.setSizePolicy(sizePolicy)
		self.fixedPropWidget.setFileChangedSignal(projectController.fixedFileChanged)
		self.fixedPropWidget.setLoadDataSlot(self.loadFixedDataSetFile)

		self.movingPropWidget = RenderPropWidget(self.movingRenderController, parent=self)
		self.movingPropWidget.setSizePolicy(sizePolicy)
		self.movingPropWidget.setFileChangedSignal(projectController.movingFileChanged)
		self.movingPropWidget.setLoadDataSlot(self.loadMovingDataSetFile)

		self.multiPropWidget = MultiRenderPropWidget(self.multiRenderController, parent=self)
		self.multiPropWidget.setSizePolicy(sizePolicy)

		self.verticalSplitter = QSplitter()
		self.verticalSplitter.setOrientation(Qt.Vertical)

		# Create the layouts

		fixedDataTitleWidget = TitleWidget("Fixed volume")
		multiDataTitleWidget = TitleWidget("Fixed + Moving")
		movingDataTitleWidget = TitleWidget("Moving volume")

		fixedLayout = QGridLayout()
		fixedLayout.setSpacing(0)
		fixedLayout.setContentsMargins(0, 0, 0, 0)
		fixedLayout.addWidget(fixedDataTitleWidget)
		fixedLayout.addWidget(self.fixedDataWidget)
		fixedWidget = QWidget()
		fixedWidget.setLayout(fixedLayout)

		multiLayout = QGridLayout()
		multiLayout.setSpacing(0)
		multiLayout.setContentsMargins(0, 0, 0, 0)
		multiLayout.addWidget(multiDataTitleWidget)
		multiLayout.addWidget(self.multiDataWidget)
		multiWidget = QWidget()
		multiWidget.setLayout(multiLayout)

		movingLayout = QGridLayout()
		movingLayout.setSpacing(0)
		movingLayout.setContentsMargins(0, 0, 0, 0)
		movingLayout.addWidget(movingDataTitleWidget)
		movingLayout.addWidget(self.movingDataWidget)
		movingWidget = QWidget()
		movingWidget.setLayout(movingLayout)

		horizontalSplitter = QSplitter()
		horizontalSplitter.setOrientation(Qt.Horizontal)
		horizontalSplitter.addWidget(fixedWidget)
		horizontalSplitter.addWidget(multiWidget)
		horizontalSplitter.addWidget(movingWidget)

		propsLayout = QHBoxLayout()
		propsLayout.setSpacing(1)
		propsLayout.setContentsMargins(0, 0, 0, 0)
		propsLayout.addWidget(self.fixedPropWidget)
		propsLayout.addWidget(self.multiPropWidget)
		propsLayout.addWidget(self.movingPropWidget)

		propsWidget = QWidget()
		propsWidget.setMinimumHeight(245)
		propsWidget.setMaximumHeight(350)
		propsWidget.setLayout(propsLayout)

		self.verticalSplitter.addWidget(horizontalSplitter)
		self.verticalSplitter.addWidget(propsWidget)
		self.verticalSplitter.setStretchFactor(0, 2)
		self.verticalSplitter.setStretchFactor(1, 1)
		self.setCentralWidget(self.verticalSplitter)

	def connectElements(self):
		"""
		All the elements have to be connected because they are dependent
		on each other.
		There is the project controller, two render controllers and a multi render
		controller.
		Also there are two render widgets and a multi render widget. Together with some
		parameter widgets that show settings and with which the user can interact.
		"""
		projectController = ProjectController.Instance()
		projectController.fixedFileChanged.connect(self.fixedRenderController.setFile)
		projectController.fixedFileChanged.connect(self.multiRenderController.setFixedFile)
		projectController.movingFileChanged.connect(self.movingRenderController.setFile)
		projectController.movingFileChanged.connect(self.multiRenderController.setMovingFile)
		projectController.fixedSettingsChanged.connect(self.fixedRenderController.setRenderSettings)
		projectController.movingSettingsChanged.connect(self.movingRenderController.setRenderSettings)
		projectController.multiSettingsChanged.connect(self.multiRenderController.setRenderSettings)

		self.fixedRenderController.visualizationChanged.connect(self.multiRenderController.setFixedVisualization)
		self.fixedRenderController.visualizationUpdated.connect(self.multiRenderController.setFixedVisualization)
		self.movingRenderController.visualizationChanged.connect(self.multiRenderController.setMovingVisualization)
		self.movingRenderController.visualizationUpdated.connect(self.multiRenderController.setMovingVisualization)

		self.multiDataWidget.transformations.transformationChanged.connect(self.movingDataWidget.transformationsUpdated)

	def createActions(self):
		"""
		Create actions that can be attached to buttons and menus.
		"""
		userTransformIconName = AppResources.imageNamed('UserTransformButton.png')
		landmarkTransformIconName = AppResources.imageNamed('LandmarkTransformButton.png')
		deformableTransformIconName = AppResources.imageNamed('DeformableTransformButton.png')
		compareIconName = AppResources.imageNamed('CompareButton.png')
		helpIconName = AppResources.imageNamed('HelpButton.png')

		self.actionFreeTransformTool = QAction('Manual transform', self, shortcut='Ctrl+1')
		self.actionFreeTransformTool.setIcon(QIcon(userTransformIconName))
		self.actionFreeTransformTool.triggered.connect(self.addManualTransform)

		self.actionLandmarkTransformTool = QAction('Landmark transform', self, shortcut='Ctrl+2')
		self.actionLandmarkTransformTool.setIcon(QIcon(landmarkTransformIconName))
		self.actionLandmarkTransformTool.triggered.connect(self.addLandmarkTransform)

		self.actionDeformableTransformTool = QAction('Automatic transform', self, shortcut='Ctrl+3')
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

		self.actionExportDataAs = QAction('Export data...', self, shortcut='Ctrl+E')
		self.actionExportDataAs.triggered.connect(self.exportDataAs)

		self.actionOpenProject = QAction('Open project...', self, shortcut='Ctrl+O')
		self.actionOpenProject.triggered.connect(self.openProject)

		self.actionNewProject = QAction('New project', self, shortcut='Ctrl+N')
		self.actionNewProject.triggered.connect(self.newProject)

		self.actionCompare = QAction('Compare', self, shortcut='Ctrl+U')
		self.actionCompare.setIcon(QIcon(compareIconName))
		self.actionCompare.triggered.connect(self.startComparison)

		self.actionHelp = QAction('Help', self, shortcut='Ctrl+H')
		self.actionHelp.setIcon(QIcon(helpIconName))
		self.actionHelp.triggered.connect(self.showHelp)

	def createMenus(self):
		"""
		Creates menus from actions.
		"""
		self.menuBar = self.menuBar()
		self.menuItemFile = self.menuBar.addMenu('&File')
		self.menuItemFile.addAction(self.actionNewProject)
		self.menuItemFile.addAction(self.actionOpenProject)
		# TODO: Open recent >
		self.menuItemFile.addAction(self.actionSaveProject)
		self.menuItemFile.addAction(self.actionSaveProjectAs)
		self.menuItemFile.addAction(self.actionExportDataAs)

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
		self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		self.toolbar.setAllowedAreas(Qt.TopToolBarArea)
		self.toolbar.setFloatable(False)
		self.toolbar.setMovable(False)

		# Create custom toolbar widget that can align items left, center and right
		self.toolbarWidget = ToolbarWidget()
		self.toolbarWidget.addActionLeft(self.actionFreeTransformTool)
		self.toolbarWidget.addActionLeft(self.actionLandmarkTransformTool)
		self.toolbarWidget.addActionLeft(self.actionDeformableTransformTool)

		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Welcome to RegistrationShop!\nStart your registration by loading two datasets. "
			+ "After that you can use the transform tools to align your volume data.")
		self.toolbarWidget.addCenterItem(statusWidget)

		# Add help button
		self.toolbarWidget.addActionRight(self.actionCompare)
		self.toolbarWidget.addActionRight(self.actionHelp)
		self.toolbar.addWidget(self.toolbarWidget)

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
	def addManualTransform(self):
		"""
		What happens when manual transform is added:
		* Entry is added to the tab history
			* Translation fields
			* Rotation fields
			* Scale field(s)
		* Transform box is added to the render widget
		* Button with apply (will apply the transform to the data)

		Applying the transform to the data means:
		* Create new dataset from transformed data
		* Save this data to the project folder
		* Read in the new data and update this in the multi render widget
		* this would mean a new data model for the multi render widget
		"""
		if not self.movingDataWidget.imageData:
			statusWidget = StatusWidget.Instance()
			statusWidget.setText("Please load a moving dataset before starting a manual transform.")
			return

		if self.transformTool is not None:
			self.transformTool.cleanUp()

		self.transformTool = UserTransformationTool()
		self.transformTool.setRenderWidgets(moving=self.movingDataWidget, multi=self.multiDataWidget)
		self.multiPropWidget.setTransformTool(self.transformTool)
		self.transformTool.toolFinished.connect(self.transformToolFinished)

	@Slot()
	def addLandmarkTransform(self):
		if not self.fixedDataWidget.imageData or not self.movingDataWidget.imageData:
			statusWidget = StatusWidget.Instance()
			statusWidget.setText("Please load a fixed and a moving dataset before starting a landmark transform.")
			return

		# Clean up the last transform tool
		if self.transformTool is not None:
			self.transformTool.cleanUp()

		self.transformTool = LandmarkTransformationTool()
		self.transformTool.setRenderWidgets(fixed=self.fixedDataWidget,
			moving=self.movingDataWidget,
			multi=self.multiDataWidget)

		# Create a tab page under the fixed render widget
		fixedLandmarkWidget = LandmarkWidget()
		self.fixedPropWidget.addTabWidget(fixedLandmarkWidget, "Landmark")

		# Create a tab page under the moving render widget
		movingLandmarkWidget = LandmarkWidget()
		self.movingPropWidget.addTabWidget(movingLandmarkWidget, "Landmark")

		# Make sure the landmark transform tool knows of these tab widgets
		self.transformTool.setLandmarkWidgets(fixedLandmarkWidget, movingLandmarkWidget)

		# Start the transformation
		self.multiPropWidget.setTransformTool(self.transformTool)
		self.transformTool.toolFinished.connect(self.transformToolFinished)

	@Slot()
	def addDeformableTransform(self):
		if not self.fixedDataWidget.imageData or not self.movingDataWidget.imageData:
			statusWidget = StatusWidget.Instance()
			statusWidget.setText("Please load a fixed and a moving dataset before starting a deformable transform.")
			return

		self.multiPropWidget.tabWidget.setCurrentWidget(self.multiPropWidget.transformParamWidget)

		if self.transformTool is not None:
			self.transformTool.cleanUp()

		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Choose a template for a deformable transform. After choosing "
			"a template you will be able to review and adjust the parameters.")

		dialog = ElastixMainDialog(self)
		dialog.setModal(True)
		result = dialog.exec_()
		if not result:
			return
		if not dialog.transformation:
			# load custom file
			filename, other = QFileDialog.getOpenFileName(self, "Open custom parameter file", "", "(*.c *.txt)")
			if len(filename) == 0:
				return
			transformation = ParameterList()
			if not transformation.loadFromFile(filename):
				transformation = None
				statusWidget = StatusWidget.Instance()
				statusWidget.setText("Warning: could not load transformation file")
		else:
			transformation = dialog.transformation

		self.transformTool = DeformableTransformationTool()
		self.transformTool.setTransformation(transformation)
		self.transformTool.startedElastix.connect(self.showProgressBar)
		self.transformTool.endedElastix.connect(self.hideProgressBar)
		self.transformTool.setRenderWidgets(fixed=self.fixedDataWidget,
			moving=self.movingDataWidget,
			multi=self.multiDataWidget)
		self.multiPropWidget.setTransformTool(self.transformTool)
		self.transformTool.toolFinished.connect(self.transformToolFinished)

	@Slot()
	def transformToolFinished(self):
		self.multiPropWidget.transformToolFinished()
		self.fixedPropWidget.removeTabWidget()
		self.movingPropWidget.removeTabWidget()

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
			# If there was another dataset first, ask if the user if the
			# visualizations should be reset
			projectController = ProjectController.Instance()
			if projectController.currentProject.fixedData:
				dialog = ResetVisualizationDialog(self)
				dialog.setWindowModality(Qt.WindowModal)
				dialog.exec_()
				if dialog.result is not None:
					projectController.loadFixedDataSet(fileName)
					if dialog.result:
						self.fixedRenderController.resetVisualizations()
			else:
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
			# If there was another dataset first, ask if the user if the
			# visualizations should be reset
			projectController = ProjectController.Instance()
			if projectController.currentProject.movingData:
				dialog = ResetVisualizationDialog(self)
				dialog.setWindowModality(Qt.WindowModal)
				dialog.exec_()
				if dialog.result is not None:
					projectController.loadMovingDataSet(fileName)
					if dialog.result:
						self.movingRenderController.resetVisualizations()
			else:
				# Inserting an identity transform
				self.multiDataWidget.transformations.append(Transformation(vtkTransform(), "No transform", fileName))
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
			saved = projCont.saveProject()
			statusWidget = StatusWidget.Instance()
			if saved:
				# Save it in the settings that this was the last opened project
				RegistrationShop.settings.setValue("project/lastProject", projCont.currentProject.folder)
				statusWidget.setText("The project was succesfully saved to disk.")
			else:
				statusWidget.setText("Something went wrong while saving the project to disk. "
					"Please try to save the project again.")
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
				self.multiDataWidget.transformations.clear()
				loaded = ProjectController.Instance().loadProject(fileName)
				if loaded:
					RegistrationShop.settings.setValue("project/lastProject", fileName)
				else:
					print "Couldn't load project:", folderName
			else:
				print "Warning: Project file does not exist"
				RegistrationShop.settings.remove("project/lastProject")

	@Slot()
	def newProject(self):
		"""
		Create new project by calling the project controller
		"""
		self.multiDataWidget.transformations.clear()
		ProjectController.Instance().newProject()
		# Reset the last loaded project in the settings
		RegistrationShop.settings.setValue("project/lastProject", "")

	@Slot()
	def exportDataAs(self):
		"""
		Opens a file dialog so that the user can provide a filename
		for saving the transformed dataset to.
		"""
		fileType = FileTypeDialog.getFileType(self, "Choose file type for export")
		if len(fileType) == 0:
			return

		extension = "(*." + fileType + ")"
		fileName, other = QFileDialog.getSaveFileName(self, "Save registration result to...", "", extension)
		if len(fileName) == 0:
			return

		self.showProgressBar("Exporting data...")

		transform = self.multiDataWidget.transformations.completeTransform()
		dataReader = DataReader()
		imageData = dataReader.GetImageData(ProjectController.Instance().currentProject.movingData)
		transformer = DataTransformer()
		outputData = transformer.TransformImageData(imageData, transform)
		writer = DataWriter()
		writer.WriteToFile(outputData, fileName, fileType)

		self.hideProgressBar()

	@Slot()
	def startComparison(self):
		projectController = ProjectController.Instance()
		project = projectController.currentProject
		if not project or not project.fixedData or not project.movingData:
			statusWidget = StatusWidget.Instance()
			statusWidget.setText("Could not start comparison. Please make a project first"
				" and make sure to load two datasets.")
			return

		if hasattr(self, "compareWidget"):
			del self.compareWidget

		transform = self.multiDataWidget.transformations.completeTransform()

		self.controller = ComparisonController()
		self.controller.setInputData(project.fixedData, project.movingData, transform)
		self.compareWidget = CompareWidget(self.controller.widgets)
		self.compareWidget.show()
		self.controller.initialize()
		self.controller.slicerChanged(self.controller.fixedImageWidget)

	@Slot()
	def showHelp(self):
		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Don't panic!")


def main():
	# Fix for PySide on OSX Mavericks
	import sys
	if sys.platform.startswith("darwin"):
		from PySide.QtGui import QFont
		QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")

	app = QApplication(sys.argv)
	app.setObjectName(APPNAME)
	app.setApplicationName(APPNAME)
	app.setOrganizationName(ORGNAME)
	app.setOrganizationDomain(ORGDOMAIN)

	mainWindow = RegistrationShop(sys.argv)
	mainWindow.raise_()
	mainWindow.show()
	mainWindow.initialize()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
