"""
Elastix

:Authors:
	Berend Klein Haneveld
"""

import os
import sys
import subprocess

class Elastix(object):
	"""
	Elastix

	Wrapper around the task-line tool Elastix.
	Inspired by pyelastix by Almar Klein. His project can be found
	at https://code.google.com/p/pirt/

	At the moment Elastix must be explicitly started and stopped in order to 
	process tasks, but what might be a better idea is to just start 
	processing tasks at the moment they are added and queue other incoming
	tasks. Implementing this would have to wait though on a working
	implementation of a task.
	"""

	def __init__(self):
		super(Elastix, self).__init__()

		self.queue = [] #: Queue of tasks to process

	def process(self, command):
		"""
		Process the task immediately
		"""
		assert command is not None
		assert command.isValid()

		# Ensure that the output folder actually exists before calling Elastix
		if not os.path.exists(command.outputFolder):
			os.makedirs(command.outputFolder)

		# Create Elastix command with the right parameters
		# TODO: build some class or thing to actually call Elastix instead of 
		# calling directly from the StrategyEdge class
		command = ["elastix", 
			"-m", command.movingData, 
			"-f", command.fixedData,
			"-out", command.outputFolder,
			"-p", command.transformation]

		# Try and call elastix
		try:
			proc = subprocess.Popen(command, stdout=subprocess.PIPE)
			# TODO: Catching output prevents from Python from real multitasking
			# This is fixed by processing Elastix and the command in a different
			# thread.
			for line in iter(proc.stdout.readline, ""):
				# print line.rstrip()
				pass
			# TODO: call transformix if WriteResultImage parameter was set to false
			# self.childNode.movingData = self.childNode.outputFolder + "/result.0.mhd"
			# self.childNode.dirty = False
		except Exception, e:
			print "Image registration failed with command:"
			print command
			print "More detailed info:"
			print sys.exc_info()
			raise e
