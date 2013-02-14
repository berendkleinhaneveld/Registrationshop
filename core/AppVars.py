"""
AppVars
	
Global variables for RegistrationShop
	
author: Berend Klein Haneveld 2013
"""

# Variables are adjusted by RegistrationShop
# This serves as a sort of global environment for
# stuff like application paths.
# This is because application path on OS X gives path
# to Python framework instead of RegistrationShop.py

class AppVars(object):
	applicationPath = None
	
	@staticmethod
	def setPath(path):
		"""
		@type path: basestring
		"""
		if not(isinstance(path, basestring)):
			raise TypeError
		# TODO: check if path is a real path
		# path should end with '/'
		AppVars.applicationPath = path

	@staticmethod
	def path():
		"""
		@rtype: basestring
		"""
		return AppVars.applicationPath

	@staticmethod
	def imagePath():
		"""
		@rtype: basestring
		"""
		extension = "resources/images/"
		if AppVars.applicationPath:
			return AppVars.applicationPath + extension
		else:
			print "Warning: application path is not set"
			return extension
