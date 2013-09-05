"""
StrategyNode

:Authors:
	Berend Klein Haneveld
"""


class StrategyNode(object):
	"""
	Node in a Strategy that represents some registration result.

	A node in the strategy tree contains the registration result at that point
	in the tree. This registration result can be 'dirty' and might need a
	rebuild.
	Has references to an incoming edge and outgoing edges.

	* Registration result
	* dirty (flag)
	* edge (incoming, parent)
	* edges (outgoing, childs)
	"""

	def __init__(self, fixedData=None, movingData=None, outputFolder=None):
		"""
		:param fixedData: Path to the fixed data set
		:type fixedData: basestring
		:param movingData: Path to the moving data set
		:type movingData: basestring
		:param outputFolder: Path to where the output should be saved
		:type outputFolder: basestring
		"""
		super(StrategyNode, self).__init__()
		
		# properties
		self.incomingEdge = None
		self.outgoingEdges = []
		self.fixedData = fixedData
		self.movingData = movingData
		self.outputFolder = outputFolder
		self.__dirty = False

	@property
	def dirty(self):
		"""
		:rtype: bool
		"""
		return self.__dirty

	@dirty.setter
	def dirty(self, value):
		"""
		Marking a node dirty will also mark all its siblings as dirty.

		:type value: bool
		"""
		if self.__dirty != value:
			self.__dirty = value
			# If the node is made dirty, then all its siblings should be made
			# dirty as well.
			if value is True:
				for edge in self.outgoingEdges:
					edge.childNode.dirty = True
