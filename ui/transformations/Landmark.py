"""
Landmark

:Authors:
	Berend Klein Haneveld
"""
from vtk import vtkProp3DFollower
from vtk import vtkTransform
from core.vtkDrawing import CreateSphere
from core.vtkDrawing import ColorActor
from core.vtkDrawing import CreateCircle


class Landmark(object):
	"""
	Landmark is a container for vtkProps for easier
	management of resources.
	"""
	def __init__(self, index, renderer, overlay, flag="Fixed"):
		super(Landmark, self).__init__()

		self.renderer = renderer
		self.overlay = overlay
		self.flag = flag

		self.colorActive = [0.5, 1.0, 0.5]
		self.colorInactive = [0.8, 0.8, 0.8]

		self._position = [0.0, 0.0, 0.0]  # coordinates in volume
		self._scale = 1.0
		self.transform = vtkTransform()
		self.active = True
		self.id = index

		self.landmark = CreateSphere(0.1, [1, 1, 0.6])

		self.landmarkIndicator = CreateCircle(1.2)
		self.landmarkIndicator.GetProperty().SetLineWidth(2)
		self.landmarkIndicator.GetProperty().SetOpacity(0.7)

		self.landmarkFollower = vtkProp3DFollower()
		self.landmarkFollower.SetProp3D(self.landmarkIndicator)
		self.landmarkFollower.SetCamera(self.renderer.GetActiveCamera())

		self.renderer.AddViewProp(self.landmark)
		self.overlay.AddViewProp(self.landmarkFollower)

	def cleanUp(self):
		self.renderer.RemoveViewProp(self.landmark)
		self.overlay.RemoveViewProp(self.landmarkFollower)

	@property
	def position(self):
		return self._position

	@position.setter
	def position(self, position):
		"""
		Position should be in local coordinates.
		"""
		self._position = position
		self.update()

	@property
	def scale(self):
		return self._scale

	@scale.setter
	def scale(self, value):
		self._scale = value
		self.landmark.SetScale(value)
		self.landmarkIndicator.SetScale(value)
	
	def update(self):
		# Update color for landmark and landmarkIndicator
		if self.active:
			color = self.colorActive
			opacity = 0.7
		else:
			color = self.colorInactive
			opacity = 0.4
		ColorActor(self.landmark, color)
		ColorActor(self.landmarkIndicator, color, opacity)

		# Update position of landmark and landmarkFollower with the latest transform
		location = list(self.transform.TransformPoint(self._position[0], self._position[1], self._position[2]))
		self.landmark.SetPosition(location[0], location[1], location[2])
		self.landmarkFollower.SetPosition(location[0], location[1], location[2])
