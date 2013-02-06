"""
Project

Model class for projects.

@author: Berend Klein Haneveld 2013
"""

try:
	from PySide.QtCore import QObject
	from PySide.QtCore import Signal
except ImportError, e:
	raise e

class Project(QObject):

	# Create a signal to be emitted
	modified = Signal()

	def __init__(self, name=None, fixedDataSet=None, movingDataSet=None, isReference=True):
		"""
		@param name: Project file name
		@type name: basestring
		@param fixedDataSet: Fixed data set name
		@type fixedDataSet: basestring
		@param movingDataSet: Moving data set name
		@type movingDataSet: basestring
		@param isReference: Whether source data sets are to be contained in project folder
		@type isReference: bool
		"""
		super(Project, self).__init__()

		self._name = name
		self._isReference = isReference
		self._fixedDataSetName = fixedDataSet
		self._movingDataSetName = movingDataSet

	def setName(self, name):
		"""
		Sets the visible name of the project.
		@type name: basestring
		"""
		self._name = name
		self.changed()

	def name(self):
		"""
		@rtype: basestring
		"""
		return self._name

	def fixedDataSet(self):
		"""
		@return: fixedDataSet filename
		@rtype: basestring
		"""
		return self._fixedDataSetName

	def setFixedDataSet(self, name=None):
		"""
		@param name: File name of fixed data set
		@type name: basestring
		"""
		self._fixedDataSetName = name
		self.changed()

	def movingDataSet(self):
		"""
		@return: movingDataSetName filename
		@rtype: basestring
		"""
		return self._movingDataSetName

	def setMovingDataSet(self, name=None):
		"""
		@param name: moving data set name
		@type name: basestring
		"""
		self._movingDataSetName = name
		self.changed()

	def setIsReference(self, reference=True):
		"""
		@param reference: Whether source data sets are to be contained in project folder
		@type reference: bool
		"""
		self._isReference = reference
		self.changed()

	def changed(self):
		"""
		Fire the modified signal that this project has changed
		"""
		self.modified.emit()
