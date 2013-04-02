import unittest
from core.Worker import Worker
from Queue import Queue
from core.Command import Command
from core.elastix.ElastixCommand import ElastixCommand

class WorkerTest(unittest.TestCase):

	def setUp(self):
		self.queue = Queue()
		self.worker = Worker(self.queue)
		self.assertEqual(self.worker.queue, self.queue)

		# Daemonize the worker
		self.worker.daemon = True
		self.worker.start()

	def tearDown(self):
		del self.worker

	def testProcessingSimpleEmptyCommand(self):
		# Fill the queue with an empty command
		command = Command()
		self.queue.put(command)
		self.assertFalse(self.queue.empty())

		# Wait for the queue to finish
		self.queue.join()
		self.assertTrue(self.queue.empty())

	def testProcessingElastixCommand(self):
		import os
		if not hasattr(self, "path"):
			# Get the path of the current test
			self.path = os.path.dirname(os.path.abspath(__file__))
		
		# Create paths to some data sets
		movingData = self.path + "/data/hi-5.mhd"
		fixedData = self.path + "/data/hi-3.mhd"
		outputFolder = self.path + "/data/worker_output"
		transformation = self.path + "/data/Sample.txt"

		# Construct a simple command object
		command = ElastixCommand(fixedData=fixedData, 
			movingData=movingData, 
			outputFolder=outputFolder, 
			transformation=transformation)

		self.queue.put(command)
		self.assertFalse(self.queue.empty())

		# Wait for the command to finish
		self.queue.join()

		self.assertTrue(self.queue.empty())
		self.assertTrue(os.path.exists(outputFolder + "/result.0.mhd"))

		# Cleanup test directory
		try:
			if os.path.exists(outputFolder):
				import shutil
				shutil.rmtree(outputFolder)
		except Exception, e:
			raise e
