"""
TransformationList

:Authors:
	Berend Klein Haneveld
"""
from vtk import vtkTransform
from vtk import vtkMatrix4x4


class TransformationList(object):
	"""
	TransformationList
	"""

	def __init__(self):
		super(TransformationList, self).__init__()

		self._transformations = []

	def completeTransform(self):
		return self.__getitem__(len(self._transformations))

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

	def __delitem__(self, index):
		del self._transformations[index]

	def __len__(self):
		return len(self._transformations)

	def __contains__(self, value):
		return value in self._transformations

	def append(self, value):
		self._transformations.append(value)
