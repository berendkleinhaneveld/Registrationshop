__author__ = 'Berend Klein Haneveld'

try:
	from vtk import *
except ImportError:
	print ImportError("Could not import vtk")

class Project():
	def __init__(self, name=None, fixedDataSet=None, movingDataSet=None, isReference=True):
		"""
		@param name: Project file name
		@type name: basestring
		@param fixedDataSet: Fixed data set name
		@type fixedDataSet: basestring
		@param movingDataSet: Moving data set name
		@type movingDataSet: basestring
		@param isReference: Whether source data sets are to be contained in project folder
		@type isReference: bool
		"""
		self._name = name
		self._isReference = isReference
		self._fixedDataSetName = fixedDataSet
		self._movingDataSetName = movingDataSet

	def setName(self, name):
		self._name = name

	def name(self):
		return self._name

	def setFixedDataSet(self, name=None):
		"""
		@param name: File name of fixed data set
		@type name: basestring
		"""
		self._fixedDataSetName = name
		imageReader = vtk.vtkMetaImageReader()
		for string in dir(imageReader):
			if len(string) > 3 and string[0] == "G":
				print string
		imageReader.SetFileName(self._fixedDataSetName)

		toet = imageReader.GetOutput()
		print toet


#		print dir(imageReader)

#		self._fixedDataSet

	def setMovingDataSet(self, name=None):
		self._movingDataSetName = name

	def setIsReference(self, reference=True):
		"""
		@param reference: Whether source data sets are to be contained in project folder
		@type reference: bool
		"""
		self._isReference = reference