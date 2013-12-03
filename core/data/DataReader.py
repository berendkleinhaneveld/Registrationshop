"""
DataReader

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkImageData
from vtk import vtkMetaImageReader
from vtk import vtkXMLImageDataReader
from vtk import vtkDICOMImageReader
from vtk import vtkNrrdReader
from DataController import DataController
import os


class DataReader(DataController):
	"""
	DataReader is a class that tries to figure out what kind of data type a
	given file is. From the extension it will try to choose the correct reader
	from vtk.
	"""

	# File extensions
	TypeMHA = "mha"  # vtkMetaImageReader
	TypeMHD = "mhd"  # vtkMetaImageReader
	TypeVTI = "vti"  # vtkXMLImageDataReader
	TypeMRB = "mrb"  # Unreadable at the moment (Slicer stuff)
	TypeVTK = "vtk"  # No real volume data... but might be used for polygon stuff
	TypeRaw = "raw"  # needs a mhd file... maybe choose some standard stuff
	TypeDAT = "dat"  # should be read byte by byte
	TypeDICOM = "dcm"  # Dicom does not really have an extension?
	TypeNRRD = "nrrd"  # Nearly Raw Raster Data

	def __init__(self):
		super(DataReader, self).__init__()

		self.supportedExtensions = [DataReader.TypeMHA,
									DataReader.TypeMHD,
									DataReader.TypeVTI,
									DataReader.TypeDICOM,
									DataReader.TypeNRRD]

	def GetImageData(self, fileName):
		"""
		:type fileName: basestr
		:rtype: vtkImageData
		"""
		# First, check if it is a directory, that is used for dicom images
		if os.path.isdir(fileName):
			# Check if the directory really contains DICOM images
			files = [f for f in os.listdir(fileName) if f.endswith("."+DataReader.TypeDICOM)]
			if len(files) > 0:
				return self.GetImageDataFromDirectory(fileName)
			else:
				# TODO: make this a proper Exception
				print "Warning: directory does not contain DICOM files:", fileName
				return None

		baseFileName, extension = fileName.rsplit(".", 1)
		if not self.IsExtensionSupported(extension):
			raise Exception(extension + " is not supported.")
		imageData = self.GetImageDataForBaseAndExtension(fileName, extension)
		return imageData

	def GetImageDataForBaseAndExtension(self, fileName, extension):
		"""
		:type fileName: basestring
		:type extension: basestring
		:rtype: vtkImageData
		"""
		if extension == DataReader.TypeMHA or extension == DataReader.TypeMHD:
			# Use a vktMetaImageReader
			imageReader = vtkMetaImageReader()
			imageReader.SetFileName(fileName)
			imageReader.Update()
			return imageReader.GetOutput()
		elif extension == DataReader.TypeDICOM:
			# Use a dicom reader
			dirName = os.path.dirname(fileName)
			return self.GetImageDataFromDirectory(dirName)
		elif extension == DataReader.TypeDAT:
			raise Exception("Support for .dat files is not implemented.")
			# Read in the .dat file byte by byte
			imageData = None

			import numpy as np
			with open(fileName, "rb") as f:
				dimensions = np.fromfile(f, np.int16, count=3)
				imageData = vtkImageData()
				imageData.SetDimensions(int(dimensions[0]), int(dimensions[1]), int(dimensions[2]))
				imageData.SetScalarTypeToFloat()
				imageData.SetNumberOfScalarComponents(1)
				imageData.AllocateScalars()
				imageData.Update()
				imageData.PrepareForNewData()

				fileData = np.fromfile(f, np.int16)

				dataIndex = 0
				for z in range(int(dimensions[2])):
					for y in range(int(dimensions[1])):
						for x in range(int(dimensions[0])):
							imageData.SetScalarComponentFromFloat(x, y, z, 0, float(fileData[dataIndex]))
							dataIndex += 1

			return imageData
		elif extension == DataReader.TypeVTI:
			# Use a XMLImageReader
			imageReader = vtkXMLImageDataReader()
			imageReader.SetFileName(fileName)
			imageReader.Update()
			return imageReader.GetOutput()
		elif extension == DataReader.TypeNRRD:
			# Use a NrrdReader
			imageReader = vtkNrrdReader()
			imageReader.SetFileName(fileName)
			imageReader.Update()
			return imageReader.GetOutput()
		else:
			assert False

	def GetImageDataFromDirectory(self, dirName):
		"""
		This method is just for DICOM image data. So input is a directory name
		and it will output an vtkImageData object.
		:type dirName: basestr
		:rtype: vtkImageData
		"""
		imageReader = vtkDICOMImageReader()
		imageReader.SetDirectoryName(dirName)
		imageReader.Update()
		imageData = imageReader.GetOutput()
		self.SanitizeImageData(imageReader, imageData)
		return imageData

	def SanitizeImageData(self, reader, imageData):
		"""
		Sanitizes the given imageData. At the moment it just checks the
		spacings to see if there are spacings that zero. This gives problems
		with rendering the data.
		"""
		# Check the image data to see if the spacings are correct
		spacing = list(imageData.GetSpacing())
		# TODO: make this more pythonic...
		for x in range(len(spacing)):
			if spacing[x] == 0.0:
				spacing[x] = 1.0
				# TODO: instead of 1.0, use a more sane value...
				# Or at least check whether it is the right thing to do
		imageData.SetSpacing(spacing)
