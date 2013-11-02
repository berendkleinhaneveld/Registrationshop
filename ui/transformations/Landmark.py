
from vtk import vtkProp3DFollower
from vtk import vtkRegularPolygonSource
from vtk import vtkSphereSource
from vtk import vtkPolyDataMapper
from vtk import vtkActor
from vtk import vtkTransform


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

		self.colorActive = [1.0, 0.5, 0.7]
		self.colorInactive = [1.0, 1.0, 0.6]

		self._position = [0.0, 0.0, 0.0]  # coordinates in volume
		self.transform = vtkTransform()
		self.active = True
		self.id = index

		self.landmark = CreateSphere()

		self.landmarkIndicator = CreateCircle()
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
	
	def update(self):
		# Update color for landmark and landmarkIndicator
		if self.active:
			color = self.colorActive
			opacity = 0.7
		else:
			color = self.colorInactive
			opacity = 0.4
		self.landmark.GetProperty().SetColor(color[0], color[1], color[2])
		self.landmarkIndicator.GetProperty().SetColor(color[0], color[1], color[2])
		self.landmarkIndicator.GetProperty().SetOpacity(opacity)

		# Update position of landmark and landmarkFollower with the latest transform
		location = list(self.transform.TransformPoint(self._position[0], self._position[1], self._position[2]))
		self.landmark.SetPosition(location[0], location[1], location[2])
		self.landmarkFollower.SetPosition(location[0], location[1], location[2])


def CreateSphere():
	sphereSource = vtkSphereSource()
	sphereSource.SetRadius(20)
	sphereSource.SetThetaResolution(6)
	sphereSource.SetPhiResolution(6)

	sphereMapper = vtkPolyDataMapper()
	sphereMapper.SetInputConnection(sphereSource.GetOutputPort())

	sphere = vtkActor()
	sphere.PickableOff()
	sphere.SetMapper(sphereMapper)
	sphere.GetProperty().SetColor(1.0, 1.0, 0.6)

	return sphere


def CreateCircle():
	circleSource = vtkRegularPolygonSource()
	circleSource.SetNumberOfSides(30)
	circleSource.SetRadius(28)
	circleSource.SetGeneratePolygon(False)

	circleMapper = vtkPolyDataMapper()
	circleMapper.SetInputConnection(circleSource.GetOutputPort())

	circle = vtkActor()
	circle.PickableOff()
	circle.SetMapper(circleMapper)
	circle.GetProperty().SetColor(1.0, 0.5, 0.5)

	return circle
