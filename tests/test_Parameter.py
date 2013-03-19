import unittest
from core.elastix.Parameter import Parameter

class ParameterTest(unittest.TestCase):

	def testParameter(self):
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

		self.assertFalse(param == Parameter("Hello", 10))
		self.assertTrue(param != Parameter("Hello", 10))
		self.assertFalse(param != param)

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

	def testConversionMethods(self):
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

	def testStringRepresentations(self):
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

	def testParameterFromString(self):
		param = Parameter.parameterFromString("")
		assert param is None

		param = Parameter.parameterFromString("()")
		assert param is None

		param = Parameter.parameterFromString("( )")
		assert param is None
		
		param = Parameter.parameterFromString("(a 1)")
		assert param is not None
		assert param.key() == "a"
		assert param.value() == 1
		
		param = Parameter.parameterFromString("a (1)")
		assert param is None

		param = Parameter.parameterFromString(")(a 1")
		assert param is None

		param = Parameter.parameterFromString("(a b c")
		assert param is None

		param = Parameter.parameterFromString("(a b c)")
		assert param is not None
		assert param.key() == "a"
		assert param.value() == "b c"

		param = Parameter.parameterFromString("(ab)")
		assert param is None
