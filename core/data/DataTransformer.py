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

	def TransformImageData(self, imageData, transform, infoData=None):
		"""
		The properties of infoData (optional) are used for generating the new dataset.
		The default is to use the properties of the given image data.

		:type imageData: vtkImageData
		:type transform: vtkTransform
		:type infoData: vtkImageData
		"""
		range = imageData.GetScalarRange()
		reslicer = vtkImageReslice()
		reslicer.SetInterpolationModeToCubic()
		if infoData:
			reslicer.SetInformationInput(infoData)
		reslicer.SetBackgroundLevel(range[0])
		reslicer.AutoCropOutputOff()
		reslicer.SetInputData(imageData)
		reslicer.SetResliceTransform(transform.GetInverse())
		reslicer.Update()

		return reslicer.GetOutput()
