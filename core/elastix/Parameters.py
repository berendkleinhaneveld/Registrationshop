"""
Parameters

@author: Berend Klein Haneveld
"""

from Parameter import Parameter

class Parameters(object):
	"""
	Object that manages a collection of parameters. By implementing some
	simple methods it can be used as a kind of simple list.
	So instead of calling parametersObject.parameters[i] you can call
	parametersObject[i] to get the same result.

	Implements the following methods:
	__getitem__(index)
	__setitem__(index, value)
	__delitem__(index)
	__len__()
	__contains__(value)
	append(value)
	"""
	def __init__(self):
		super(Parameters, self).__init__()
		self.parameters = []

	# IO methods

	def loadFromFile(self, filename):
		"""
		Reads a list of parameters from file. Returns whether it has succeeded
		in doing so.

		@type filename: basestring
		@rtype: bool
		"""
		parameterFile = open(filename, "r")
		
		try:
			for line in parameterFile:
				if not line.startswith("//") and len(line) > 1:
					# Remove leading and trailing white space chars
					line = line.strip()
					indexOfCaretOpen = line.find("(")
					indexOfSpace = line.find(" ")
					indexOfCaretClose = line.rfind(")")

					key = line[indexOfCaretOpen+1:indexOfSpace]
					value = line[indexOfSpace+1:indexOfCaretClose]
					if '"' in value:
						value = value[1:-1]
					param = Parameter(key, value)
					self.append(param)

		except Exception, e:
			raise e
			
		return False

	def saveToFile(self, filename):
		"""
		Saves a list of parameters to file. Returns whether it has succeeded in
		doing so.

		@type filename: basestring
		@rtype: bool
		"""
		lines = []
		for param in self.parameters:
			lines.append(str(param))

		content = "\n".join(lines)
		
		parameterFile = open(filename, "w+")
		try:
			parameterFile.write(content.encode('utf-8'))
		finally:
			parameterFile.close()

	# Override methods for simple list behaviour

	def __getitem__(self, index):
		return self.parameters[index]

	def __setitem__(self, index, value):
		self.parameters[index] = value

	def __delitem__(self, index):
		del self.parameters[index]

	def __len__(self):
		return len(self.parameters)

	def __contains__(self, value):
		return value in self.parameters

	def __eq__(self, other):
		if not isinstance(other, Parameters):
			return False

		for x in self.parameters:
			if x not in other.parameters:
				return False
		
		for x in other.parameters:
			if x not in self.parameters:
				return False

		return True

	def append(self, value):
		"""
		Only if value has the type Parameter it gets added to the list,
		so that the parameter list stays consistent.
		@type value: Parameter
		"""
		if isinstance(value, Parameter):
			self.parameters.append(value)
		else:
			raise TypeError("Only Parameter type objects \
				can be added to a Parameters object. An object with \
				type %s was provided" % type(value))

def testListMethods():
	nonvalidValue = "hello world"
	value = Parameter("key", "hello world")
	otherValue = Parameter("key", "goodbye world")
	anotherValue = Parameter("key", 0)

	parameters = Parameters()
	assert len(parameters) == 0
	# Test adding a non Parameter value
	try:
		parameters.append(nonvalidValue)
		assert False
	except Exception, e:
		assert isinstance(e, TypeError)
	
	assert len(parameters) == 0
	parameters.append(value)
	assert len(parameters) == 1
	assert parameters[0] == value
	parameters.append(otherValue)
	assert len(parameters) == 2
	assert parameters[1] == otherValue
	parameters[0] = anotherValue
	assert parameters[0] == anotherValue
	del parameters[1]
	assert len(parameters) == 1
	assert anotherValue in parameters
	assert otherValue not in parameters

def testInputOutputMethods():
	parameters = Parameters()
	parameters.loadFromFile("Sample.c")
	assert len(parameters) == 29
	parameters.saveToFile("SampleOutput.c")
	otherParameters = Parameters()
	otherParameters.loadFromFile("SampleOutput.c")
	assert len(parameters) == len(otherParameters)
	assert Parameter("MovingInternalImagePixelType", "float") in parameters
	assert parameters == otherParameters

if __name__ == '__main__':
	print "Testing the Parameters class"
	testListMethods()
	testInputOutputMethods()
	print "All test have succeeded"
