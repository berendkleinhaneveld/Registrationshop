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
except ImportError, e:
	raise e

from Project import Project
from singleton import Singleton

@Singleton
class ProjectController(QObject):
	# Signals for when file name has changed
	changedFixedDataSetFileName = Signal(basestring)
	changedMovingDataSetFileName = Signal(basestring)

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
		@param name: File name of project
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

	
