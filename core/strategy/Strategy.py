"""
Strategy

:Authors:
	Berend Klein Haneveld
"""

from StrategyNode import StrategyNode
from StrategyEdge import StrategyEdge


class Strategy(object):
	"""
	Strategy is the complete tree of transformations and registration results.

	This class manages the structure of all the transformations that are build
	up by the user. By representing all the actions in a tree, it will be
	possible to compare the results of leaves to each other.
	"""

	def __init__(self, fixedData=None, movingData=None, baseDir=None):
		super(Strategy, self).__init__()
		
		# Properties
		self.rootNode = StrategyNode(fixedFile=fixedData, movingFile=movingData)
		self.fixedData = fixedData
		self.baseDir = baseDir

		# Create a pointer to the current node
		self.currentNode = self.rootNode

	def setCurrentNode(self, node):
		"""
		Sets the given node as the current node.

		:param node: Node to be set as current node
		:type node: StrategyNode
		"""
		self.currentNode = node

	def addTransformation(self, transformation):
		"""
		Add a transformation to the tree, by adding an edge and node
		to the current node.
		Note: might be a temporary method

		:param transformation: Transformation that will be added to the tree
		:type transformation: Transformation
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
		Cleanup a certain node. It assumes that parents of the provided
		node are not dirty.

		:param node: node that should be 'executed'
		:type node: StrategyNode
		"""
		if node.dirty:
			# TODO: call Elastix on node and incoming edge
			node.dirty = False

		# Go and call Elastix for all child nodes.
		for edge in node.outgoingEdges:
			childNode = edge.childNode
			self.calculateNode(childNode)
