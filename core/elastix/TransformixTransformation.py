"""
TransformixTransformation

:Authors:
	Berend Klein Haneveld
"""
from ParameterList import ParameterList
from Parameter import Parameter
from core.data import DataReader
from vtk import vtkMatrix4x4


class TransformixTransformation(object):
	"""
	TransformixTransformation
	"""

	def __init__(self, dataset, transform):
		"""
		:type transform: vktTransform
		"""
		super(TransformixTransformation, self).__init__()

		self.dataset = dataset
		self.transform = transform

	def transformation(self):
		transformation = ParameterList()
		transformation.append(Parameter("Transform", "AffineTransform"))

		transformMatrix = self.transform.GetMatrix()
		matrix = vtkMatrix4x4()
		matrix.DeepCopy(transformMatrix)
		matrix.Invert()
		elemList = listFromMatrix(matrix)
		imageReader = DataReader()
		imageData = imageReader.GetImageData(self.dataset)
		if not imageData:
			raise Exception("Could not create image data")

		scalarType = imageData.GetScalarTypeAsString()
		dimensions = list(imageData.GetDimensions())
		spacing = list(imageData.GetSpacing())
		center = map(lambda x: x / 2.0, dimensions)

		if not scalarType or not dimensions or not spacing:
			raise Exception("Could not get the needed parameters")

		transformation.append(Parameter("NumberOfParameters", len(elemList)))
		transformation.append(Parameter("TransformParameters", elemList))
		transformation.append(Parameter("InitialTransformParametersFileName", "NoInitialTransform"))
		transformation.append(Parameter("HowToCombineTransforms", "Compose"))
		transformation.append(Parameter("MovingImageDimension", 3))
		transformation.append(Parameter("FixedImageDimension", 3))

		# The following options are from the dataset
		transformation.append(Parameter("FixedInternalImagePixelType", scalarType))
		transformation.append(Parameter("MovingInternalImagePixelType", scalarType))
		transformation.append(Parameter("Size", dimensions))
		transformation.append(Parameter("Spacing", spacing))
		transformation.append(Parameter("CenterOfRotation", center))
		return transformation


def listFromMatrix(matrix):
	"""
	Returns list of the elements of a vtkMatrix4x4 object.
	:type matrix: vtkMatrix4x4
	"""
	result = []
	for j in range(3):
		for i in range(3):
			element = matrix.GetElement(i, j)
			result.append(element)
		for k in range(3):
			element = matrix.GetElement(k, 3)
			result.append(element)
	return result
