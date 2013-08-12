"""
ProjectController

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtCore import QObject
from PySide.QtCore import Slot
from PySide.QtCore import Signal
import yaml

from Project import Project
from core.decorators import Singleton

@Singleton
class ProjectController(QObject):
	"""
	Model controller class that manages projects.
	There should be only one instance in the whole application.
	"""

	# Signals
	fixedFileChanged = Signal(basestring)
	movingFileChanged = Signal(basestring)
	fixedSettingsChanged = Signal(object)
	movingSettingsChanged = Signal(object)
	multiSettingsChanged = Signal(object)
	resultFileChanged = Signal(basestring)
	projectChanged = Signal(Project)
	
	# Define the standard project file name
	ProjectFile = u"/project.yaml"

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
		if self.currentProject == None:
			self.currentProject = Project()

	def loadProject(self, folder=None):
		"""
		:param folder: Directory of project
		:type folder: unicode
		:returns:: Success, whether the project could be loaded
		:rtype: bool
		"""
		projectFileName = folder + self.ProjectFile
		projectFile = open(projectFileName, "r")
		
		try:
			project = yaml.load(projectFile)
			self.currentProject = project
		except Exception, e:
			print e
			return False

		self.projectChanged.emit(self.currentProject)
		self.fixedFileChanged.emit(self.currentProject.fixedData)
		self.movingFileChanged.emit(self.currentProject.movingData)
		self.resultFileChanged.emit(self.currentProject.resultData)
		self.fixedSettingsChanged.emit(self.currentProject.fixedSettings)
		self.movingSettingsChanged.emit(self.currentProject.movingSettings)
		self.multiSettingsChanged.emit(self.currentProject.multiSettings)

		return True

	def saveProject(self):
		"""
		Saves project to disk. 
		Assumes: project name is set and correct

		:param name: File/Directory name to save the project file to
		:type name: unicode
		:returns:: Success
		:rtype: bool
		"""
		# Prepare the project
		if self.fixedRenderController:
			self.currentProject.fixedSettings = self.fixedRenderController.getRenderSettings()	
		if self.movingRenderController:
			self.currentProject.movingSettings = self.movingRenderController.getRenderSettings()
		if self.multiRenderController:
			self.currentProject.multiSettings = self.multiRenderController.getRenderSettings()

		try:
			projectFileName = self.currentProject.folder + self.ProjectFile
			projectFile = open(projectFileName, "w+")

			# Create a readable project file
			yaml.dump(self.currentProject, projectFile, default_flow_style=False)
			projectFile.close()
		except Exception, e:
			print e
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
		self.resultFileChanged.emit(self.currentProject.resultData)
		self.fixedSettingsChanged.emit(self.currentProject.fixedSettings)
		self.movingSettingsChanged.emit(self.currentProject.movingSettings)
		self.multiSettingsChanged.emit(self.currentProject.multiSettings)

	# Slots for signals of SlicerWidget
	@Slot(basestring)
	def loadFixedDataSet(self, name=None):
		"""
		Sets the name in the current project as the fixed data set filename
		:param name: File name of fixed data set
		:type name: basestring
		"""
		# TODO: some extra magic like checking if file exists
		self.currentProject.fixedData = name

		# Emit signal that data set file name has changed
		self.fixedFileChanged.emit(self.currentProject.fixedData)

	@Slot(basestring)
	def loadMovingDataSet(self, name=None):
		"""
		Sets the name in the current project as the moving data set filename
		:param name: File name of moving data set
		:type name: basestring
		"""
		# TODO: some extra magic like checking if file exists
		self.currentProject.movingData = name

		# Emit signal that data set file name has changed
		self.movingFileChanged.emit(self.currentProject.movingData)
	
	def register(self):
		"""
		Make an Elastix object.
		Specify where this Elastix object should look for/write its files.
		Set the fixed and moving data sets as parameters. (or the project?)
		Then create a parameter file, argh, this is where the fault is...
		
		First, there should be a tree, and for each step there should be parameters,
		and eacht step has to run with its own parameters...

		So, the tree is concern #1. After that, I have to figure out how I will process
		the whole tree step by step.
		"""
		# self.queue = multiprocessing.Queue()
		# reg = Elastix()
		# reg.queue = self.queue
		# params = reg.get_default_params('affine')
		# params.MaximumNumberOfIterations = 200
		# params.FinalGridSpacingInVoxels = 10
		# im1 = self._currentProject.fixedDataSetName()
		# im2 = self._currentProject.movingDataSetName()
		# p = multiprocessing.Process(target=reg.register())
		# p.start()
		# job = multiprocessing.Process(reg.register(im1, im2, params))
		# im1_deformed, field = reg.register(im1, im2, params, verbose=1)
		# filename = 'registration_result'
		# resultFile, succes = reg.writeImageData(im1_deformed, self._currentProject.name(), filename)
		# if succes:
		# 	self._currentProject.setResultDataSetName(resultFile)
		# 	self.resultFileChanged.emit(resultFile)
		return
