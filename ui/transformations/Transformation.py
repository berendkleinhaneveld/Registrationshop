"""
Transformation

:Authors:
	Berend Klein Haneveld
"""


class Transformation(object):
	"""
	Transformation is a kind of container for adding
	meta-data to a transform, such as the kind of tool
	that produced the transform.
	Could be extended by adding creation time of transformation.
	"""

	TypeUser = "Manual transform"
	TypeLandmark = "Landmark transform"
	TypeDeformable = "Automatic transform"

	def __init__(self, transform, transformType, filename):
		super(Transformation, self).__init__()

		self.transform = transform
		self.transformType = transformType
		self.filename = filename
		self.landmarks = None
