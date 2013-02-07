"""
ProjectController

Model controller class that manages projects.
Should be only one instance

@author: Berend Klein Haneveld
"""

try:
	from PySide.QtCore import QObject
except ImportError, e:
	raise e

from Project import Project
from singleton import Singleton

@Singleton
class ProjectController(QObject):

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
		@rtype: bool
		"""
		# TODO: some extra magic like checking if file exists
		print "Load the fixed data set", name
		self._currentProject.setFixedDataSet(name)
		# TODO: return whether the file name is correct
		return True

	def loadMovingDataSet(self, name=None):
		"""
		Sets the name in the current project as the moving data set filename
		@param name: File name of moving data set
		@type name: basestring
		@return:
		@rtype: bool
		"""
		# TODO: some extra magic like checking if file exists
		print "Load the moving data set", name
		self._currentProject.setMovingDataSet(name)
		# TODO: return whether the file name is correct
		return True

	def loadFixedDataSetFileName(self, fileName):
		"""
		@type fileName: basestring
		"""
		slicerWidget = self.sender()
		loaded = self.loadFixedDataSet(fileName)
		if loaded:
			slicerWidget.setFileName(fileName)
		pass

	def loadMovingDataSetFileName(self, fileName):
		"""
		@type fileName: basestring
		"""
		slicerWidget = self.sender()
		loaded = self.loadMovingDataSet(fileName)
		if loaded:
			slicerWidget.setFileName(fileName)
		pass
