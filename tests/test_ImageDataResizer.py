import unittest
from core.data import DataResizer
from vtk import vtkImageData
from vtk import VTK_FLOAT


class DataResizerTest(unittest.TestCase):

	def setUp(self):
		self.imageResizer = DataResizer()

	def tearDown(self):
		del self.imageResizer

	def testDataResizer(self):
		self.assertTrue(True)

	def testDataResizerDimensions(self):
		dimensions = [512, 512, 196]
		factor = 0.125
		imageData = createImageData(dimensions)

		resizedData = self.imageResizer.ResizeData(imageData, factor)

		newDimensions = resizedData.GetDimensions()

		self.assertEquals(newDimensions[0], 256)
		self.assertEquals(newDimensions[1], 256)
		self.assertEquals(newDimensions[2], 98)

	def testCalculateFactor(self):
		dimensions = [512, 512, 196]
		maxVoxels = 17500000

		factor = self.imageResizer.calculateFactor(dimensions, maxVoxels)

		voxels = int(factor * dimensions[0] * dimensions[1] * dimensions[2])
		self.assertLessEqual(voxels, maxVoxels)

	def testDataResizerMaxVoxels(self):
		dimensions = [512, 512, 196]
		maxVoxels = 17500000
		imageData = createImageData(dimensions)

		resizedData = self.imageResizer.ResizeData(imageData, maximum=maxVoxels)

		newDimensions = resizedData.GetDimensions()

		numberOfVoxels = newDimensions[0] * newDimensions[1] * newDimensions[2]
		self.assertLessEqual(numberOfVoxels, maxVoxels)

	def testResizerShouldNotEnlarge(self):
		dimensions = [12, 13, 14]
		maxVoxels = 17500000
		imageData = createImageData(dimensions)

		resizedData = self.imageResizer.ResizeData(imageData, maximum=maxVoxels)

		newDimensions = resizedData.GetDimensions()

		self.assertEquals(dimensions[0], newDimensions[0])
		self.assertEquals(dimensions[1], newDimensions[1])
		self.assertEquals(dimensions[2], newDimensions[2])


# Helper method

def createImageData(dimensions):
	imageData = vtkImageData()
	imageData.Initialize()
	imageData.SetDimensions(dimensions)
	imageData.AllocateScalars(VTK_FLOAT, 1)
	return imageData
