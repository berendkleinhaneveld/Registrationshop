import unittest
import os

from core.strategy.StrategyNode import StrategyNode


class StrategyNodeTest(unittest.TestCase):
    def setUp(self):
        super(StrategyNodeTest, self).setUp()
        path = os.path.dirname(os.path.abspath(__file__))
        fixedData = path + "/data/hi-3.vti"
        movingData = path + "/data/hi-5.vti"
        self.node = StrategyNode(fixedFile=fixedData, movingFile=movingData)

    def tearDown(self):
        super(StrategyNodeTest, self).tearDown()
        del self.node

    def testBasicNode(self):
        """
        Test the basic creation of a StrategyNode
        """
        self.assertIn("hi-5", self.node.moving.filename)
        self.assertIn("hi-3", self.node.fixed.filename)
        self.assertIsNone(self.node.incomingEdge)
        self.assertEqual(len(self.node.outgoingEdges), 0)
        self.assertIsNone(self.node.outputFolder)
        self.assertFalse(self.node.dirty)

    # def testAddAndRemoveChild(self):
    #     root = StrategyNode()
    #     childNode = StrategyNode()
    #     # Add a child to the root
    #     root.addChild(childNode)
    #     assert len(root.outgoingEdges) == 1
    #     assert childNode.incomingEdge is not None
    #     edge = childNode.incomingEdge
    #     assert edge.parentNode != None
    #     assert edge.childNode != None
    #     assert edge in root.outgoingEdges

    #     # Remove the child
    #     root.removeChild(childNode)
    #     assert len(root.outgoingEdges) == 0
    #     assert childNode.incomingEdge == None

    # def testAddAndRemoveChild2(self):
    #     root = StrategyNode()
    #     childNode = StrategyNode()
    #     otherChild = StrategyNode()
    #     root.addChild(childNode)
    #     childNode.addChild(otherChild)
    #     childNode.removeFromStrategy()
    #     assert len(root.outgoingEdges) == 0
    #     assert childNode.incomingEdge == None
    #     assert len(childNode.outgoingEdges) == 1
    #     assert childNode.outgoingEdges[0].childNode == otherChild
    #     root.addChild(childNode)
    #     assert len(root.outgoingEdges) == 1
    #     assert childNode.incomingEdge is not None
    #     edge = childNode.incomingEdge
    #     assert edge.parentNode != None
    #     assert edge.childNode != None
    #     assert edge in root.outgoingEdges
    #     childNode.removeFromStrategy(withSubTree=True)
    #     assert len(childNode.outgoingEdges) == 0
    #     assert otherChild.incomingEdge is None

    # def testNodeDirty(self):
    #     childNode1 = StrategyNode("Data1")
    #     childNode2 = StrategyNode("Data2")
    #     self.node.addChild(childNode1)
    #     self.node.addChild(childNode2)
    #     self.node.dirty = True
    #     assert self.node.dirty is True
    #     assert childNode1.dirty is True
    #     assert childNode2.dirty is True
