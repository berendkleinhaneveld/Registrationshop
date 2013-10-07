import unittest
from core.operations import *


class OperationsTest(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testOperationsDot(self):
		vec1 = [1, 0, 0]
		vec2 = [0, 1, 0]
		result = Dot(vec1, vec2)
		self.assertEquals(result, 0)

		vec1 = [1, 0, 0]
		vec2 = [3, 0, 0]
		result = Dot(vec1, vec2)
		self.assertEquals(result, 3)

	def testOperationDotRaisesAssertOnIncompatibleVectors(self):
		u = [0, 0]
		v = [0, 0, 0]
		self.assertRaises(AssertionError, Dot, u, v)

	def testSubtract(self):
		vec1 = [1, 1, 1]
		vec2 = [2, 3, 5]
		expectedRes1 = [-1, -2, -4]
		expectedRes2 = [1, 2, 4]

		result = Subtract(vec1, vec2)
		self.assertEquals(expectedRes1, result)
		result = Subtract(vec2, vec1)
		self.assertEquals(expectedRes2, result)

	def testSubtractRaisesAssertOnIncompatibleVectors(self):
		u = [0, 0]
		v = [0, 0, 0]
		self.assertRaises(AssertionError, Subtract, u, v)

	def testMultiply(self):
		vec1 = [1, 1, 1]
		vec2 = [2, 3, 5]
		sca1 = 3
		sca2 = 6
		expectedRes1 = [3, 3, 3]
		expectedRes2 = [12, 18, 30]

		result = Multiply(vec1, sca1)
		self.assertEquals(expectedRes1, result)
		result = Multiply(vec2, sca2)
		self.assertEquals(expectedRes2, result)

	def testAdd(self):
		vec1 = [1, 1, 1]
		vec2 = [2, 3, 5]
		expectedRes = [3, 4, 6]

		result = Add(vec1, vec2)
		self.assertEquals(expectedRes, result)

	def testAddRaisesAssertOnIncompatibleVectors(self):
		u = [0, 0]
		v = [0, 0, 0]
		self.assertRaises(AssertionError, Add, u, v)

	def testLength(self):
		vec1 = [1, 0, 0]

		result = Length(vec1)
		self.assertEquals(result, 1)

	def testNormalize(self):
		vec = [3, 3, 3]
		result = Normalize(vec)
		self.assertEquals(Length(result), 1.0)

		vec = [40, -31, 21]
		result = Normalize(vec)
		self.assertEquals(Length(result), 1.0)

	def testNormalizeLenghtZero(self):
		vec = [0, 0, 0]
		result = Normalize(vec)
		self.assertTrue(math.isnan(result[0]))

	def testMean(self):
		vec1 = [1, 1, 1]
		vec2 = [20, 3, 5]
		vec3 = [33, 42, 16]
		vec4 = [40, -31, 21]
		expected = [23.5, 3.75, 10.75]

		result = Mean([vec1, vec2, vec3, vec4])
		self.assertEquals(expected, result)

	def testMeanWithUnevenVectorLength(self):
		vec1 = [1, 1, 1]
		vec2 = [20, 3]
		self.assertRaises(AssertionError, Mean, [vec1, vec2])

	def testMeanScalar(self):
		self.assertRaises(TypeError, Mean, 3)

		sca1 = 1
		sca2 = 2
		sca3 = 3
		self.assertRaises(AssertionError, Mean, [sca1, sca2, sca3])
