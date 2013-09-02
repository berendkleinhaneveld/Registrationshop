"""
DataController

:Authors:
	Berend Klein Haneveld
"""


class DataController(object):
	"""
	DataController is the base interface for
	the reader and writer.
	"""
	def __init__(self):
		super(DataController, self).__init__()
		
		self.supportedExtensions = []

	def IsExtensionSupported(self, extension):
		"""
		:type extension: basestring
		:rtype: bool
		"""
		result = False

		for ext in self.supportedExtensions:
			if ext == extension:
				result = True
				break

		return result

	def GetSupportedExtensionsAsString(self):
		"""
		Create string representation of all the supported file extensions.
		It will be formatted as follows: '*.mbr *.dcm'
		:rtype: basestr
		"""
		stringRepresentation = ""
		for extension in self.supportedExtensions:
			stringRepresentation += ("*." + extension + " ")
		return stringRepresentation
