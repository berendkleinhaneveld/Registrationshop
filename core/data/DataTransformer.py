"""
DataTransformer

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkImageReslice


class DataTransformer(object):
	"""DataTransformer is a class that can transform a given dataset"""
	def __init__(self):
		super(DataTransformer, self).__init__()

	def TransformImageData(self, imageData, transform):
		"""
		:type imageData: vtkImageData
		:type transform: vtkTransform
		"""
		range = imageData.GetScalarRange()
		reslicer = vtkImageReslice()
		reslicer.SetInterpolationModeToCubic()
		reslicer.SetBackgroundLevel(range[0])
		reslicer.AutoCropOutputOff()
		reslicer.SetInputData(imageData)
		reslicer.SetResliceTransform(transform.GetInverse())
		reslicer.Update()

		return reslicer.GetOutput()
