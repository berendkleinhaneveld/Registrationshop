"""
ImageDataResizer

:Authors:
	Berend Klein Haneveld
"""

from vtk import vtkImageResample

class ImageDataResizer(object):
	"""
	ImageDataResizer is a tool that will resize a given image dataset.
	You can specify a certain magnification factor or you can use a maximum 
	number of voxels that it should contain. If the image is larger than the 
	maximum amount of voxels, it will resize the volume to just below the 
	specified maximum.
	It will never upscale a volume! So factor value that are higher than 1.0
	will not have any result.

	http://vtk.1045678.n5.nabble.com/vtkImageReslice-and-vtkImageResample-different-behaviour-between-32-bit-and-64-bit-platform-td3358830.html
	"""

	def __init__(self):
		super(ImageDataResizer, self).__init__()

	def ResizeData(self, imageData, factor=1.0, maximum=0):
		self.imageResampler = vtkImageResample()
		self.imageResampler.SetInterpolationModeToLinear()
		self.imageResampler.SetInput(imageData)
		
		# If a maximum has been set: calculate the right factor
		if maximum > 0:
			factor = self.calculateFactor(imageData.GetDimensions(), maximum)

		# Make sure that we are never upscaling the data
		if factor > 1.0:
			factor = 1.0

		self.resampledImageData = None
		if factor != 1.0:	
			self.imageResampler.SetAxisMagnificationFactor(0, factor)
			self.imageResampler.SetAxisMagnificationFactor(1, factor)
			self.imageResampler.SetAxisMagnificationFactor(2, factor)
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
