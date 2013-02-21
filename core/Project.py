"""
Project

Model class for projects.

@author: Berend Klein Haneveld 2013
"""

try:
	from PySide.QtCore import QObject
	from PySide.QtCore import Signal
	import yaml
except ImportError, e:
	raise e

class Project(QObject):

	# Create a signal to be emitted
	modified = Signal()

	def __init__(self, name=None, fixedDataSetName=None, movingDataSetName=None, resultDataSetName=None, isReference=True, dictionary=None):
		"""
		@param name: Project directory name (also used as display name)
		@type name: unicode
		@param fixedDataSetName: Fixed data set name
		@type fixedDataSetName: basestring
		@param movingDataSetName: Moving data set name
		@type movingDataSetName: basestring
		@param isReference: Whether source data sets are to be contained in project folder
		@type isReference: bool
		"""
		super(Project, self).__init__()

		if name and not(isinstance(name, basestring)):
			raise TypeError("Wrong type for name. Please specify variable name.")

		if dictionary:
			properties = ["name", "fixedDataSetName", "movingDataSetName", "resultDataSetName", "isReference"]
			tempDict = {}
			# TODO: just check for certain keys in the dictionary
			# Add a '_' and set as property
			for val in properties:
				if val in dictionary:
					# Set as private property
					tempDict["_" + val] = dictionary[val]
			
			# Construct project from dictionary
			self.__dict__.update(tempDict)
		else:
			# Construct project from arguments
			self._name = name
			self._isReference = isReference
			self._fixedDataSetName = fixedDataSetName
			self._movingDataSetName = movingDataSetName
			self._resultDataSetName = resultDataSetName
	
	def __eq__(self, other):
		"""
		Returns true iff all attributes of both objects correspond.
		@rtype: bool
		"""
		return self._name == other.name() \
			and self._fixedDataSetName == other.fixedDataSetName() \
			and self._movingDataSetName == other.movingDataSetName() \
			and self._isReference == other.isReference() \
			and self._resultDataSetName == other.resultDataSetName()

	def __ne__(self, other):
		"""
		Returns the inverse of __eq__ functions.
		@rtype: bool
		"""
		return not(self.__eq__(other))

	def dictionary(self):
		"""
		Returns a dictionary representation of its self. Project should be able
		to be initiated with this dictionary representation.
		Underscore is removed from the keys, so that it is better readable
		when a yaml representation is generated.
		@rtype: dict
		"""
		dictionary = dict(name=self._name, \
			fixedDataSetName=self._fixedDataSetName, \
			movingDataSetName=self._movingDataSetName, \
			isReference=self._isReference, \
			resultDataSetName=self._resultDataSetName)
		return dictionary

	def __repr__(self):
		"""
		Returns a string representation of self. Yaml magic.
		@rtype: basestring
		"""
		return "%s(name=%s, fixedDataSetName=%s, movingDataSetName=%s, isReference=%s)" % (
			self.__class__.__name__, self._name, self._fixedDataSetName, self._movingDataSetName, self._isReference)


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

	def displayName(self):
		"""
		Returns the last path component of the directory that the project
		is saved to.
		"""
		result = ""
		if self._name:
			index = self._name.rfind("/")
			if index >= 0:
				result = self._name[index+1:]
		return result

	def fixedDataSetName(self):
		"""
		@return: fixedDataSet filename
		@rtype: basestring
		"""
		return self._fixedDataSetName

	def setFixedDataSetName(self, name=None):
		"""
		@param name: File name of fixed data set
		@type name: basestring
		"""
		self._fixedDataSetName = name
		self.changed()

	def movingDataSetName(self):
		"""
		@return: movingDataSetName filename
		@rtype: basestring
		"""
		return self._movingDataSetName

	def setMovingDataSetName(self, name=None):
		"""
		@param name: moving data set name
		@type name: basestring
		"""
		self._movingDataSetName = name
		self.changed()

	def resultDataSetName(self):
		"""
		@return: File name of result data set
		@rtype: basestring
		"""
		return self._resultDataSetName

	def setResultDataSetName(self, name=None):
		"""
		@param name: result data set name
		@type name: basestring
		"""
		self._resultDataSetName = name
		self.changed()

	def isReference(self):
		"""
		Returns whether the project has the data files included (relative from project root) 
		or that the data files are only referenced.
		@rtype: bool
		"""
		return self._isReference

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

# Unit tests

def testEqual():
	testProjectA = Project(name="TestProjectA", fixedDataSetName="FixedTest", movingDataSetName="MovingTest", isReference=True)
	testProjectB = Project(name="TestProjectB", fixedDataSetName="FixedTest", movingDataSetName="MovingTest", isReference=True)
	assert testProjectA == testProjectA
	assert testProjectA != testProjectB
	testProjectB.setName("TestProjectA")
	assert testProjectA == testProjectB
	pass

def testObjToDictToYamlAndBack():
	testProject = Project(name="TestProject", fixedDataSetName="FixedTest", movingDataSetName="MovingTest", isReference=True)
	testDictionary = testProject.dictionary()
	yamlRepresentation = yaml.dump(testDictionary)
	dictFromYaml = yaml.load(yamlRepresentation)
	objectFromDictionary = Project(dictionary=dictFromYaml)
	# Check that the projects are still the same
	assert testProject == objectFromDictionary
	# Test that you don't have to specify a variable name
	try:
		anotherObject = Project(dictFromYaml)
	except TypeError:
		assert True
	else:
		assert False
	
	pass

def testDictionary():
	testProject = Project(name="TestProject", fixedDataSetName="FixedTest", movingDataSetName="MovingTest", isReference=True)
	dictionary = testProject.dictionary()
	assert type(dictionary) == dict
	assert dictionary["name"] == "TestProject"
	assert dictionary["fixedDataSetName"] == "FixedTest"
	assert dictionary["movingDataSetName"] == "MovingTest"
	assert dictionary["isReference"] == True
	pass

# Run some unit tests
if __name__ == "__main__":
	testEqual()
	testDictionary()
	testObjToDictToYamlAndBack()
	print "Tests passed"
