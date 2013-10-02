"""
AppResources

:Authors:
	Berend Klein Haneveld
"""

import os
from AppVars import AppVars
from core.elastix import ParameterList


class AppResources(object):
	"""
	AppResources is a static class that can be used to find common resources
	easily. Just provide a name to the imageNamed() method and it will return
	the correct path.
	"""

	@staticmethod
	def imageNamed(imageName):
		"""
		Returns the full path to the given imageName.

		Note:
		Future versions might be more intelligent and can handle searching
		through the resource folder. For now it just combines the AppVars
		imagePath with the imageName.

		:type imageName: basestring
		:rtype: basestring
		"""
		return os.path.join(AppVars.imagePath(), imageName)

	@staticmethod
	def elastixTemplates():
		"""
		Returns a list of all the available elastix templates in the
		resource folder.
		"""
		transformations = []
		fileNames = os.listdir(AppVars.transformationsPath())
		for fileName in fileNames:
			fullFileName = os.path.join(AppVars.transformationsPath(), fileName)
			transformation = ParameterList()
			if transformation.loadFromFile(fullFileName):
				transformations.append(transformation)
		return transformations
