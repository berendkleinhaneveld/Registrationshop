"""
Strategy

Strategy is the complete tree of transformations and registration results.

@author: Berend Klein Haneveld
"""

from StrategyNode import StrategyNode
from StrategyEdge import StrategyEdge

class Strategy(object):
	"""
	"""
	def __init__(self, fixedData=None, movingData=None, baseDir=None):
		super(Strategy, self).__init__()
		
		# Properties
		self.rootNode = StrategyNode(fixedData=fixedData, dataset=movingData)
		self.fixedData = fixedData
		self.baseDir = baseDir

		# Create a pointer to the current node
		self.currentNode = self.rootNode

	def setCurrentNode(self, node):
		"""
		Sets the given node as the current node.
		"""
		self.currentNode = node

	def addTransformation(self, transformation):
		"""
		Add a transformation to the tree, by adding an edge and node
		to the current node.
		Note: might be a temporary method
		"""
		# Create an edge with the transformation
		edge = StrategyEdge()
		edge.transformation = transformation

		# Create a dirty node that will hold the data at a later point
		newNode = StrategyNode()
		newNode.dirty = True
		newNode.incomingEdge = edge

		# Connect the edge to the nodes
		self.currentNode.outgoingEdges.append(edge)
		edge.parentNode = self.currentNode
		edge.childNode = newNode

		# Update the current node
		self.currentNode = newNode

	def cleanUp(self):
		"""
		This method cleans up dirty nodes by calling Elastix and
		applying the transformations. It will cleanup all nodes
		that are dirty.
		"""
		self.calculateNode(self.rootNode)

	def calculateNode(self, node):
		"""
		Cleanup a certain node. It assumes that parents of this
		node are not dirty.
		"""
		if node.dirty:
			# TODO: call Elastix on node and incoming edge
			node.dirty = False

		# Go and call Elastix for all child nodes.
		for edge in node.outgoingEdges:
			childNode = edge.childNode
			self.calculateNode(childNode)
