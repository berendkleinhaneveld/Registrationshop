"""
Transformation

@author: Berend Klein Haneveld
"""

class Transformation(object):
	"""
	Model (abstract) class for transformations
	"""
	def __init__(self):
		super(Transformation, self).__init__()

		# Parameters
		self.parameters = [] # type: Parameters
		
		pass

	def name(self):
		if self.parameters:
			return self.parameters.Transform
		else:
			return "Name of transformation"
