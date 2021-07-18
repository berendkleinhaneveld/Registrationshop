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
        self.assertEqual(len(parameters), 0)
        # Test adding a non Parameter value
        self.assertRaises(TypeError, parameters.append, nonvalidValue)

        self.assertEqual(len(parameters), 0)
        parameters.append(value)
        self.assertEqual(len(parameters), 1)
        self.assertEqual(parameters[0], value)
        parameters.append(otherValue)
        self.assertEqual(len(parameters), 2)
        self.assertEqual(parameters[1], otherValue)
        parameters[0] = anotherValue
        self.assertEqual(parameters[0], anotherValue)
        del parameters[1]
        self.assertEqual(len(parameters), 1)
        self.assertTrue(anotherValue in parameters)
        self.assertTrue(otherValue not in parameters)

    def testInputOutputMethods(self):
        import os

        parameters = ParameterList()
        path = os.path.dirname(os.path.abspath(__file__))
        parameters.loadFromFile(str(path) + "/data/Sample.txt")
        self.assertEqual(len(parameters), 28)
        parameters.saveToFile(str(path) + "/SampleOutput.c")
        otherParameters = ParameterList()
        otherParameters.loadFromFile(str(path) + "/SampleOutput.c")
        self.assertEqual(len(parameters), len(otherParameters))
        self.assertTrue(
            Parameter("MovingInternalImagePixelType", "float") in parameters
        )
        self.assertEqual(parameters, otherParameters)

        # Clean up sample output data
        try:
            import os

            os.remove(str(path) + "/SampleOutput.c")
        except Exception as e:
            print(e)
