"""
ProjectController

:Authors:
    Berend Klein Haneveld
"""

from PySide6.QtCore import QObject
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal
import yaml

from .Project import Project
from core.decorators import Singleton


@Singleton
class ProjectController(QObject):
    """
    Model controller class that manages projects.
    There should be only one instance in the whole application.
    """

    # Signals
    fixedFileChanged = Signal(str)
    movingFileChanged = Signal(str)
    fixedSettingsChanged = Signal(object)
    movingSettingsChanged = Signal(object)
    multiSettingsChanged = Signal(object)
    projectChanged = Signal(Project)

    # Define the standard project file name
    ProjectFile = "/project.yaml"

    def __init__(self, project=None):
        """
        :param project: Project to be made current
        :type project: Project
        """
        QObject.__init__(self)

        self.currentProject = project

        self.fixedRenderController = None
        self.movingRenderController = None
        self.multiRenderController = None

        # Create new standard project if no project is provided
        if self.currentProject is None:
            self.currentProject = Project()

    def loadProject(self, folder=None):
        """
        :param folder: Directory of project
        :type folder: str
        :returns:: Success, whether the project could be loaded
        :rtype: bool
        """
        projectFileName = folder + self.ProjectFile
        projectFile = open(projectFileName, "r")

        try:
            project = yaml.load(projectFile, Loader=yaml.UnsafeLoader)
            self.currentProject = project
        except Exception as e:
            print(e)
            return False

        if not self.currentProject.isValid():
            self.currentProject = Project()
            return False

        self.projectChanged.emit(self.currentProject)
        self.fixedFileChanged.emit(self.currentProject.fixedData)
        self.movingFileChanged.emit(self.currentProject.movingData)
        self.fixedSettingsChanged.emit(self.currentProject.fixedSettings)
        self.movingSettingsChanged.emit(self.currentProject.movingSettings)
        self.multiSettingsChanged.emit(self.currentProject.multiSettings)

        return True

    def saveProject(self):
        """
        Saves project to disk.
        Assumes: project name is set and correct

        :param name: File/Directory name to save the project file to
        :type name: str
        :returns:: Success
        :rtype: bool
        """
        # Prepare the project
        if self.fixedRenderController:
            self.currentProject.fixedSettings = (
                self.fixedRenderController.getRenderSettings()
            )
        if self.movingRenderController:
            self.currentProject.movingSettings = (
                self.movingRenderController.getRenderSettings()
            )
        if self.multiRenderController:
            self.currentProject.multiSettings = (
                self.multiRenderController.getRenderSettings()
            )

        try:
            projectFileName = self.currentProject.folder + self.ProjectFile
            projectFile = open(projectFileName, "w+")

            # Create a readable project file
            yaml.dump(self.currentProject, projectFile, default_flow_style=False)
            projectFile.close()
        except Exception as e:
            print(e)
            return False

        # TODO:
        # If folder is empty:
        # If the project is set to not reference the datasets:
        # Copy fixed/moving data over and update the data references
        # Save a yaml representation of the project into the directory
        # If folder is not empty:
        # Ask the user if it should be emptied

        return True

    def newProject(self):
        # Set a new project as current project
        self.currentProject = Project()
        # Send out the signals!
        self.projectChanged.emit(self.currentProject)
        self.fixedFileChanged.emit(self.currentProject.fixedData)
        self.movingFileChanged.emit(self.currentProject.movingData)
        self.fixedSettingsChanged.emit(self.currentProject.fixedSettings)
        self.movingSettingsChanged.emit(self.currentProject.movingSettings)
        self.multiSettingsChanged.emit(self.currentProject.multiSettings)

    # Slots for signals of SlicerWidget
    @Slot(str)
    def loadFixedDataSet(self, name=None):
        """
        Sets the name in the current project as the fixed data set filename
        :param name: File name of fixed data set
        :type name: str
        """
        # TODO: some extra magic like checking if file exists
        self.currentProject.fixedData = name

        # Emit signal that data set file name has changed
        self.fixedFileChanged.emit(self.currentProject.fixedData)

    @Slot(str)
    def loadMovingDataSet(self, name=None):
        """
        Sets the name in the current project as the moving data set filename
        :param name: File name of moving data set
        :type name: str
        """
        # TODO: some extra magic like checking if file exists
        if name == self.currentProject.movingData:
            return
        self.currentProject.movingData = name

        # Emit signal that data set file name has changed
        self.movingFileChanged.emit(self.currentProject.movingData)
