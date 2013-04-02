"""
StrategyEdge

:Authors:
	Berend Klein Haneveld
"""

import os, sys
import subprocess

class StrategyEdge(object):
	"""
	An edge is the relation between two nodes. It contains the transformation that is applied to node A to get the result at node B. It also knows the parameters with which the transformation was made (with elastix). So that this can be adjusted / tweaked later by the user.
	An edge can be seen as the function that is applied to a dataset from a node. Custom edges should be supported that can modify / play with the data. These edges need to support custom modules / code from the user.

	- Transformation
	- Transformation parameters
	- node (parent)
	- node (child)
	"""
	def __init__(self, parent=None, child=None, transformation=None):
		"""
		:param parent: Parent node of the edge to be constructed
		:type parent: StrategyNode
		:param child: Child node of the edge to be constructed
		:type child: StrategyNode
		:param transformation: Transformation that this edge will represent
		:type transformation: Transformation
		"""
		super(StrategyEdge, self).__init__()

		# define properties
		self.parentNode = parent
		self.childNode = None
		self.transformation = transformation

	def execute(self):
		"""
		Call Elastix to execute the transformation.
		Needed at least:
		- Fixed data set (also from parent node)
		- Moving data set (from parent node)
		- Parameter file (made from transformation)

		TODO: this will be replaced by the ElastixCommand and ElastixTask system
		"""
		assert self.parentNode is not None
		assert self.childNode is not None
		assert self.transformation is not None
		assert self.parentNode.movingData is not None
		assert self.parentNode.fixedData is not None
		assert self.parentNode.outputFolder is not None
		assert self.childNode.outputFolder is not None

		# Create a parameter file of the transformation in the output folder
		# of the parent node (next to the (moving) input data)
		parameterFile = self.parentNode.outputFolder + "/TransformationParameters.txt"
		self.transformation.saveToFile(parameterFile)
		assert os.path.exists(parameterFile)

		# Ensure that the output folder actually exists before calling Elastix
		if not os.path.exists(self.childNode.outputFolder):
			os.makedirs(self.childNode.outputFolder)

		# Create Elastix command with the right parameters
		# TODO: build some class or thing to actually call Elastix instead of 
		# calling directly from the StrategyEdge class
		command = ["elastix", 
			"-m", self.parentNode.movingData, 
			"-f", self.parentNode.fixedData,
			"-out", self.childNode.outputFolder,
			"-p", parameterFile]

		# Try and call elastix
		try:
			return_code = subprocess.check_call(command)
			# TODO: call transformix if (WriteResultImage "true") was set to false
			self.childNode.movingData = self.childNode.outputFolder + "/result.0.mhd"
			self.childNode.dirty = False
			del return_code
		except:
			print "Image registration failed with command:"
			print command
			print "More detailed info:"
			print sys.exc_info()

		assert self.childNode.movingData is not None
		assert self.childNode.dirty is False
