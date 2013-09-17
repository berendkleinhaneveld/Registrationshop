import unittest
import os
from core.data import DataReader


class DataReaderTest(unittest.TestCase):

	def setUp(self):
		self.reader = DataReader()

	def tearDown(self):
		del self.reader

	def testDataReader(self):
		path = os.path.dirname(os.path.abspath(__file__))

		fileName = path + "/data/hi-3.mhd"
		imageData = self.reader.GetImageData(fileName)
		self.assertIsNotNone(imageData)
		dimensions = imageData.GetDimensions()
		self.assertEquals(dimensions, (21, 15, 9))

	def testUnsupportedDataTypes(self):
		self.assertRaises(Exception, self.reader.GetImageData, "data/hi-3.mrb")

	def testSupportedDataTypes(self):
		self.assertTrue(self.reader.IsExtensionSupported("mhd"))
		self.assertTrue(self.reader.IsExtensionSupported("vti"))
		self.assertTrue(self.reader.IsExtensionSupported("dcm"))

		self.assertFalse(self.reader.IsExtensionSupported("mrb"))
		self.assertFalse(self.reader.IsExtensionSupported("vtk"))
		self.assertFalse(self.reader.IsExtensionSupported("raw"))
		self.assertFalse(self.reader.IsExtensionSupported("dat"))

	# def testDatFileFormat(self):
	# 	path = os.path.dirname(os.path.abspath(__file__))
	# 	fileName = path + "/data/present492x492x442.dat"

	# 	imageData = self.reader.GetImageData(fileName)
	# 	dimensions = imageData.GetDimensions()
	# 	self.assertEquals(dimensions, (492, 492, 442))

	def testVTIFileFormat(self):
		path = os.path.dirname(os.path.abspath(__file__))
		fileName = path + "/data/modelSegmentation.vti"
		imageData = self.reader.GetImageData(fileName)
		dimensions = imageData.GetDimensions()
		self.assertEquals(dimensions, (376, 245, 206))

	def testEmptyDirectory(self):
		path = os.path.dirname(os.path.abspath(__file__))
		fileName = path + "/data"
		imageData = self.reader.GetImageData(fileName)
		self.assertIsNone(imageData)

	def testDICOMFileFormat(self):
		path = os.path.dirname(os.path.abspath(__file__))
		fileName = path + "/data/DICOM"
		imageData = self.reader.GetImageData(fileName)
		self.assertIsNotNone(imageData)
		dimensions = imageData.GetDimensions()
		self.assertEquals(dimensions, (320, 384, 11))
