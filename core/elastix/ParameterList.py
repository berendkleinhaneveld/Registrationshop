"""
ParameterList

:Authors:
	Berend Klein Haneveld
"""

import os
from Parameter import Parameter


class ParameterList(object):
	"""
	Object that manages a collection of parameters. By implementing some
	simple methods it can be used as a kind of simple list.
	So instead of calling paramList.parameters[i] you can call
	paramList[i] to get the same result.

	Implements the following methods:
	- __getitem__(index)
	- __setitem__(index, value)
	- __delitem__(index)
	- __len__()
	- __contains__(value)
	- append(value)

	"""

	def __init__(self):
		super(ParameterList, self).__init__()
		self.parameters = []
		self.name = None

	# IO methods

	def loadFromFile(self, filename):
		"""
		Reads a list of parameters from file. Returns whether it has succeeded
		in doing so.

		:type filename: basestring
		:rtype: bool
		"""
		directory, lastPathComponent = os.path.split(filename)
		self.name = lastPathComponent

		# TODO: write tests for this method in order to better specify its behaviour
		noErrors = True
		try:
			if filename.startswith('.DS'):
				noErrors = False
			else:
				with open(filename, "r") as parameterFile:
					try:
						for line in parameterFile:
							param = Parameter.parameterFromString(line)
							if param:
								self.append(param)

					except Exception:
						noErrors = False
		except Exception:
			noErrors = False
			
		return noErrors

	def saveToFile(self, filename):
		"""
		Saves a list of parameters to file. Returns whether it has succeeded in
		doing so. Overwrites anything on the given path.

		:type filename: basestring
		:rtype: bool
		"""
		lines = []
		for param in self.parameters:
			lines.append(str(param))

		content = "\n".join(lines)

		# Create directory, if it does not exist yet
		paramDirectory = os.path.dirname(filename)
		if not os.path.exists(paramDirectory):
			os.makedirs(paramDirectory)

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
		if not isinstance(other, ParameterList):
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

		:param value: Parameter to add to the list
		:type value: Parameter
		"""
		if isinstance(value, Parameter):
			self.parameters.append(value)
		else:
			raise TypeError("Only Parameter type objects \
				can be added to a ParameterList object. An object with \
				type %s was provided" % type(value))
