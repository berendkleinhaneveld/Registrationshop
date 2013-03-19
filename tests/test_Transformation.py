import unittest

from core.Transformation import Transformation
from core.elastix.Parameter import Parameter

class TransformationTest(unittest.TestCase):

	def testListMethods(self):
		nonvalidValue = "hello world"
		value = Parameter("key", "hello world")
		otherValue = Parameter("key", "goodbye world")
		anotherValue = Parameter("key", 0)

		parameters = Transformation()
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

	def testInputOutputMethods(self):
		import os
		parameters = Transformation()
		path = os.path.dirname(os.path.abspath(__file__))
		parameters.loadFromFile(unicode(path) + "/data/Sample.txt")
		assert len(parameters) == 28
		parameters.saveToFile(unicode(path) + "/SampleOutput.c")
		otherParameters = Transformation()
		otherParameters.loadFromFile(unicode(path) + "/SampleOutput.c")
		assert len(parameters) == len(otherParameters)
		assert Parameter("MovingInternalImagePixelType", "float") in parameters
		assert parameters == otherParameters

		try:
			import os
			os.remove(unicode(path) + "/SampleOutput.c")
		except Exception, e:
			print e
