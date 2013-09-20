"""
ElastixCommand

:Authors:
	Berend Klein Haneveld
"""

import os
from core.worker.Command import Command
from core.elastix import Elastix
from core.decorators import overrides


class ElastixCommand(Command):
	"""
	ElastixCommand that can be used to construct and  verify Elastix commands.

	Provides a placeholder for a command for Elastix that can be processed by
	Elastix.py. This makes is possible to validate a command before sending it
	off to elastix (the command line tool).
	"""

	def __init__(self, fixedData=None, movingData=None, outputFolder=None,
		transformation=None):
		"""
		Constructs a simple object with the provided parameters.

		:type fixedData: str
		:type movingData: str
		:type outputFolder: str
		:type transformation: str
		"""
		super(ElastixCommand, self).__init__()
		
		self.fixedData = fixedData
		self.movingData = movingData
		self.outputFolder = outputFolder
		self.transformation = transformation

	def isValid(self):
		"""
		Returns whether the given arguments are valid. Valid means that the
		fixed and moving data sets exists and that the parameter file is valid.

		:rtype: bool
		"""
		fixedDataValid = pathIsValidAndExists(self.fixedData)
		movingDataValid = pathIsValidAndExists(self.movingData)
		transformationValid = pathIsValidAndExists(self.transformation)
		outputFolderValid = pathIsValidOutputFolder(self.outputFolder)

		return (fixedDataValid and movingDataValid and transformationValid and
				outputFolderValid)

	@overrides(Command)
	def execute(self):
		"""
		Call Elastix to process itself as a command.
		"""
		Elastix.process(self)


def pathIsValidAndExists(path):
	"""
	Returns whether the given value is not None and whether it exists
	on the file system.

	:rtype: bool
	"""
	return path is not None and os.path.exists(path)


def pathIsValidOutputFolder(path):
	"""
	Returns wheter the given value is not None and whether the path can
	be constructed by creating one directory. So without the last path part
	it should ba a valid and existing directory.

	:rtype: bool
	"""
	head, tail = os.path.split(path)
	return os.path.exists(path) or os.path.exists(head)
