"""
StrategyNode

A node in the strategy tree contains the registration result at that point in the tree. This registration result can be 'dirty' and might need a rebuild.

* Registration result
* dirty (flag)
* edge (incoming, parent)
* edges (outgoing, childs)

@author: Berend Klein Haneveld
"""

# from Strategy import Strategy
from StrategyEdge import StrategyEdge

try:
	from PySide.QtCore import QObject
except ImportError as e:
	raise e

class StrategyNode(QObject):
	"""
	"""
	def __init__(self):
		super(StrategyNode, self).__init__()
		
		# properties
		self.incomingEdge = None
		self.outgoingEdges = []
		self.registrationResult = None
		self.dirty = False
		pass


	def addChild(self, otherNode):
		edge = StrategyEdge()
		edge.setParentNode(self)
		edge.setChildNode(otherNode)
		otherNode.incomingEdge = edge
		self.outgoingEdges.append(edge)
		pass


	def removeChild(self, otherNode):
		edges = []
		for edge in self.outgoingEdges:
			node = edge.childNode
			if node is not otherNode:
				edges.append(edge)
		self.outgoingEdges = edges
		otherNode.incomingEdge = None
		pass

	def removeFromStrategy(self, withSubTree=False):
		parent = self.incomingEdge.parentNode
		parent.removeChild(self)
		if withSubTree:
			while len(self.outgoingEdges) > 0:
				edge = self.outgoingEdges[0]
				child = edge.childNode
				child.removeFromStrategy(withSubTree)


def testAddAndRemoveChild():
	root = StrategyNode()
	childNode = StrategyNode()
	# Add a child to the root
	root.addChild(childNode)
	assert len(root.outgoingEdges) == 1
	assert childNode.incomingEdge is not None
	edge = childNode.incomingEdge
	assert edge.parentNode != None
	assert edge.childNode != None
	assert edge in root.outgoingEdges

	# Remove the child
	root.removeChild(childNode)
	assert len(root.outgoingEdges) == 0
	assert childNode.incomingEdge == None

def testAddAndRemoveChild2():
	root = StrategyNode()
	childNode = StrategyNode()
	otherChild = StrategyNode()
	root.addChild(childNode)
	childNode.addChild(otherChild)
	childNode.removeFromStrategy()
	assert len(root.outgoingEdges) == 0
	assert childNode.incomingEdge == None
	assert len(childNode.outgoingEdges) == 1
	assert childNode.outgoingEdges[0].childNode == otherChild
	root.addChild(childNode)
	assert len(root.outgoingEdges) == 1
	assert childNode.incomingEdge is not None
	edge = childNode.incomingEdge
	assert edge.parentNode != None
	assert edge.childNode != None
	assert edge in root.outgoingEdges
	childNode.removeFromStrategy(withSubTree=True)
	assert len(childNode.outgoingEdges) == 0
	assert otherChild.incomingEdge is None

if __name__ == '__main__':
	testAddAndRemoveChild()
	testAddAndRemoveChild2()
