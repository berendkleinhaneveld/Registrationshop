__author__ = 'Berend Klein Haneveld'

from Project import Project

class ProjectController():

	def __init__(self, project=None):
		"""
		@param project: Project to be made current
		@type project: Project
		"""
		self.currentProject = project
		if project == None:
			# Create new standard project
			self.currentProject = Project()

	def currentProject(self):
		"""
		@return: Current project
		@rtype: Project
		"""
		return self.currentProject

	def loadProject(self, name=""):
		"""
		@param name: Name of project file
		@type name: basestring
		@return: Success
		@rtype: bool
		"""
		return False

	def saveProject(self, name=None):
		"""
		Saves project to disk. If no name is provided, then the name
		in the project is used. If there is no name in the project,
		then something is wrong...
		@param name: File name to save the project file to
		@type name: basestring
		@return: Success
		@rtype: bool
		"""
		return False

	def loadFixedDataSet(self, name=None):
		"""
		Sets the name in the current project as the fixed data set filename
		@param name: File name of fixed data set
		@type name: basestring
		@return:
		@rtype:
		"""
		# TODO: do some extra magic here like checking if file exists
		print "load the fixed data set"
		self.currentProject.setFixedDataSet(name)


	def loadMovingDataSet(self, name=None):
		"""
		Sets the name in the current project as the moving data set filename
		@param name: File name of moving data set
		@type name: basestring
		@return:
		@rtype:
		"""
		# TODO: do some extra magic here like checking if file exists
		print "load the moving data set"
		self.currentProject.setMovingDataSet(name)
