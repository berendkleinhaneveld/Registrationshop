import unittest

from core.elastix import ParameterList
from core.elastix import Parameter


class ParameterListTest(unittest.TestCase):

	def testListMethods(self):
		nonvalidValue = "hello world"
		value = Parameter("key", "hello world")
		otherValue = Parameter("key", "goodbye world")
		anotherValue = Parameter("key", 0)

		parameters = ParameterList()
		self.assertEquals(len(parameters), 0)
		# Test adding a non Parameter value
		self.assertRaises(TypeError, parameters.append, nonvalidValue)
		
		self.assertEquals(len(parameters), 0)
		parameters.append(value)
		self.assertEquals(len(parameters), 1)
		self.assertEquals(parameters[0], value)
		parameters.append(otherValue)
		self.assertEquals(len(parameters), 2)
		self.assertEquals(parameters[1], otherValue)
		parameters[0] = anotherValue
		self.assertEquals(parameters[0], anotherValue)
		del parameters[1]
		self.assertEquals(len(parameters), 1)
		self.assertTrue(anotherValue in parameters)
		self.assertTrue(otherValue not in parameters)

	def testInputOutputMethods(self):
		import os
		parameters = ParameterList()
		path = os.path.dirname(os.path.abspath(__file__))
		parameters.loadFromFile(unicode(path) + "/data/Sample.txt")
		self.assertEquals(len(parameters), 28)
		parameters.saveToFile(unicode(path) + "/SampleOutput.c")
		otherParameters = ParameterList()
		otherParameters.loadFromFile(unicode(path) + "/SampleOutput.c")
		self.assertEquals(len(parameters), len(otherParameters))
		self.assertTrue(Parameter("MovingInternalImagePixelType", "float") in parameters)
		self.assertEquals(parameters, otherParameters)

		# Clean up sample output data
		try:
			import os
			os.remove(unicode(path) + "/SampleOutput.c")
		except Exception, e:
			print e
