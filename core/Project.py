class Project(object):

	def __init__(self, title=None, fixedData=None, movingData=None, isReference=None):
		super(Project, self).__init__()

		self.title = title
		self.fixedData = fixedData
		self.movingData = movingData
		self.isReference = isReference
		self.folder = None
		self.resultData = None

	def __eq__(self, other):
		if not isinstance(other, Project):
			return False
		return self.title == other.title \
			and self.fixedData == other.fixedData \
			and self.movingData == other.movingData \
			and self.isReference == other.isReference

	# def dictionary(self):
	# 	return self.__dict__

# """
# Project

# Model class for projects.

# @author: Berend Klein Haneveld 2013
# """

# from Strategy import Strategy

# try:
# 	from PySide.QtCore import QObject
# 	from PySide.QtCore import Signal
# 	import yaml
# except ImportError, e:
# 	raise e

# class Project(QObject):

# 	# Create a signal to be emitted
# 	modified = Signal()

# 	def __init__(self, name=None, fixedData=None, movingData=None, resultData=None, isReference=True, dictionary=None):
# 		"""
# 		@param name: Project directory name (also used as display name)
# 		@type name: unicode
# 		@param fixedData: Fixed data set name
# 		@type fixedData: basestring
# 		@param movingData: Moving data set name
# 		@type movingData: basestring
# 		@param isReference: Whether source data sets are to be contained in project folder
# 		@type isReference: bool
# 		"""
# 		super(Project, self).__init__()

# 		self.strategy = Strategy

# 		if name and not(isinstance(name, basestring)):
# 			raise TypeError("Wrong type for name. Please specify variable name.")

# 		if dictionary:
# 			properties = ["name", "fixedData", "movingData", "resultData", "isReference"]
# 			tempDict = {}
# 			# TODO: just check for certain keys in the dictionary
# 			# Add a '_' and set as property
# 			for val in properties:
# 				if val in dictionary:
# 					# Set as private property
# 					tempDict["_" + val] = dictionary[val]
			
# 			# Construct project from dictionary
# 			self.__dict__.update(tempDict)
# 		else:
# 			# Construct project from arguments
# 			self._name = name
# 			self._isReference = isReference
# 			self._fixedData = fixedData
# 			self._movingData = movingData
# 			self._resultData = resultData
	
# 	def __eq__(self, other):
# 		"""
# 		Returns true iff all attributes of both objects correspond.
# 		@rtype: bool
# 		"""
# 		return self._name == other.name() \
# 			and self._fixedData == other.fixedData() \
# 			and self._movingData == other.movingData() \
# 			and self._isReference == other.isReference() \
# 			and self._resultData == other.resultData()

# 	def __ne__(self, other):
# 		"""
# 		Returns the inverse of __eq__ functions.
# 		@rtype: bool
# 		"""
# 		return not(self.__eq__(other))

# 	def dictionary(self):
# 		"""
# 		Returns a dictionary representation of its self. Project should be able
# 		to be initiated with this dictionary representation.
# 		Underscore is removed from the keys, so that it is better readable
# 		when a yaml representation is generated.
# 		@rtype: dict
# 		"""
# 		dictionary = dict(name=self._name, \
# 			fixedData=self._fixedData, \
# 			movingData=self._movingData, \
# 			isReference=self._isReference, \
# 			resultData=self._resultData)
# 		return dictionary

# 	def __repr__(self):
# 		"""
# 		Returns a string representation of self. Yaml magic.
# 		@rtype: basestring
# 		"""
# 		return "%s(name=%s, fixedData=%s, movingData=%s, isReference=%s)" % (
# 			self.__class__.__name__, self._name, self._fixedData, 
# 			self._movingData, self._isReference)



# 	def setName(self, name):
# 		"""
# 		Sets the visible name of the project.
# 		@type name: basestring
# 		"""
# 		self._name = name
# 		self.changed()

# 	def name(self):
# 		"""
# 		@rtype: basestring
# 		"""
# 		return self._name



# 	def displayName(self):
# 		"""
# 		Returns the last path component of the directory that the project
# 		is saved to.
# 		"""
# 		result = ""
# 		if self._name:
# 			index = self._name.rfind("/")
# 			if index >= 0:
# 				result = self._name[index+1:]
# 		return result

# 	def fixedData(self):
# 		"""
# 		@return: fixedDataSet filename
# 		@rtype: basestring
# 		"""
# 		return self._fixedData

# 	def setfixedData(self, name=None):
# 		"""
# 		@param name: File name of fixed data set
# 		@type name: basestring
# 		"""
# 		self._fixedData = name
# 		self.changed()

# 	def movingData(self):
# 		"""
# 		@return: movingData filename
# 		@rtype: basestring
# 		"""
# 		return self._movingData

# 	def setmovingData(self, name=None):
# 		"""
# 		@param name: moving data set name
# 		@type name: basestring
# 		"""
# 		self._movingData = name
# 		self.changed()

# 	def resultData(self):
# 		"""
# 		@return: File name of result data set
# 		@rtype: basestring
# 		"""
# 		return self._resultData

# 	def setresultData(self, name=None):
# 		"""
# 		@param name: result data set name
# 		@type name: basestring
# 		"""
# 		self._resultData = name
# 		self.changed()

# 	def isReference(self):
# 		"""
# 		Returns whether the project has the data files included (relative from 
# 		project root) or that the data files are only referenced.
# 		@rtype: bool
# 		"""
# 		return self._isReference

# 	def setIsReference(self, reference=True):
# 		"""
# 		@param reference: Whether source data sets are to be contained in 
# 		project folder
# 		@type reference: bool
# 		"""
# 		self._isReference = reference
# 		self.changed()

# 	def changed(self):
# 		"""
# 		Fire the modified signal that this project has changed
# 		"""
# 		self.modified.emit()
