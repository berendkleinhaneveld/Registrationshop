"""
Project

:Authors:
	Berend Klein Haneveld
"""


class Project(object):
	"""
	Project holds the basic information of a project for RegistrationShop
	"""

	def __init__(self, title=None, fixedData=None, movingData=None, isReference=None):
		super(Project, self).__init__()

		self.title = title
		self.fixedData = fixedData
		self.movingData = movingData
		self.isReference = isReference
		self.folder = None
		self.resultData = None
		self.fixedSettings = None
		self.movingSettings = None
		self.multiSettings = None
		self.transformations = None

	def __eq__(self, other):
		if not isinstance(other, Project):
			return False
		return (self.title == other.title
			and self.fixedData == other.fixedData
			and self.movingData == other.movingData
			and self.isReference == other.isReference)

	def __ne__(self, other):
		return not self.__eq__(other)
