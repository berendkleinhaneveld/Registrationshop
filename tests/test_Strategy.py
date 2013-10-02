import unittest
# import os
from core.strategy.Strategy import Strategy
from core.elastix import ParameterList


class TestStrategy(unittest.TestCase):

	# Setup and teardown

	def setUp(self):
		super(TestStrategy, self).setUp()
		self.strategy = Strategy("/Users/beer/Registrationshop/Data/datasets/cryo.mhd",
			"/Users/beer/Registrationshop/Data/datasets/CT.mhd",
			"/Users/beer/Registrationshop/Data/datasets/output")

	def tearDown(self):
		super(TestStrategy, self).tearDown()
		del self.strategy

	# Test cases

	def testSimpleStrategy(self):
		# Create a strategy with a fixed and moving data set
		self.assertIsNotNone(self.strategy.fixedData)
		self.assertIn("cryo", self.strategy.fixedData)
		self.assertIsNotNone(self.strategy.rootNode)
		self.assertIsNotNone(self.strategy.rootNode.moving.filename)
		self.assertFalse(self.strategy.rootNode.dirty)
		self.assertEqual(self.strategy.currentNode, self.strategy.rootNode)
		self.assertIn("output", self.strategy.baseDir)

	# def testAddingTransformation(self):
	# 	self.strategy.addTransformation(ParameterList())
	# 	self.assertNotEqual(self.strategy.currentNode, self.strategy.rootNode)
	# 	self.assertTrue(self.strategy.currentNode.dirty)
	# 	self.assertEqual(self.strategy.currentNode.incomingEdge.parentNode, self.strategy.rootNode)
	# 	edge = self.strategy.currentNode.incomingEdge
	# 	self.assertIsNotNone(edge.transformation)

	def testSettingCurrentNode(self):
		self.strategy.addTransformation(ParameterList())
		self.strategy.setCurrentNode(self.strategy.rootNode)
		self.assertEqual(self.strategy.currentNode, self.strategy.rootNode)
		self.strategy.addTransformation(ParameterList())
		self.assertEqual(len(self.strategy.rootNode.outgoingEdges), 2)

	# def testExecutingStrategy(self):
	# 	transformation = ParameterList()
	# 	path = os.path.dirname(os.path.abspath(__file__))
	# 	transformation.loadFromFile(unicode(path) + "/data/Sample.txt")
	# 	self.strategy.addTransformation(transformation)
	# 	self.assertTrue(self.strategy.currentNode.dirty)
	# 	self.strategy.cleanUp()
	# 	self.assertFalse(self.strategy.currentNode.dirty)
