"""
Parameter

Class that encapsulates a single parameter. Most important
part is that the string representation is in the format that
Elastix uses for its parameters.

:Authors:
	Berend Klein Haneveld
"""


class Parameter(object):
	"""
	Simple parameter object that consists out of a key and a value.
	Just a little more interesting over normal dict entries because of the specific representation
	to be used in a parameter file for Elastix.
	"""
	
	def __init__(self, key=None, value=None):
		"""
		:type key: basestring
		:type value: basestring or bool or int, float
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

	def __ne__(self, other):
		return not self.__eq__(other)

	def setKeyValue(self, key, value):
		"""
		:type key: basestring
		:type value: float, int, basestring
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

		:type key: basestring
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
		:type value: basestring, float, int
		"""
		if not self._key:
			raise AttributeError("Can't set a value when the key is None")

		if isinstance(value, list):
			if len(value) == 0:
				raise AttributeError("Can't set an empty list as value")

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
		:rtype: basestring
		"""
		return self._key

	def value(self):
		"""
		:rtype: float, int, basestring
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
		elif isinstance(value, list):
			result = ''
			for item in value[0:-1]:
				result += Parameter.valueToString(item) + ' '
			result += Parameter.valueToString(value[-1])
			return result

	@classmethod
	def valueAsBool(cls, value):
		"""
		Tries to convert the given value into a boolean type. If the type is
		a string, then it checks for the existance of 'true' or 'false' in the
		string.
		Returns the (converted) value and a bool whether the value is
		succesfully converted or not. If not, the original value is returned.

		:rtype: bool, bool
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

		:rtype: int, bool
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

		:rtype: float, bool
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

	@classmethod
	def parameterFromString(cls, line):
		"""
		:type value: basestring
		:rtype: Parameter
		"""
		# Remove leading and trailing white space chars
		line = line.strip()
		indexOfComment = line.find("//")
		if indexOfComment >= 0:
			line = line[0:indexOfComment]
		if len(line) > 1:
			indexOfCaretOpen = line.find("(")
			indexOfSpace = line.find(" ")
			indexOfCaretClose = line.rfind(")")
			if indexOfCaretOpen < 0 or indexOfCaretClose < 0 \
				or indexOfSpace < 0 or indexOfCaretClose < indexOfCaretOpen \
				or indexOfSpace < indexOfCaretOpen \
				or indexOfSpace > indexOfCaretClose \
				or indexOfSpace == indexOfCaretOpen+1:
				# TODO: make a better exception message.
				# raise Exception("Line is not correctly formatted.")
				return None
			
			key = line[indexOfCaretOpen+1:indexOfSpace]
			value = line[indexOfSpace+1:indexOfCaretClose]
			if len(key) == 0:
				return None
			if '"' in value:
				value = value[1:-1]
			param = Parameter(key, value)
			return param

		return None
