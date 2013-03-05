"""
Strategy

Strategy is the complete tree of transformations and registration results.

@author: Berend Klein Haneveld
"""

try:
	from PySide.QtCore import QObject
except ImportError as e:
	raise e

class Strategy(QObject):
	"""
	"""
	def __init__(self):
		super(Strategy, self).__init__()
		
		# Properties
		self.rootNode = None

		pass
