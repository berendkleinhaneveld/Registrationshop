"""
DataWriter.py
"""

from DataController import DataController
from DataReader import DataReader
from vtk import vtkMetaImageWriter
from vtk import vtkXMLImageDataReader


class DataWriter(DataController):
	"""
	DataWriter writes an image data object to
	disk using the provided format.
	"""
	def __init__(self):
		super(DataWriter, self).__init__()

		self.supportedExtensions = [DataReader.TypeMHA,
									DataReader.TypeVTI]

	def WriteToFile(self, imageData, exportFileName, fileType):
		if fileType == DataReader.TypeMHA:
			writer = vtkMetaImageWriter()
			writer.SetFileName(exportFileName)
			writer.SetInputData(imageData)
			writer.Write()
		elif fileType == DataReader.TypeVTI:
			writer = vtkXMLImageDataReader()
			writer.SetFileName(exportFileName)
			writer.SetInputData(imageData)
			writer.Write()
		else:
			raise NotImplementedError("No writing support for type " + str(fileType))