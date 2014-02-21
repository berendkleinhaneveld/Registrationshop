"""
AppVars

Global variables for RegistrationShop

author: Berend Klein Haneveld 2013
"""

import os
import sys

# Variables are adjusted by RegistrationShop
# This serves as a sort of global environment for
# stuff like application paths.
# This is because application path on OS X gives path
# to Python framework instead of RegistrationShop.py


class AppVars(object):
	"""
	AppVars keeps track of a few global parameters needed for RegistrationShop.

	The parameters are mostly paths to resources.
	"""

	#: Path to the application executable
	applicationPath = None

	@staticmethod
	def setPath(path):
		"""
		:type path: basestring
		"""
		if not(isinstance(path, basestring)):
			raise TypeError

		if not os.path.exists(path) and os.path.isdir(path):
			raise Exception("The provided path does not exist")
		AppVars.applicationPath = path

	@staticmethod
	def path():
		"""
		:rtype: basestring
		"""
		return AppVars.applicationPath

	@staticmethod
	def imagePath():
		"""
		:rtype: basestring
		"""
		extension = "resources/images/"
		if AppVars.applicationPath:
			# Put the application path in front of the extension only on
			# OS X systems.
			if sys.platform.startswith('darwin'):
				return os.path.join(AppVars.applicationPath, extension)
			else:
				return extension
		else:
			print "Warning: application path is not set"
			return extension

	@staticmethod
	def transformationsPath():
		"""
		:rtype: basestring
		"""
		extension = "resources/transformations/"
		if AppVars.applicationPath:
			return os.path.join(AppVars.applicationPath, extension)
		else:
			print "Warning: application path is not set"
			return extension

	@staticmethod
	def dataPath():
		"""
		:rtype: basestring
		"""
		extension = "resources/data/"
		if AppVars.applicationPath:
			return os.path.join(AppVars.applicationPath, extension)
		else:
			print "Warning: application path is not set"
			return extension
