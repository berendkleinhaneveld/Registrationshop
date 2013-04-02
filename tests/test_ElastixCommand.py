import unittest
import os
from core.elastix.ElastixCommand import ElastixCommand

class ElastixCommandTest(unittest.TestCase):

	def setUp(self):
		if not hasattr(self, "path"):
			# Get the path of the current test
			self.path = os.path.dirname(os.path.abspath(__file__))
		
		# Create paths to some data sets
		movingData = self.path + "/data/hi-5.mhd"
		fixedData = self.path + "/data/hi-3.mhd"
		outputFolder = self.path + "/data/data"
		transformation = self.path + "/data/Sample.txt"

		# Construct a simple command object
		self.command = ElastixCommand(fixedData=fixedData, 
			movingData=movingData, 
			outputFolder=outputFolder, 
			transformation=transformation)

	def tearDown(self):
		del self.command

	def testCommandParametersAreSetCorrectly(self):
		self.assertIn("/data/hi-5", self.command.movingData)
		self.assertIn("/data/hi-3", self.command.fixedData)
		self.assertIn("/data/data", self.command.outputFolder)
		self.assertIn("/data/Sample.txt", self.command.transformation)

	def testCommandIsInvalidForMissingParameter(self):
		self.command.transformation = None
		self.assertFalse(self.command.isValid())

	def testCommandIsInvalidForNonexistingFileParameter(self):
		# Change the transformation to an invalid string
		self.command.transformation = "NonexistantTransformationFileName.txt"
		self.assertFalse(self.command.isValid())

	def testCommandIsValidForCompleteParameter(self):
		# self.command should be a valid parameter
		self.assertTrue(self.command.isValid())
		
	def testCommandIsInvalidForTooDeepOutputDirectory(self):
		self.assertTrue(self.command.isValid())
		self.command.outputFolder = self.path + "/data/subfolder/tooDeep"
		self.assertFalse(self.command.isValid())

	# def testCommandCanExecute(self):
		# self.command.execute()
