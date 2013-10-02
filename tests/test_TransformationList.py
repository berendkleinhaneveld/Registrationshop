import unittest
from ui.transformations.TransformationList import TransformationList
from vtk import *


class TransformationListTest(unittest.TestCase):

	def setUp(self):
		self.transformList = TransformationList()

	def tearDown(self):
		del self.transformList

	def testTransformationList(self):
		transform = vtkTransform()
		self.transformList.append(transform)
		self.assertEquals(len(self.transformList._transformations), 1)

		completeTransform = self.transformList.completeTransform()
		self.assertIsNotNone(completeTransform)

		matrix = completeTransform.GetMatrix()

		self.assertEquals(matrix.GetElement(0, 0), 1)
		self.assertEquals(matrix.GetElement(1, 1), 1)
		self.assertEquals(matrix.GetElement(2, 2), 1)
		self.assertEquals(matrix.GetElement(3, 3), 1)
		self.assertEquals(matrix.GetElement(1, 3), 0)

		transform = vtkTransform()
		transform.Scale(2.0, 2.0, 2.0)

		self.transformList.append(transform)
		self.assertEquals(len(self.transformList._transformations), 2)
		self.assertNotEquals(self.transformList[0], self.transformList[1])

		completeTransform = self.transformList.completeTransform()
		matrix = completeTransform.GetMatrix()
		self.assertEquals(matrix.GetElement(0, 0), 2)
		self.assertEquals(matrix.GetElement(1, 1), 2)
		self.assertEquals(matrix.GetElement(2, 2), 2)
		self.assertEquals(matrix.GetElement(3, 3), 1)
		self.assertEquals(matrix.GetElement(1, 3), 0)

		transform = vtkTransform()
		transform.Translate(3.0, 3.0, 3.0)

		self.transformList.append(transform)
		self.assertEquals(len(self.transformList._transformations), 3)
		self.assertNotEquals(self.transformList[1], self.transformList[2])

		completeTransform = self.transformList.completeTransform()
		matrix = completeTransform.GetMatrix()

		self.assertEquals(matrix.GetElement(0, 0), 2)
		self.assertEquals(matrix.GetElement(1, 1), 2)
		self.assertEquals(matrix.GetElement(2, 2), 2)
		self.assertEquals(matrix.GetElement(3, 3), 1)
		self.assertEquals(matrix.GetElement(0, 3), 3)
		self.assertEquals(matrix.GetElement(1, 3), 3)
		self.assertEquals(matrix.GetElement(2, 3), 3)

		transform = vtkTransform()
		transform.RotateX(90.0)
		
		self.transformList.append(transform)

		prevTransform = self.transformList[3]
		prevMatrix = prevTransform.GetMatrix()

		self.assertEquals(prevMatrix.GetElement(0, 0), 2)
		self.assertEquals(prevMatrix.GetElement(1, 1), 2)
		self.assertEquals(prevMatrix.GetElement(2, 2), 2)
		self.assertEquals(prevMatrix.GetElement(3, 3), 1)
		self.assertEquals(prevMatrix.GetElement(0, 3), 3)
		self.assertEquals(prevMatrix.GetElement(1, 3), 3)
		self.assertEquals(prevMatrix.GetElement(2, 3), 3)
