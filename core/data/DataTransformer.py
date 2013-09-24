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
		reslicer = vtkImageReslice()
		reslicer.SetInterpolationModeToCubic()
		range = imageData.GetScalarRange()
		reslicer.SetBackgroundLevel(range[0])
		# reslicer.SetAutoCropOutput(1)  # Not sure if this is what we want

		reslicer.SetInputData(imageData)
		reslicer.SetResliceTransform(transform.GetInverse())
		reslicer.Update()

		return reslicer.GetOutput()
