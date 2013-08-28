"""
DataResizer

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkImageResample


class DataResizer(object):
	"""
	DataResizer is a tool that will resize a given image dataset.
	You can specify a certain magnification factor or you can use a maximum
	number of voxels that it should contain. If the image is larger than the
	maximum amount of voxels, it will resize the volume to just below the
	specified maximum.
	It will never upscale a volume! So factor value that are higher than 1.0
	will not have any result.
	"""

	def __init__(self):
		super(DataResizer, self).__init__()

	def ResizeData(self, imageData, factor=1.0, maximum=0):
		self.imageResampler = vtkImageResample()
		self.imageResampler.SetInterpolationModeToLinear()
		self.imageResampler.SetInputData(imageData)

		# If a maximum has been set: calculate the right factor
		if maximum > 0:
			factor = self.calculateFactor(imageData.GetDimensions(), maximum)

		# Make sure that we are never upscaling the data
		if factor > 1.0:
			factor = 1.0

		# The factor is now only in amount of pixels. This has to be translated
		# to each of the dimensions: factor^(1/3)
		axisMagnificationFactor = pow(factor, 1.0/3.0)

		self.resampledImageData = None
		if factor != 1.0:
			self.imageResampler.SetAxisMagnificationFactor(0, axisMagnificationFactor)
			self.imageResampler.SetAxisMagnificationFactor(1, axisMagnificationFactor)
			self.imageResampler.SetAxisMagnificationFactor(2, axisMagnificationFactor)
			self.imageResampler.Update()
			self.resampledImageData = self.imageResampler.GetOutput()
		else:
			self.resampledImageData = imageData

		return self.resampledImageData

	# Private methods

	def calculateFactor(self, dimensions, maximum):
		voxels = dimensions[0] * dimensions[1] * dimensions[2]
		factor = float(maximum) / float(voxels)
		return factor
