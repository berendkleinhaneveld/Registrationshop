"""
StrategyEdge

An edge is the relation between two nodes. It contains the transformation that is applied to node A to get the result at node B. It also knows the parameters with which the transformation was made (with elastix). So that this can be adjusted / tweaked later by the user.
An edge can be seen as the function that is applied to a dataset from a node. Custom edges should be supported that can modify / play with the data. These edges need to support custom modules / code from the user.

* Transformation
* Transformation parameters
* node (parent)
* node (child)

@author: Berend Klein Haneveld
"""

# from Strategy import Strategy
# from StrategyNode import StrategyNode

try:
	from PySide.QtCore import QObject
except ImportError as e:
	raise e

class StrategyEdge(QObject):
	"""
	"""
	def __init__(self):
		super(StrategyEdge, self).__init__()

		# define properties
		self.parentNode = None
		self.childNode = None
		self.transformation = None

	def setParentNode(self, node):
		self.parentNode = node

	def setChildNode(self, node):
		self.childNode = node
