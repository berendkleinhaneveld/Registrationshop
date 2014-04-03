"""
TranslateWidget

:Authors:
	Berend Klein Haneveld
"""
from TransformWidget import TransformWidget
from core.vtkDrawing import CreateArrow
from vtk import vtkPolygonalHandleRepresentation3D
from vtk import vtkHandleWidget


class TranslateWidget(TransformWidget):
	def __init__(self):
		super(TranslateWidget, self).__init__()

	def _internalInit(self):
		for i in range(3):
			direction = [0, 0, 0]
			direction[i] = 1.0
			arrow, arrowPoly = CreateArrow([0, 0, 0], direction)

			rep = vtkPolygonalHandleRepresentation3D()
			rep.GetProperty().SetColor(direction)
			rep.SetWorldPosition(self.pos)
			rep.SetConstrainedAxis(i)
			rep.SetInteractionMode(0)
			rep.SetHandle(arrowPoly)
			self.representations.append(rep)

			handleWidget = vtkHandleWidget()
			handleWidget.SetInteractor(self.rwi)
			handleWidget.SetDefaultRenderer(self.renderer)
			handleWidget.SetEnableAxisConstraint(True)
			handleWidget.SetRepresentation(rep)
			handleWidget.AddObserver("InteractionEvent", self.interactionCallback)
			self.handles.append(handleWidget)

	def getTranslation(self):
		pos = self.representations[0].GetWorldPosition()
		return map(lambda x, y: x - y, pos, self.pos)

	def interactionCallback(self, interactor, ev):
		pos = interactor.GetRepresentation().GetWorldPosition()
		for handle in self.handles:
			if handle is interactor:
				continue
			handle.GetRepresentation().SetWorldPosition(pos)

		self.updatedTransform.emit()
