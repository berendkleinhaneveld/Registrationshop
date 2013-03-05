"""
Parameter

Class that encapsulates a single parameter. Most important
part is that the string representation is in the format that
Elastix uses for its parameters.

@author: Berend Klein Haneveld
"""

class Parameter(object):
	"""
	Simple parameter object that consists out of a key and a value.
	Just a little more interesting over normal dict entries because of the specific representation
	to be used in a parameter file for Elastix.
	"""
	def __init__(self, key=None, value=None):
		"""
		@type key: basestring
		@type value: basestring or bool or int, float
		"""
		super(Parameter, self).__init__()

		if value is None and key is None:
			self._key = None
			self._value = None
		else:
			self.setKeyValue(key, value)

	def __str__(self):
		"""
		Return a specific representation of the key value pair in the way Elastix
		likes: (key value). If value is a string, it should be represented like "value".
		"""
		value = Parameter.valueToString(self._value)
		return "(%s %s)" % (self._key, value)

	def __eq__(self, other):
		if not isinstance(other, Parameter):
			return False

		return other.key() == self.key() and other.value() == self.value()

	def setKeyValue(self, key, value):
		"""
		@type key: basestring
		@type value: float, int, basestring
		"""
		# Raise attribute error if the key is None while the value has a value
		if not key and value:
			raise AttributeError("Key attribute can't be None if a value is specified.")

		if key and not isinstance(key, basestring):
			raise TypeError("attribute key should be of string type")

		self.setKey(key)
		self.setValue(value)

	def setKey(self, key):
		"""
		Strips whitespace characters and spaces from key.

		@type key: basestring
		"""
		if not key:
			raise AttributeError("Can't set a key to None")

		if not isinstance(key, basestring):
			raise TypeError("attribute key should be of string type")

		key = key.strip()
		key = key.replace(" ", "")

		self._key = key

	def setValue(self, value):
		"""
		@type value: basestring, float, int
		"""
		if not self._key:
			raise AttributeError("Can't set a value when the key is None")

		if isinstance(value, basestring):
			# Try to convert to another type
			value, success = Parameter.valueAsBool(value)
			if not success:
				value, success = Parameter.valueAsInt(value)
			if not success:
				value, success = Parameter.valueAsFloat(value)

		self._value = value

	def key(self):
		"""
		@rtype: basestring
		"""
		return self._key

	def value(self):
		"""
		@rtype: float, int, basestring
		"""
		return self._value

	@classmethod
	def valueToString(cls, value):
		if isinstance(value, bool):
			return '"%s"' % str(value).lower()
		elif isinstance(value, int):
			return str(value)
		elif isinstance(value, float):
			tmp = str(value)
			if not '.' in tmp:
				tmp += '.0'
			return tmp
		elif isinstance(value, basestring):
			return '"%s"' % value

	@classmethod
	def valueAsBool(cls, value):
		"""
		Tries to convert the given value into a boolean type. If the type is 
		a string, then it checks for the existance of 'true' or 'false' in the
		string.
		Returns the (converted) value and a bool whether the value is 
		succesfully converted or not. If not, the original value is returned.

		@rtype: bool, bool
		"""
		if isinstance(value, bool):
			return value, True
		if isinstance(value, basestring):
			if "true" in value.lower():
				return True, True
			elif "false" in value.lower():
				return False, True
		
		return value, False

	@classmethod
	def valueAsInt(cls, value):
		"""
		Tries to convert the given value into an integer type. If the type is 
		a string, then it checks whether the string is a representation of a
		digit. If there is a dot in the string, it is not converted.
		Returns the (converted) value and a bool whether the value is 
		succesfully converted or not. If not, the original value is returned.

		@rtype: int, bool
		"""
		if isinstance(value, int) and not isinstance(value, bool):
			return value, True
		elif isinstance(value, basestring) and value.isdigit():
			return int(value), True
		
		return value, False
	
	@classmethod	
	def valueAsFloat(cls, value):
		"""
		Tries to convert the given value into a float type. If the type is 
		a string, then it checks for the existance of a float number in the
		string. If the value in the string is actually an integer, it will not
		be converted.
		Returns the (converted) value and a bool whether the value is 
		succesfully converted or not. If not, the original value is returned.

		@rtype: float, bool
		"""
		if isinstance(value, float):
			return value, True
		elif isinstance(value, basestring) and not value.isdigit():
			try:
				floatValue = float(value)
				return floatValue, True
			except ValueError:
				pass

		return value, False

# Unit tests

def testParameter():
	# Test init function
	param = Parameter("key", 10)
	assert param.key() is "key"
	assert param.value() == 10
	# Test string representation
	assert param.__str__() == "(key 10)"
	# Test changing the key
	param.setKey("otherKey")
	assert param.key() == "otherKey"

	# Test simple object creation
	param = Parameter()
	assert param.key() == None
	assert param.value() == None

	# Test setting the values with the KeyValue function
	param.setKeyValue("otherKey", 20)
	assert param.key() == "otherKey"
	assert param.value() == 20

	# Test with setting only the key
	param = Parameter("key")
	assert param.key() == "key"
	assert param.value() == None

	param = Parameter("key", 0.4)
	otherParam = Parameter(''.join(['k','e','y']), 0.4)
	assert param == otherParam

	# Strip characters from key, but not from value
	param.setKey("    Key With Spaces  \n")
	assert param.key() == "KeyWithSpaces"
	param.setValue("Value with spaces")
	assert param.value() == "Value with spaces"

	# Test setting a value when Key is still None
	try:
		# This should raise an exception
		param = Parameter(None, "value")
		assert False, "No exception is raised while a parameter was constructed\
			with a key with value 'None'"
	except AssertionError, e:
		raise e
	except Exception, e:
		assert isinstance(e, AttributeError)

	try:
		param = Parameter()
		param.setValue(20)
	except Exception, e:
		assert isinstance(e, AttributeError)

def testConversionMethods():
	# Create list of elements with different types
	values = [True, "true", 20, "20", 0.4, "0.4", "hello", "0.02f"]

	# Put every type of element through the grinder
	for value in values:
		newValue, success = Parameter.valueAsBool(value)
		if success:
			assert type(newValue) == bool
			assert value == True or value == "true"
		newValue, success = Parameter.valueAsInt(value)
		if success:
			assert type(newValue) == int
			assert newValue == 20
		newValue, success = Parameter.valueAsFloat(value)
		if success:
			assert type(newValue) == float
			assert newValue == 0.4

	param = Parameter("Key", 0)
	assert isinstance(param.value(), int)
	param = Parameter("Key", "0")
	assert isinstance(param.value(), int)
	param = Parameter("Key", 0.0)
	assert isinstance(param.value(), float)
	param = Parameter("Key", "0.0")
	assert isinstance(param.value(), float)
	param = Parameter("Key", True)
	assert isinstance(param.value(), bool)
	param = Parameter("Key", False)
	assert isinstance(param.value(), bool)
	param = Parameter("Key", "True")
	assert isinstance(param.value(), bool)
	param = Parameter("Key", "False")
	assert isinstance(param.value(), bool)
	param = Parameter("Key", "other")
	assert isinstance(param.value(), basestring)

def testStringRepresentations():
	# Test the string representations
	# String value
	param = Parameter("key", "value")
	assert param.__str__() == '(key "value")'
	# Integer value
	param.setValue(20)
	assert param.__str__() == '(key 20)'
	# Float value
	param.setValue(20.0)
	assert param.__str__() == '(key 20.0)'
	# bool values
	param.setValue(True)
	assert param.__str__() == '(key "true")'
	param.setValue(False)
	assert param.__str__() == '(key "false")'

if __name__ == '__main__':
	print "Testing the parameter class"
	testParameter()
	testConversionMethods()
	testStringRepresentations()
	print "All test have succeeded"
