"""
ScaleWidget

:Authors:
	Berend Klein Haneveld
"""
from TransformWidget import TransformWidget
from core.vtkDrawing import CreateBoxOnStick
from vtk import vtkPolygonalHandleRepresentation3D
from vtk import vtkHandleWidget


class ScaleWidget(TransformWidget):
	def __init__(self):
		super(ScaleWidget, self).__init__()

	def _internalInit(self):
		for i in range(3):
			direction = [0, 0, 0]
			direction[i] = 1.0
			arrow, arrowPoly = CreateBoxOnStick([0, 0, 0], direction)

			rep = vtkPolygonalHandleRepresentation3D()
			rep.GetProperty().SetColor(direction)
			rep.SetWorldPosition(self.pos)
			rep.SetConstrainedAxis(i)
			rep.SetInteractionMode(1)
			rep.SetHandle(arrowPoly)
			self.representations.append(rep)

			handleWidget = vtkHandleWidget()
			handleWidget.SetInteractor(self.rwi)
			handleWidget.SetDefaultRenderer(self.renderer)
			handleWidget.SetEnableAxisConstraint(True)
			handleWidget.SetRepresentation(rep)
			handleWidget.AddObserver("InteractionEvent", self.interactionCallback)
			self.handles.append(handleWidget)

	def getScale(self):
		return [1, 1, 1]

	def interactionCallback(self, interactor, ev):
		pass
