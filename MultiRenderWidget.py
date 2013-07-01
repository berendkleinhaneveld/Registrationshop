"""
MultiRenderWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import *
# from libvtkGPUMultiVolumeRenderPython import vtkOpenGLGPUMultiVolumeRayCastMapper
from vtk import vtkRenderer
from vtk import vtkInteractorStyleTrackballCamera
from ui.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MultiRenderWidget(QWidget):
	"""
	MultiRenderWidget
	"""

	def __init__(self):
		super(MultiRenderWidget, self).__init__()

		self.renderer = vtkRenderer()
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetGradientBackground(True)

		self.rwi = QVTKRenderWindowInteractor(parent=self)
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)
