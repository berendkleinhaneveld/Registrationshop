"""
TransformationList

:Authors:
	Berend Klein Haneveld
"""
from vtk import vtkTransform
from PySide.QtCore import QObject
from PySide.QtCore import Signal
from Transformation import Transformation
from core.vtkObjectWrapper import vtkTransformWrapper
from core.vtkDrawing import TransformWithMatrix
from core.project import ProjectController


class TransformationList(QObject):
	"""
	TransformationList that serves as a list of vtkTransform objects.
	By querying a certain index it will return a vtkTransform that is
	a concatination of all transforms up to (and including) that index.
	"""
	transformationChanged = Signal(object)

	def __init__(self):
		super(TransformationList, self).__init__()

		self._transformations = []
		self._cachedTransformation = None
		self._activeIndex = 0
		self._dirty = True

	def activateTransformationAtIndex(self, index):
		if index < 0:
			self._setActiveIndex(len(self._transformations)-1)
		else:
			self._setActiveIndex(index)

	def completeTransform(self):
		"""
		Use this function instead of transformationList[-1] to get
		a cached version of the complete transformation matrix.
		"""
		if self._dirty:
			self._cachedTransformation = self.transform(self._activeIndex)
			self._dirty = False
		return self._cachedTransformation

	def copyFromTransformations(self, other):
		"""
		Performs deep copy.
		"""
		self._transformations = []
		for transformation in other._transformations:
			self._transformations.append(transformation)
		self._dirty = True
		self.transformationChanged.emit(self)

	def clear(self):
		"""
		Clears out all the transformations.
		"""
		self._transformations = []
		self._dirty = True

	def scalingTransform(self):
		"""
		For now, just return the complete transformation.
		It is a very complex problem to remove rotation from
		a transformation matrix that requires another more
		sophisticated solution.
		"""
		transform = self.completeTransform()
		return transform

	def transform(self, index):
		tempTransform = vtkTransform()
		tempTransform.PreMultiply()

		# Check for all the transforms that have the same filename
		# as the one at a certain index
		idx = index
		if idx < len(self._transformations) and idx >= 0:
			filename = self._transformations[idx].filename
			# print filename
			while idx >= 0 and self._transformations[idx].filename == filename:
				tempTransform.Concatenate(self._transformations[idx].transform)
				idx -= 1
			tempTransform.Update()

		transform = TransformWithMatrix(tempTransform.GetMatrix())
		return transform

	# Methods for loading and saving to file

	def getPythonVersion(self):
		"""
		Returns an object that can be written to file by
		yaml. It creates a list of tuples where each tuple
		consists out of the transformation type, a wrapped
		vtkTransform and the filename.
		"""
		result = list()
		for transformation in self._transformations:
			# First wrap the transform
			transformWrap = vtkTransformWrapper(transformation.transform)
			wrappedTransform = dict()
			# Create a dict with all the information
			wrappedTransform["TransformationType"] = transformation.transformType
			wrappedTransform["Transformation"] = transformWrap
			wrappedTransform["Filename"] = transformation.filename
			wrappedTransform["Landmarks"] = transformation.landmarks
			result.append(wrappedTransform)
		return result

	def setPythonVersion(self, transformWrappers):
		"""
		Unwraps the wrapped transformations into this
		transformation list.
		"""
		self._transformations = []
		self._dirty = True

		for wrappedTransformation in transformWrappers:
			if isinstance(wrappedTransformation, dict):
				transformType = wrappedTransformation["TransformationType"]
				transform = wrappedTransformation["Transformation"].originalObject()
				filename = wrappedTransformation["Filename"]
				landmarks = wrappedTransformation["Landmarks"]
				# Create new transformation
				transformation = Transformation(transform, transformType, filename)
				transformation.landmarks = landmarks
				self._transformations.append(transformation)
			elif isinstance(wrappedTransformation, list):
				# Get the transform type
				transformType = wrappedTransformation[0]
				# Get the wrapped transform and unwrap immediately
				transform = wrappedTransformation[1].originalObject()
				# Get the filename
				filename = wrappedTransformation[2]
				# Add the transform to the internal transformations
				self._transformations.append(Transformation(transform, transformType, filename))

		self.transformationChanged.emit(self)

	def _setActiveIndex(self, index):
		"""
		Updates the active index. Makes cached transformation dirty and
		sends out a signal that the transformation changed.
		"""
		if self._activeIndex != index:
			self._activeIndex = index
			self._dirty = True
			if index >= 0 and index < len(self._transformations):
				projectController = ProjectController.Instance()
				projectController.loadMovingDataSet(self._transformations[index].filename)
			self.transformationChanged.emit(self)

	# Override methods for list behaviour

	def __getitem__(self, index):
		return self._transformations[index]

	def __setitem__(self, index, value):
		assert type(value) == Transformation
		self._transformations[index] = value
		self._dirty = True
		self.transformationChanged.emit(self)

	def __delitem__(self, index):
		del self._transformations[index]
		if self._activeIndex >= len(self._transformations):
			self._activeIndex = len(self._transformations)-1
		self._dirty = True
		self.transformationChanged.emit(self)

	def __len__(self):
		return len(self._transformations)

	def __contains__(self, value):
		return value in self._transformations

	def append(self, value):
		"""
		:type value: Transformation
		"""
		assert type(value) == Transformation
		self._transformations.append(value)
		self._activeIndex = len(self._transformations)-1
		self._dirty = True
		self.transformationChanged.emit(self)
