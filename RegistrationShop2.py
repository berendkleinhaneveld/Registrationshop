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
from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow
from PySide.QtGui import QApplication
from PySide.QtGui import QAction
from PySide.QtGui import QIcon
from PySide.QtGui import QFileDialog
from PySide.QtGui import QScrollArea
from PySide.QtGui import QPushButton
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QMenuBar
from PySide.QtGui import QWidget
from PySide.QtGui import QSizePolicy
from PySide.QtGui import QSplitter
from PySide.QtGui import QComboBox
from PySide.QtGui import QTabWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QFrame
from PySide.QtGui import QGridLayout
from PySide.QtCore import Slot

from MultiRenderWidget import MultiRenderWidget
# Import ui elements
from core.AppVars import AppVars
from core.ProjectController import ProjectController
# from ui.VolumeViewerWidget import VolumeViewerWidget
from core.DataReader import DataReader
from RenderWidget import RenderWidget

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
		# self.resultDataWidget = VolumeViewerWidget()
		# self.resultDataWidget = RenderWidget()
		self.resultDataWidget = MultiRenderWidget()
		self.movingDataWidget = RenderWidget()

		# Render properties widgets
		spLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		spLeft.setHorizontalStretch(1)

		self.fixedPropWidget = RenderPropWidget(self.fixedDataWidget, parent=self)
		self.fixedPropWidget.setSizePolicy(spLeft)
		self.fixedPropWidget.setFileChangedSignal(ProjectController.Instance().changedFixedData)
		self.fixedPropWidget.setLoadDataSlot(self.loadFixedDataSetFile)
		self.resultPropWidget = ResultPropWidget(self)
		self.resultPropWidget.setSizePolicy(spLeft)
		self.movingPropWidget = RenderPropWidget(self.movingDataWidget, parent=self)
		self.movingPropWidget.setSizePolicy(spLeft)
		self.movingPropWidget.setFileChangedSignal(ProjectController.Instance().changedMovingData)
		self.movingPropWidget.setLoadDataSlot(self.loadMovingDataSetFile)


		ProjectController.Instance().changedFixedData.connect(self.fixedDataWidget.loadFile)
		# ProjectController.Instance().changedFixedData.connect(self.fixedPropWidget.loadFile)
		# ProjectController.Instance().changedFixedData.connect(self.resultDataWidget.setFixedDatasetName)
		# ProjectController.Instance().changedMovingData.connect(self.resultDataWidget.setMovingDatasetName)
		ProjectController.Instance().changedMovingData.connect(self.movingDataWidget.loadFile)
		# ProjectController.Instance().changedMovingData.connect(self.movingPropWidget.loadFile)

		self.verticalSplitter = QSplitter()
		self.verticalSplitter.setOrientation(Qt.Vertical)

		renderHBoxLayout = QHBoxLayout()
		renderHBoxLayout.setSpacing(1)
		renderHBoxLayout.setContentsMargins(0, 0, 0, 0)
		renderHBoxLayout.addWidget(self.fixedDataWidget)
		renderHBoxLayout.addWidget(self.resultDataWidget)
		renderHBoxLayout.addWidget(self.movingDataWidget)

		propsHBoxLayout = QHBoxLayout()
		propsHBoxLayout.setSpacing(1)
		propsHBoxLayout.setContentsMargins(0, 0, 0, 0)
		propsHBoxLayout.addWidget(self.fixedPropWidget)
		propsHBoxLayout.addWidget(self.resultPropWidget)
		propsHBoxLayout.addWidget(self.movingPropWidget)

		rendersWidget = QWidget()
		rendersWidget.setLayout(renderHBoxLayout)
		propsWidget = QWidget()
		propsWidget.setMaximumHeight(300)
		propsWidget.setMinimumHeight(300)
		propsWidget.setLayout(propsHBoxLayout)

		self.verticalSplitter.addWidget(rendersWidget)
		self.verticalSplitter.addWidget(propsWidget)
		self.setCentralWidget(self.verticalSplitter)

	def createActions(self):
		"""
		Create actions that can be attached to buttons and menus.
		"""
		userTransformIconName = os.path.join(AppVars.imagePath(), 'UserTransformButton.png')
		print userTransformIconName
		landmarkTransformIconName = os.path.join(AppVars.imagePath(), 'LandmarkTransformButton.png')
		deformableTransformIconName = os.path.join(AppVars.imagePath(), 'DeformableTransformButton.png')

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
		
		# TODO: add don't panic button

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
		Tries to find the path to the application. This is done so that it
		can figure out where certain resources are located. 
		QCoreApplication::applicationDirPath() on OS X does not return the 
		desired path to the actual application but to the python executable 
		in /Library/FrameWorks. This is inconvenient because images can't be
		located that way.
		"""
		AppVars.setPath(os.path.dirname(os.path.abspath(__file__)) + "/")

	# Action callbacks

	def addFreeTransform(self):
		print "Add free transform"

	def addLandmarkTransform(self):
		print "Add landmark transform"

	def addDeformableTransform(self):
		print "Add deformable transform"

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

	def newProject(self):
		"""
		Create new project by calling the project controller
		"""
		ProjectController.Instance().newProject()

"""
There is a RenderWidget object and a RenderPropWidget.
The RenderWidget will render the dataset defined by the project (fixed or moving)
The RenderPropWidget will hold the parameters and properties for the dataset.

Steps:
User loads file.
ProjectController changes filename.
RenderWidget loads the dataset. (But needs its parameters from RPW)
(RenderPropWidget is a container for the RenderParameterWidget and the RenderInfoWidget.)
RenderParameterWidget gets the parameter widget from RenderWidget.
RenderWidget gets the parameter widget from its VolumeProperty.
RenderInfoWidget also gets the parameters from RenderWidget.
"""

class RenderPropWidget(QWidget):
	"""
	RenderPropWidget is a widget that is displayed under the render widgets.
	"""
	def __init__(self, renderWidget, parent=None):
		super(RenderPropWidget, self).__init__(parent)

		# Two tabs: Visualization and Data info
		self.visParamTabWidget = RenderParameterWidget(renderWidget)
		self.dataInfoTabWidget = RenderInfoWidget()

		# Create the load dataset widget
		self.loadDataWidget = QWidget()
		self.loadDataButton = QPushButton()
		self.loadDataButton.setText("Load a dataset")
		# button.clicked.connect(self.parent().loadFixedDataSetFile)

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.loadDataButton)
		self.loadDataWidget.setLayout(layout)

		# Create the tab widget
		self.tabWidget = QTabWidget()
		self.tabWidget.addTab(self.visParamTabWidget, "Visualization")
		self.tabWidget.addTab(self.dataInfoTabWidget, "Data info")

		layout = QVBoxLayout()
		layout.addWidget(self.loadDataWidget)	
		self.setLayout(layout)

	def setFileChangedSignal(self, signal):
		self.signal = signal
		self.signal.connect(self.loadFile)
		self.signal.connect(self.dataInfoTabWidget.loadFile)

	def setLoadDataSlot(self, slot):
		self.loadDataButton.clicked.connect(slot)

	@Slot(basestring)
	def loadFile(self, fileName):
		layout = self.layout()
		if fileName is None:
			if layout.indexOf(self.tabWidget) != -1:
				layout.removeWidget(self.tabWidget)
				self.tabWidget.setParent(None)
				layout.addWidget(self.loadDataWidget)
				self.setLayout(layout)
		else:
			if layout.indexOf(self.loadDataWidget) != -1:
				layout.removeWidget(self.loadDataWidget)
				self.loadDataWidget.setParent(None)
				layout.addWidget(self.tabWidget)
				self.setLayout(layout)


class RenderParameterWidget(QWidget):
	def __init__(self, renderWidget, parent=None):
		super(RenderParameterWidget, self).__init__(parent)

		self.renderWidget = renderWidget
		self.renderWidget.loadedData.connect(self.dataLoaded)

		self.visTypeLabel = QLabel("Visualization type")
		self.visTypeLabel.setMaximumHeight(20)

		self.visTypeCompoBox = QComboBox()
		for renderType in self.renderWidget.renderTypes:
			self.visTypeCompoBox.addItem(renderType)

		self.paramWidget = None

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.visTypeLabel)
		layout.addWidget(self.visTypeCompoBox)
		self.setLayout(layout)

		self.scrollArea = QScrollArea()
		self.scrollArea.setFrameShape(QFrame.NoFrame)
		self.scrollArea.setAutoFillBackground(False)
		self.scrollArea.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.scrollArea.setWidgetResizable(True)

		self.visTypeCompoBox.currentIndexChanged.connect(self.renderTypeComboBoxChanged)

	def renderTypeComboBoxChanged(self, index):
		self.renderWidget.SetRenderType(self.visTypeCompoBox.currentText())
		self.UpdateWidgetFromRenderWidget()
		self.renderWidget.Update()

	@Slot()
	def dataLoaded(self):
		# Get the correct widget from the RenderWidget
		self.UpdateWidgetFromRenderWidget()

	def UpdateWidgetFromRenderWidget(self):
		"""
		Update the parameter widget with a widget from the render widget.
		"""
		# Add the scroll area for the parameter widget if it is not there yet
		layout = self.layout()
		if layout.indexOf(self.scrollArea) == -1:
			layout.addWidget(self.scrollArea)
			self.setLayout(layout)

		# Clear the previous parameter widget
		if self.paramWidget is not None:
			self.paramWidget.setParent(None)
			self.renderWidget.renderVolumeProperty.disconnect(QtCore.SIGNAL("updatedTransferFunction"), self.transferFunctionChanged)

		# Get a new parameter widget from the render widget
		self.paramWidget = self.renderWidget.GetParameterWidget()
		self.scrollArea.setWidget(self.paramWidget)
		self.renderWidget.renderVolumeProperty.updatedTransferFunction.connect(self.transferFunctionChanged)

	@Slot()
	def transferFunctionChanged(self):
		"""
		Slot that can be used when a transfer function has changed so that
		the render will be updated afterwards.
		"""
		self.renderWidget.Update()

class ResultPropWidget(QWidget):
	"""
	ResultPropWidget is a widget that is displayed under the result render
	widget. It contains tabs with some controls for interaction and 
	visualization of the combined render widget.
	"""
	def __init__(self, parent=None):
		super(ResultPropWidget, self).__init__(parent)

		# Two tabs: Visualization and Data info
		self.mixParamWidget = QWidget()
		self.registrationHistoryWidget = QWidget()

		# Create the tab widget
		self.tabWidget = QTabWidget()
		self.tabWidget.addTab(self.mixParamWidget, "Mix")
		self.tabWidget.addTab(self.registrationHistoryWidget, "History")

		layout = QVBoxLayout()
		layout.addWidget(self.tabWidget)
		self.setLayout(layout)

class RenderInfoWidget(QWidget):
	"""
	RenderInfoWidget shows information about the loaded dataset. Things like
	filenames, range of data values, size of data, etc.
	"""
	def __init__(self):
		super(RenderInfoWidget, self).__init__()

	@Slot(basestring)
	def loadFile(self, fileName):
		if fileName is None:
			return

		# Read info from dataset
		# TODO: read out the real world dimensions in inch or cm
		# TODO: scalar type
		imageReader = DataReader()
		imageData = imageReader.GetImageData(fileName)

		directory, name = os.path.split(fileName)
		dimensions = imageData.GetDimensions()
		minimum, maximum = imageData.GetScalarRange()

		# Create string representations
		nameField = QLabel("File name:")
		dimsField = QLabel("Dimensions:")
		voxsField = QLabel("Voxels:")
		rangField = QLabel("Range:")

		nameField.setAlignment(Qt.AlignRight)
		dimsField.setAlignment(Qt.AlignRight)
		voxsField.setAlignment(Qt.AlignRight)
		rangField.setAlignment(Qt.AlignRight)

		nameText = name
		dimsText = "(" + str(dimensions[0]) + ", " + str(dimensions[1]) + ", " + str(dimensions[2]) + ")"
		voxsText = str(dimensions[0] * dimensions[1] * dimensions[2])
		rangText = "[" + str(minimum) + " : " + str(maximum) + "]"

		# Create labels
		labelTitle = QLabel(nameText)
		labelDimensions = QLabel(dimsText)
		labelVoxels = QLabel(voxsText)
		labelRange = QLabel(rangText)

		# Create a nice layout for the labels
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(nameField, 0, 0)
		layout.addWidget(dimsField, 1, 0)
		layout.addWidget(voxsField, 2, 0)
		layout.addWidget(rangField, 3, 0)

		layout.addWidget(labelTitle, 0, 1)
		layout.addWidget(labelDimensions, 1, 1)
		layout.addWidget(labelVoxels, 2, 1)
		layout.addWidget(labelRange, 3, 1)
		self.setLayout(layout)


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
