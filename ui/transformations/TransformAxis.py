"""
Transformation Axes

:Authors:
	Berend Klein Haneveld
"""

import sys
import os
rootDir = os.path.dirname(os.path.realpath(__file__))
regPath = "../../../../src/registrationshop/"
joinedPath = os.path.join(rootDir, regPath)
sys.path.append(joinedPath)

from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QApplication
from PySide.QtGui import QMainWindow
from PySide.QtCore import QObject
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from vtk import vtkRenderer
from vtk import vtkRenderWindow
from vtk import vtkConeSource
from vtk import vtkPolyDataMapper
from vtk import vtkInteractorStyleTrackballCamera
from vtk import vtkActor
from vtk import vtkTransform
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from ui.Interactor import Interactor
from TranslateWidget import TranslateWidget
from ScaleWidget import ScaleWidget
from RotateWidget import RotateWidget


class CompleteTransformationWidget(QObject, Interactor):

	updatedTransform = Signal(object)  # vtkTransform

	def __init__(self, rwi, renderer, position):
		super(CompleteTransformationWidget, self).__init__()

		# TODO: apply transformation to all interface elements.
		# So the rotation of the rotate tool will also rotate
		# the translate and scale tool

		self.rwi = rwi
		self.renderer = renderer
		self.origin = position

		self.rotateTransform = vtkTransform()
		self.scaleTransform = vtkTransform()
		self.translateTransform = vtkTransform()
		self.completeTransform = vtkTransform()
		
		# 3 transforms to apply:
		# Scale
		# Rotate
		# Translate

		# The widgets will translate and rotate but not scale
		self.translateWidget = TranslateWidget()
		self.scaleWidget = ScaleWidget()
		self.rotateWidget = RotateWidget()

		self.translateWidget.setObjects(self.rwi, self.renderer, self.origin)
		self.scaleWidget.setObjects(self.rwi, self.renderer, self.origin)
		self.rotateWidget.setObjects(self.rwi, self.renderer, self.origin)

		self.translateWidget.updatedTransform.connect(self.transformUpdated)
		self.scaleWidget.updatedTransform.connect(self.transformUpdated)
		self.rotateWidget.updatedTransform.connect(self.transformUpdated)

		self.tag = self.rwi.AddObserver("KeyPressEvent", self.keyPressed, 1)

	@Slot()
	def transformUpdated(self):
		translation = self.translateWidget.getTranslation()
		scale = self.scaleWidget.getScale()
		rotation = self.rotateWidget.getRotation()  # transform
		rotation.Translate(-translation[0], -translation[1], -translation[2])

		transform = vtkTransform()
		transform.Translate(translation)  # Applied third
		transform.Concatenate(rotation)  # Applied second
		transform.Scale(scale)  # Applied first

		self.updatedTransform.emit(transform)

	def keyPressed(self, interactor, ev):
		key = interactor.GetKeyCode()
		if key not in 'zxc':
			return

		pos = self.translateWidget.representations[0].GetWorldPosition()
		self.rotateWidget.setPosition(pos)
		self.scaleWidget.setPosition(pos)

		if key == 'z':
			# switch to translate
			self.translateWidget.On()
			self.scaleWidget.Off()
			self.rotateWidget.Off()
		elif key == 'x':
			# switch to rotate
			self.translateWidget.Off()
			self.scaleWidget.Off()
			self.rotateWidget.On()
		elif key == 'c':
			# switch to scale
			self.translateWidget.Off()
			self.scaleWidget.On()
			self.rotateWidget.Off()
		self.rwi.GetRenderWindow().Render()


class RenderWindow(QWidget, Interactor):
	def __init__(self):
		super(RenderWindow, self).__init__()

		# Render, window and interactor
		self.renderer = vtkRenderer()
		self.renderer.SetBackground(0.1, 0.1, 0.1)
		self.renderer.SetBackground2(0.4, 0.4, 0.4)
		self.renderer.SetGradientBackground(True)

		self.renderWindow = vtkRenderWindow()
		self.renderWindow.AddRenderer(self.renderer)

		self.rwi = QVTKRenderWindowInteractor(parent=self)
		self.rwi.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
		self.rwi.GetRenderWindow().AddRenderer(self.renderer)

		# Create cone
		coneSource = vtkConeSource()
		coneSource.Update()
		coneMapper = vtkPolyDataMapper()
		coneMapper.SetInputConnection(coneSource.GetOutputPort())

		self.coneActor = vtkActor()
		self.coneActor.SetMapper(coneMapper)
		self.coneActor.GetProperty().SetColor(1, 1, 0)
		self.renderer.AddActor(self.coneActor)
		self.renderer.ResetCamera()

		self.completeTransformWidget = CompleteTransformationWidget(self.rwi, self.renderer, [0, 0, 0])
		self.completeTransformWidget.updatedTransform.connect(self.updatedTransform)

		self.setMinimumWidth(400)
		self.setMinimumHeight(400)

		layout = QGridLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.rwi, 0, 0)
		self.setLayout(layout)

	@Slot(object)
	def updatedTransform(self, transform):
		self.coneActor.SetUserTransform(transform)
		self.rwi.GetRenderWindow().Render()


if __name__ == '__main__':
	app = QApplication([])
	mw = QMainWindow()

	rw = RenderWindow()

	mw.setCentralWidget(rw)
	mw.raise_()
	mw.show()
	rw.rwi.Initialize()
	sys.exit(app.exec_())
