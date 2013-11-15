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

	def isValid(self):
		"""
		Project is valid when the fixed and moving image data actually
		exits on disk. If this is not the case, then the project is
		invalid.
		"""
		import os
		if self.fixedData and not os.path.isfile(self.fixedData):
			return False
		if self.movingData and not os.path.isfile(self.movingData):
			return False
		return True
