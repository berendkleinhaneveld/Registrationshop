"""
RotateWidget

:Authors:
	Berend Klein Haneveld
"""
from TransformWidget import TransformWidget
from core.vtkDrawing import CreateTorus
from vtk import vtkPolygonalHandleRepresentation3D
from vtk import vtkHandleWidget
from vtk import vtkMatrix4x4
from vtk import vtkTransform


class RotateWidget(TransformWidget):
	def __init__(self):
		super(RotateWidget, self).__init__()

	def _internalInit(self):
		for i in range(3):
			direction = [0, 0, 0]
			direction[i] = 1.0
			torus, torusPoly = CreateTorus([0, 0, 0], direction, i)

			rep = vtkPolygonalHandleRepresentation3D()
			rep.GetProperty().SetColor(direction)
			rep.SetWorldPosition(self.pos)
			rep.SetConstrainedAxis(i)
			rep.SetInteractionMode(2)
			rep.SetHandle(torusPoly)
			self.representations.append(rep)

			handleWidget = vtkHandleWidget()
			handleWidget.SetInteractor(self.rwi)
			handleWidget.SetDefaultRenderer(self.renderer)
			handleWidget.SetEnableAxisConstraint(True)
			handleWidget.SetRepresentation(rep)
			handleWidget.AddObserver("InteractionEvent", self.interactionCallback)
			self.handles.append(handleWidget)

	def interactionCallback(self, interactor, ev):
		weirdTransform = interactor.GetRepresentation().GetTransform()

		matrix = vtkMatrix4x4()
		matrix.DeepCopy(weirdTransform.GetMatrix())

		transform = vtkTransform()
		transform.SetMatrix(matrix)

		for handle in self.handles:
			if handle is interactor:
				continue
			handle.GetRepresentation().SetTransform(transform)
			handle.GetRepresentation().SetTransformation(interactor.GetRepresentation().GetTransformation())

		self.updatedTransform.emit()

	def getRotation(self):
		weirdTransform = self.representations[0].GetTransform()
		matrix = vtkMatrix4x4()
		matrix.DeepCopy(weirdTransform.GetMatrix())

		transform = vtkTransform()
		transform.SetMatrix(matrix)
		# pos = self.representations[0].GetWorldPosition()
		# transform.Translate(-pos[0], -pos[1], -pos[2])
		# transform.Translate(-self.pos[0], -self.pos[1], -self.pos[2])
		return transform
