import unittest
import os
from core.data import DataWriter
from core.data import DataReader


class DataWriterTest(unittest.TestCase):
	"""Test cases for the DataWriter class"""

	def setUp(self):
		self.writer = DataWriter()

	def tearDown(self):
		del self.writer

	def testDataWriter(self):
		path = os.path.dirname(os.path.abspath(__file__))
		fileName = path + "/data/hi-3.mhd"
		outputFolder = path + "/data/DataWriter"
		exportFileName = outputFolder + "/output.mhd"
		dataReader = DataReader()
		imageData = dataReader.GetImageData(fileName)
		fileType = DataReader.TypeMHD

		self.writer.WriteToFile(imageData, exportFileName, fileType)

		# Cleanup test directory
		try:
			if os.path.exists(outputFolder):
				import shutil
				shutil.rmtree(outputFolder)
		except Exception, e:
			raise e

	def testUnsupportedDataType(self):
		self.assertRaises(NotImplementedError, self.writer.WriteToFile, None, "", DataReader.TypeRaw)

	def testSuppportedExtensions(self):
		extensions = self.writer.GetSupportedExtensionsAsString()
		self.assertIn("vti", extensions)
		self.assertIn("mhd", extensions)
