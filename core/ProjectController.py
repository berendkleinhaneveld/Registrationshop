"""
ProjectController

Model controller class that manages projects.
Should be only one instance

@author: Berend Klein Haneveld
"""

try:
	from PySide.QtCore import QObject
	from PySide.QtCore import Slot
	from PySide.QtCore import Signal
	import yaml
except ImportError, e:
	raise e

from Project import Project
from singleton import Singleton

@Singleton
class ProjectController(QObject):
	# Signals for when file name has changed
	changedFixedDataSetFileName = Signal(basestring)
	changedMovingDataSetFileName = Signal(basestring)
	changedProject = Signal(Project)

	ProjectFile = u"project.yaml"

	def __init__(self, project=None):
		"""
		@param project: Project to be made current
		@type project: Project
		"""
		QObject.__init__(self)

		self._currentProject = project
		# Create new standard project if no project is provided
		if project == None:
			self._currentProject = Project()

	def currentProject(self):
		"""
		@return: Current project
		@rtype: Project
		"""
		return self._currentProject

	def loadProject(self, name=None):
		"""
		@param name: Directory of project
		@type name: unicode
		@return: Success
		@rtype: bool
		"""
		projectFileName = name + "/" + self.ProjectFile
		projectFile = open(projectFileName, "r")
		
		try:
			yamlRepresentation = yaml.load(projectFile)
			project = Project(dictionary=yamlRepresentation)
			self._currentProject = project
		except Exception, e:
			print e
			return False
		
		# Reload all the views!
		self.changedFixedDataSetFileName.emit(self._currentProject.fixedDataSetName())
		self.changedMovingDataSetFileName.emit(self._currentProject.movingDataSetName())
		# TODO: removed the 2 lines above: they shouldn't be necessary
		self.changedProject.emit(self._currentProject)

		return True

	def saveProject(self):
		"""
		Saves project to disk. 
		Assumes: project name is set and correct

		@param name: File/Directory name to save the project file to
		@type name: unicode
		@return: Success
		@rtype: bool
		"""
		try:
			dictionary = self._currentProject.dictionary()
			projectFileName = self._currentProject.name() + "/" + self.ProjectFile
			projectFile = open(projectFileName, "w+")
			# Create a readable project file
			yaml.dump(dictionary, projectFile, default_flow_style=False)
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

	# Slots for signals of SlicerWidget
	@Slot(basestring)
	def loadFixedDataSet(self, name=None):
		"""
		Sets the name in the current project as the fixed data set filename
		@param name: File name of fixed data set
		@type name: basestring
		@return:
		@rtype:
		"""
		# TODO: some extra magic like checking if file exists
		print "Load the fixed data set", name
		self._currentProject.setFixedDataSetName(name)

		# Emit signal that data set file name has changed
		self.changedFixedDataSetFileName.emit(name)

	@Slot(basestring)
	def loadMovingDataSet(self, name=None):
		"""
		Sets the name in the current project as the moving data set filename
		@param name: File name of moving data set
		@type name: basestring
		@return:
		@rtype:
		"""
		# TODO: some extra magic like checking if file exists
		print "Load the moving data set", name
		self._currentProject.setMovingDataSetName(name)

		# Emit signal that data set file name has changed
		self.changedMovingDataSetFileName.emit(name)

	
