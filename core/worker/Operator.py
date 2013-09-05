"""
:Authors:
	Berend Klein Haneveld
"""

from Queue import Queue
from core.worker.Worker import Worker


class Operator(object):
	"""
	Operator is an operator of command. It creates a queue of commands.
	Each command should be a subclass of the type Command. For each type
	there is a specific kind of operator that will be called to process the
	command.

	An operator collects all the commands that are 'fired'. There are one or more
	workers that wait until commands are given to the queue of commands. These
	workers will process the commands, depending on the type of command.

	Command pattern:
	http://sourcemaking.com/design_patterns/command

	Use of threading and queues:
	http://www.blog.pythonlibrary.org/2012/08/01/python-concurrency-an-example-of-a-queue/

	Pool instead of Queue?
	"""

	def __init__(self):
		super(Operator, self).__init__()

		self.queue = Queue()
		self.worker = Worker(self.queue)
		self.worker.setDaemon(True)
		self.worker.start()

	def addCommand(self, command):
		self.queue.put(command)
