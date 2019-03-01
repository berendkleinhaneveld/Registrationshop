"""
StrategyNode

:Authors:
	Berend Klein Haneveld
"""

from core.data import DataReader


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

	def __init__(self, fixedFile=None, movingFile=None, outputFolder=None):
		"""
		:param fixedData: Path to the fixed data set
		:type fixedData: str
		:param movingData: Path to the moving data set
		:type movingData: str
		:param outputFolder: Path to where the output should be saved
		:type outputFolder: str
		"""
		super(StrategyNode, self).__init__()

		# properties
		self.incomingEdge = None
		self.outgoingEdges = []

		# Create wrappers around the file name
		self.fixed = DataWrapper(fixedFile)
		self.moving = DataWrapper(movingFile)

		self.outputFolder = outputFolder
		self.dirty = False


class DataWrapper(object):
	"""
	DataWrapper is a simple container object for
	a file name plus a vtkImageData object. The file
	name should be set, but the image data can be cleared.
	"""
	def __init__(self, fileName=None):
		super(DataWrapper, self).__init__()
		self.filename = fileName    # Required property
		self.__imageData = None  	# Optional property
		self.outgoingEdge = None
		self.incomingEdge = None

	@property
	def imageData(self):
		if not self.filename:
			return None

		if not self.__imageData:
			dataReader = DataReader()
			self.__imageData = dataReader.GetImageData(self._filename)

		return self.__imageData

	def clearImageData(self):
		del self.__imageData
		self.__imageData = None
