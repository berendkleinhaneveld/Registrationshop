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

	TypeUser = "Free transform"
	TypeLandmark = "Landmark transform"
	TypeDeformable = "Deformable transform"

	def __init__(self, transform, transformType):
		super(Transformation, self).__init__()

		self.transform = transform
		self.transformType = transformType
