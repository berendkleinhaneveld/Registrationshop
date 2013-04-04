import os
import unittest
import time
from core.Operator import Operator
from core.Command import Command
from core.elastix.ElastixCommand import ElastixCommand


class OperatorTest(unittest.TestCase):

	def setUp(self):
		self.operator = Operator()

	def tearDown(self):
		del self.operator

	def testOperator(self):
		self.assertIsNotNone(self.operator)

	def testAddingSimpleCommand(self):
		# Create empty command
		command = Command()

		# Add command to the queue
		self.operator.addCommand(command)

		# An immediate check should find that the queue is not empty
		self.assertFalse(self.operator.queue.empty())

		# Wait until the queue is finished
		self.operator.queue.join()
		self.assertTrue(self.operator.queue.empty())

	def testAddingElastixCommand(self):
		path = os.path.dirname(os.path.abspath(__file__))
		
		# Create paths to some data sets
		movingData = path + "/data/hi-5.mhd"
		fixedData = path + "/data/hi-3.mhd"
		outputFolder = path + "/data/OperatorOutput"
		transformation = path + "/data/Sample.txt"

		# Construct a simple command object
		command = ElastixCommand(fixedData=fixedData, 
			movingData=movingData, 
			outputFolder=outputFolder, 
			transformation=transformation)

		self.operator.addCommand(command)
		# An immediate check should find that the queue is not empty
		self.assertFalse(self.operator.queue.empty())

		# Wait until the queue is finished
		self.operator.queue.join()
		self.assertTrue(self.operator.queue.empty())
		self.assertTrue(os.path.exists(outputFolder + "/result.0.mhd"))

		# Cleanup test directory
		try:
			if os.path.exists(outputFolder):
				import shutil
				shutil.rmtree(outputFolder)
		except Exception, e:
			raise e

	def testAddingMultipleCommands(self):
		command = Command()
		otherCommand = Command()

		self.operator.addCommand(command)
		self.operator.addCommand(otherCommand)

		self.assertEqual(self.operator.queue.qsize(), 2)

		self.operator.queue.join()
		self.assertTrue(self.operator.queue.empty())
