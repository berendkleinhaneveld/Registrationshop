#!/usr/bin/python
"""
Renders a volume with MIP. Give a mhd file as the first argument.

This exposes a bug in VTK where it will say something like: read buffer error
"""

from vtk import *

class MIPVis(object):
	def __init__(self, fileName):
		super(MIPVis, self).__init__()

		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)

		self.renderWindow = vtkRenderWindow()
		self.renderWindow.SetSize(512, 512)
		self.renderWindow.AddRenderer(self.renderer)

		self.rwi = vtkRenderWindowInteractor()
		self.rwi.SetRenderWindow(self.renderWindow)
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())

		imageReader = vtkMetaImageReader()
		imageReader.SetFileName(fileName)
		imageReader.Update()
		imageData = imageReader.GetOutput()

		# Make sure that the data is not too big
		self.imageData = self.ResizeData(imageData, maximum=25000000)

		self.minimum, self.maximum = self.imageData.GetScalarRange()

		colorFunction = vtkColorTransferFunction()
		colorFunction.AddRGBSegment(0.0, 1.0, 1.0, 1.0, 255.0, 1, 1, 1)

		opacityFunction = vtkPiecewiseFunction()
		opacityFunction.AddSegment(self.minimum, 0.0,
								   self.maximum, 1.0)

		volumeProperty = vtkVolumeProperty()
		volumeProperty.SetIndependentComponents(True);
		volumeProperty.SetInterpolationTypeToLinear();
		volumeProperty.SetColor(colorFunction)
		volumeProperty.SetScalarOpacity(opacityFunction)

		self.mapper = vtkGPUVolumeRayCastMapper()
		self.mapper.SetBlendModeToMaximumIntensity()
		self.mapper.SetInputData(self.imageData)
		
		self.volume = vtkVolume()
		self.volume.SetProperty(volumeProperty)
		self.volume.SetMapper(self.mapper)

		self.renderer.AddViewProp(self.volume)
		self.renderer.ResetCamera()
		
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

	def calculateFactor(self, dimensions, maximum):
		voxels = dimensions[0] * dimensions[1] * dimensions[2]
		factor = float(maximum) / float(voxels)
		return factor

if __name__ == '__main__':
	import os, sys
	if len(sys.argv) > 1:
		mhdFileName = sys.argv[1]
		if not os.path.exists(mhdFileName):
			print "File '" + mhdFileName + "' does not exist."
			sys.exit(0)
	else:
		print "Please provide a file (*.mhd) as first argument for this script."
		sys.exit(0)
	
	visualization = MIPVis(mhdFileName)
	visualization.renderWindow.Render()
	
	if sys.platform != "darwin":
		visualization.rwi.Initialize()

	visualization.rwi.Start()
