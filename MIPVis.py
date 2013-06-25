#!/usr/bin/python
"""
Renders a volume with MIP. Give a mhd file as the first argument.
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
		# self.imageData = imageReader.GetOutput()

		imageCaster = vtkImageCast()
		imageCaster.SetInput(imageReader.GetOutput())
		imageCaster.SetOutputScalarTypeToUnsignedShort()
		imageCaster.Update()
		self.imageData = imageCaster.GetOutput()

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
		# self.mapper = vtkVolumeRayCastMapper()
		self.mapper.SetBlendModeToMaximumIntensity()
		self.mapper.SetInput(self.imageData)
		
		self.volume = vtkVolume()
		self.volume.SetProperty(volumeProperty)
		self.volume.SetMapper(self.mapper)

		self.renderer.AddViewProp(self.volume)
		self.renderer.ResetCamera()
		
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
