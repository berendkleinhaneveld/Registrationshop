"""
TransformationList

:Authors:
	Berend Klein Haneveld
"""
import math
from vtk import vtkTransform
from vtk import vtkMatrix4x4
from PySide.QtCore import QObject
from PySide.QtCore import Signal


class TransformationList(QObject):
	"""
	TransformationList
	"""
	transformationChanged = Signal(object)

	def __init__(self):
		super(TransformationList, self).__init__()

		self._transformations = []

	def completeTransform(self):
		return self.__getitem__(len(self._transformations))

	def scalingTransform(self):
		# Specify 4 points / 3 vectors (identity?)
		# Multiply these points by the full matrix
		# The lengths of the new vectors are the
		# scaling values.
		transform = self.completeTransform()

		point0 = [0.0, 0.0, 0.0]
		point1 = [1.0, 0.0, 0.0]
		point2 = [0.0, 1.0, 0.0]
		point3 = [0.0, 0.0, 1.0]

		point0 = [10.0, 10.0, 10.0]
		point1 = [11.0, 10.0, 10.0]
		point2 = [10.0, 11.0, 10.0]
		point3 = [10.0, 10.0, 11.0]

		trans0 = transform.TransformPoint(point0)
		trans1 = transform.TransformPoint(point1)
		trans2 = transform.TransformPoint(point2)
		trans3 = transform.TransformPoint(point3)

		vec1 = SubtractVector(trans1, trans0)
		vec2 = SubtractVector(trans2, trans0)
		vec3 = SubtractVector(trans3, trans0)

		shearX = DotProduct(vec1, vec2)
		shearY = DotProduct(vec2, vec3)
		shearZ = DotProduct(vec3, vec1)

		# print "ShearX:", shearX
		# print "ShearY:", shearY
		# print "ShearZ:", shearZ

		matrix = vtkMatrix4x4()
		matrix.Identity()
		matrix.SetElement(0, 0, Length(vec1))
		matrix.SetElement(1, 1, Length(vec2))
		matrix.SetElement(2, 2, Length(vec3))
		matrix.SetElement(0, 1, shearX)
		matrix.SetElement(1, 0, shearX)
		matrix.SetElement(2, 1, shearY)
		matrix.SetElement(1, 2, shearY)
		matrix.SetElement(2, 0, shearZ)
		matrix.SetElement(0, 2, shearZ)

		result = vtkTransform()
		result.SetMatrix(matrix)
		# result.Scale(Length(vec1), Length(vec2), Length(vec3))
		return result

	# Override methods for list behaviour

	def __getitem__(self, index):
		tempTransform = vtkTransform()
		tempTransform.PostMultiply()
		for transform in self._transformations[0:index]:
			tempTransform.Concatenate(transform)

		matrix = vtkMatrix4x4()
		matrix.DeepCopy(tempTransform.GetMatrix())
		
		result = vtkTransform()
		result.SetMatrix(matrix)
		return result

	def __setitem__(self, index, value):
		self._transformations[index] = value
		self.transformationChanged.emit(self)

	def __delitem__(self, index):
		del self._transformations[index]
		self.transformationChanged.emit(self)

	def __len__(self):
		return len(self._transformations)

	def __contains__(self, value):
		return value in self._transformations

	def append(self, value):
		self._transformations.append(value)
		self.transformationChanged.emit(self)


def SubtractVector(vec1, vec2):
	result = []
	for i in range(len(vec1)):
		result.append(vec1[i] - vec2[i])
	return result


def Length(vec):
	sq = map(lambda x: x**2, vec)
	sumsq = sum(sq)
	return math.sqrt(sumsq)


def DotProduct(vec1, vec2):
	result = 0.0
	for i in range(len(vec1)):
		result += (vec1[i] * vec2[i])
	return result
