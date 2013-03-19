"""
StrategyNode

A node in the strategy tree contains the registration result at that point in the tree. This registration result can be 'dirty' and might need a rebuild.

* Registration result
* dirty (flag)
* edge (incoming, parent)
* edges (outgoing, childs)

@author: Berend Klein Haneveld
"""

class StrategyNode(object):
	"""
	"""
	def __init__(self, fixedData=None, dataset=None, outputFolder=None):
		super(StrategyNode, self).__init__()
		
		# properties
		self.incomingEdge = None
		self.outgoingEdges = []
		self.fixedData = fixedData
		self.dataset = dataset
		self.outputFolder = outputFolder
		self.__dirty = False

	@property
	def dirty(self):
		return self.__dirty

	@dirty.setter
	def dirty(self, value):
		if self.__dirty != value:
			self.__dirty = value
			if value == True:
				for edge in self.outgoingEdges:
					edge.childNode.dirty = True

	# def addChild(self, otherNode):
	# 	edge = StrategyEdge()
	# 	edge.setParentNode(self)
	# 	edge.setChildNode(otherNode)
	# 	otherNode.incomingEdge = edge
	# 	self.outgoingEdges.append(edge)

	# def removeChild(self, otherNode):
	# 	edges = []
	# 	for edge in self.outgoingEdges:
	# 		node = edge.childNode
	# 		if node is not otherNode:
	# 			edges.append(edge)
	# 	self.outgoingEdges = edges
	# 	otherNode.incomingEdge = None

	# def removeFromStrategy(self, withSubTree=False):
	# 	parent = self.incomingEdge.parentNode
	# 	parent.removeChild(self)
	# 	if withSubTree:
	# 		while len(self.outgoingEdges) > 0:
	# 			edge = self.outgoingEdges[0]
	# 			child = edge.childNode
	# 			child.removeFromStrategy(withSubTree)
