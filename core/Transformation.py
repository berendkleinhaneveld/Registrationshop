"""
Transformation

@author: Berend Klein Haneveld
"""

try:
	from PySide.QtCore import QObject
except ImportError:
	raise ImportError("Could not import PySide")

class Transformation(QObject):
	"""
	Model (abstract) class for transformations
	"""
	def __init__(self):
		super(Transformation, self).__init__()
		
		pass
