import unittest
from core.worker.Command import Command

class CommandTest(unittest.TestCase):

	def setUp(self):
		self.command = Command()

	def tearDown(self):
		del self.command

	def testCommandHasExecuteFunction(self):
		self.assertTrue(hasattr(self.command, "execute"))

	def testCommandCanSetDelegate(self):
		delegate = "delegate"
		command = Command(delegate)
		self.assertEqual(command.delegate, delegate)
