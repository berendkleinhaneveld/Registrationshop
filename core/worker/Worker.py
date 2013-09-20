"""
Worker

:Authors:
	Berend Klein Haneveld
"""

from threading import Thread
from core.decorators import overrides


class Worker(Thread):
	"""
	Worker class that can process all kinds of commands. Depending on the
	type of command it will execute it. The operator can use a worker to
	process commands in different threads.
	"""

	def __init__(self, queue):
		"""
		Initiate the worker with a certain queue. The worker will call the
		get() method of the queue so that it blocks until the queue gets filled
		with commands.

		:param queue: Queue that the worker will attach to
		:type queue: Queue.Queue
		"""
		super(Worker, self).__init__()

		self.queue = queue

	@overrides(Thread)
	def run(self):
		"""
		Overridden method of threading.Thread
		"""
		while True:
			# Get the command from the queue
			command = self.queue.get()

			# Process the command
			self.processCommand(command)

			# Send a signal to the queue that the command is done
			self.queue.task_done()

	def processCommand(self, command):
		"""
		:param command: A command that can be executed / processed.
		:type command: Command
		"""
		command.execute()
