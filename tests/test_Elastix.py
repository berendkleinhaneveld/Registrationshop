import unittest
import os
import shutil
from core.elastix import Elastix
from core.elastix import ElastixCommand


class ElastixTest(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testElastix(self):
		self.assertTrue(hasattr(Elastix, "process"))

	def testProcessingSingleTask(self):
		if not hasattr(self, "path"):
			# Get the path of the current test
			self.path = os.path.dirname(os.path.abspath(__file__))
		
		# Create paths to some data sets
		movingData = self.path + "/data/hi-5.mhd"
		fixedData = self.path + "/data/hi-3.mhd"
		outputFolder = self.path + "/data/output"
		transformation = self.path + "/data/Sample.txt"

		# Construct a simple valid command object
		command = ElastixCommand(fixedData=fixedData,
			movingData=movingData,
			outputFolder=outputFolder,
			transformation=transformation)

		self.assertTrue(command.isValid())

		Elastix.process(command)

		# Important parameters to keep track of:
		# (NumberOfResolutions 1)
		# (MaximumNumberOfIterations 50)
		# These are the most time consuming operations within Elastix and
		# are a good way of keeping track of the process.

		self.assertTrue(os.path.exists(outputFolder + "/result.0.mhd"))

		# Cleanup test directory
		try:
			if os.path.exists(outputFolder):
				shutil.rmtree(outputFolder)
		except Exception, e:
			raise e

	def testProcessingInvalidTaskRaisesException(self):
		# Create incomplete task (is missing command)
		otherTask = ElastixCommand()
		
		self.assertRaises(Exception, Elastix.process, otherTask)
