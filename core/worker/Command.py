"""
Command

:Authors:
	Berend Klein Haneveld
"""


class Command(object):
	"""
	Command is an interface class for wrapping different kind of
	commands. Subclasses can implement certain methods so that they
	can be executed.
	This enables a command to be a command-line or code command.

	http://sourcemaking.com/design_patterns/command
	"""

	def __init__(self, delegate=None):
		super(Command, self).__init__()

		self.delegate = delegate

	def execute(self):
		pass


def overrides(interface_class):
	def overrider(method):
		assert(method.__name__ in dir(interface_class))
		return method
	return overrider
