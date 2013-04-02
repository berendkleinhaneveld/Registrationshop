import unittest
import time
from core.Operator import Operator
from core.Command import Command


class OperatorTest(unittest.TestCase):

	def setUp(self):
		self.operator = Operator()

	def tearDown(self):
		del self.operator

	def testOperator(self):
		self.assertIsNotNone(self.operator)

	def testAddingCommands(self):
		# Create empty command
		command = Command()

		# Add command to the queue
		self.operator.addCommand(command)

		# An immediate check should find that the queue is not empty
		self.assertFalse(self.operator.queue.empty())

		# When we wait a little bit, the should be processed and thus
		# the queue should be empty again. 
		time.sleep(0.05)
		self.assertTrue(self.operator.queue.empty(), 
			"Processing takes too long or queue is not emptied.")
