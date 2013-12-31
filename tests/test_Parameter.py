import unittest
from core.elastix import Parameter


class ParameterTest(unittest.TestCase):

	def testParameter(self):
		# Test init function
		param = Parameter("key", 10)
		self.assertEquals(param.key(), "key")
		self.assertEquals(param.value(), 10)
		# Test string representation
		self.assertEquals(param.__str__(), "(key 10)")
		# Test changing the key
		param.setKey("otherKey")
		self.assertEquals(param.key(), "otherKey")

		# Test simple object creation
		param = Parameter()
		self.assertIsNone(param.key())
		self.assertIsNone(param.value())

		# Test setting the values with the KeyValue function
		param.setKeyValue("otherKey", 20)
		self.assertEquals(param.key(), "otherKey")
		self.assertEquals(param.value(), 20)

		# Test with setting only the key
		param = Parameter("key")
		self.assertEquals(param.key(), "key")
		self.assertIsNone(param.value())

		param = Parameter("key", 0.4)
		otherParam = Parameter(''.join(['k', 'e', 'y']), 0.4)
		self.assertEquals(param, otherParam)

		# Strip characters from key, but not from value
		param.setKey("    Key With Spaces  \n")
		self.assertEquals(param.key(), "KeyWithSpaces")
		param.setValue("Value with spaces")
		self.assertEquals(param.value(), ["Value", "with", "spaces"])

		self.assertFalse(param == Parameter("Hello", 10))
		self.assertTrue(param != Parameter("Hello", 10))
		self.assertFalse(param != param)

		# Test setting a value when Key is still None
		self.assertRaises(AttributeError, Parameter, None, "value")

		param = Parameter()
		self.assertRaises(AttributeError, param.setValue, 20)

	def testConversionMethods(self):
		# Create list of elements with different types
		values = [True, "true", 20, "20", 0.4, "0.4", "hello", "0.02f"]

		# Put every type of element through the grinder
		for value in values:
			newValue, success = Parameter.valueAsBool(value)
			if success:
				self.assertIsInstance(newValue, bool)
				self.assertTrue(value is True or value == "true")
			newValue, success = Parameter.valueAsInt(value)
			if success:
				self.assertIsInstance(newValue, int)
				self.assertEquals(newValue, 20)
			newValue, success = Parameter.valueAsFloat(value)
			if success:
				self.assertIsInstance(newValue, float)
				self.assertEquals(newValue, 0.4)

		param = Parameter("Key", 0)
		self.assertIsInstance(param.value(), int)
		param = Parameter("Key", "0")
		self.assertIsInstance(param.value(), int)
		param = Parameter("Key", 0.0)
		self.assertIsInstance(param.value(), float)
		param = Parameter("Key", "0.0")
		self.assertIsInstance(param.value(), float)
		param = Parameter("Key", True)
		self.assertIsInstance(param.value(), bool)
		param = Parameter("Key", False)
		self.assertIsInstance(param.value(), bool)
		param = Parameter("Key", "True")
		self.assertIsInstance(param.value(), bool)
		param = Parameter("Key", "False")
		self.assertIsInstance(param.value(), bool)
		param = Parameter("Key", "other")
		self.assertIsInstance(param.value(), basestring)

	def testListAsValue(self):
		# Multiple values
		ls = [0.5, 0.3, 5.2, 3, -2]
		param = Parameter("key", ls)
		self.assertEquals(param.__str__(), '(key 0.5 0.3 5.2 3 -2)')

		# Empty list
		ls = []
		self.assertRaises(AttributeError, param.setValue, ls)

		# Single item
		ls = [0.3]
		param.setValue(ls)
		self.assertEquals(param.__str__(), '(key 0.3)')
		param.setValue("value")
		self.assertEquals(param.__str__(), '(key "value")')

	def testStringRepresentations(self):
		# Test the string representations
		# String value
		param = Parameter("key", "value")
		self.assertEquals(param.__str__(), '(key "value")')
		# Integer value
		param.setValue(20)
		self.assertEquals(param.__str__(), '(key 20)')
		# Float value
		param.setValue(20.0)
		self.assertEquals(param.__str__(), '(key 20.0)')
		# bool values
		param.setValue(True)
		self.assertEquals(param.__str__(), '(key "true")')
		param.setValue(False)
		self.assertEquals(param.__str__(), '(key "false")')

	def testParameterFromString(self):
		param = Parameter.parameterFromString("")
		self.assertIsNone(param)

		param = Parameter.parameterFromString("()")
		self.assertIsNone(param)

		param = Parameter.parameterFromString("( )")
		self.assertIsNone(param)
		
		param = Parameter.parameterFromString("(a 1)")
		self.assertIsNotNone(param)
		self.assertEquals(param.key(), "a")
		self.assertEquals(param.value(), 1)
		
		param = Parameter.parameterFromString("a (1)")
		self.assertIsNone(param)

		param = Parameter.parameterFromString(")(a 1")
		self.assertIsNone(param)

		param = Parameter.parameterFromString("(a b c")
		self.assertIsNone(param)

		param = Parameter.parameterFromString("(a b c)")
		self.assertIsNotNone(param)
		self.assertEquals(param.key(), "a")
		self.assertEquals(param.value(), ["b", "c"])

		param = Parameter.parameterFromString("(ab)")
		self.assertIsNone(param)

	def testParameterList(self):
		param = Parameter.parameterFromString("(a 4 4 4 1 1)")
		self.assertIsNotNone(param)

		self.assertEquals(param.__str__(), "(a 4 4 4 1 1)")
