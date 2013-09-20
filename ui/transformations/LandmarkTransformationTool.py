"""
LandmarkTransformationTool (TransformationTool)

:Authors:
	Berend Klein Haneveld
"""
from TransformationTool import TransformationTool
from core.decorators import overrides
from ui.widgets import PointsWidget
from ui.transformations import Picker
from vtk import vtkSphereSource
from vtk import vtkPolyDataMapper
from vtk import vtkActor
from vtk import vtkPoints
from vtk import vtkLandmarkTransform
from vtk import vtkTransform
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QComboBox
from PySide.QtGui import QLabel
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from PySide.QtCore import Qt


class LandmarkTransformationTool(TransformationTool):
	"""
	LandmarkTransformationTool
	"""
	updatedLandmarks = Signal(list, list)

	def __init__(self):
		super(LandmarkTransformationTool, self).__init__()

		self.fixedPicker = Picker()
		self.movingPicker = Picker()

		self.fixedPoints = []  # Locations
		self.fixedLandmarks = []  # Spheres, vtkActors
		self.fixedMultiLandmarks = []  # Spheres, vtkActors
		self.movingPoints = []
		self.movingLandmarks = []  # Spheres, vtkActors
		self.movingMultiLandmarks = []  # Spheres, vtkActors

		self.activeIndex = 0
		self.landmarkTransformType = 0  # Rigid

	@overrides(TransformationTool)
	def getParameterWidget(self):
		pointsWidget = PointsWidget()
		self.updatedLandmarks.connect(pointsWidget.setPoints)
		pointsWidget.activeLandmarkChanged.connect(self.setActiveLandmark)

		self.landmarkComboBox = QComboBox()
		self.landmarkComboBox.addItem("Rigid body")
		self.landmarkComboBox.addItem("Similarity")
		self.landmarkComboBox.addItem("Affine")
		self.landmarkComboBox.currentIndexChanged.connect(self.landmarkTypeChanged)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Transform type"), 0, 0)
		layout.addWidget(self.landmarkComboBox, 0, 1)
		layout.addWidget(pointsWidget, 1, 0, 1, 2)
		widget = QWidget()
		widget.setLayout(layout)
		return widget

	@overrides(TransformationTool)
	def setRenderWidgets(self, fixed=None, moving=None, multi=None):
		self.fixedWidget = fixed
		self.movingWidget = moving
		self.multiWidget = multi

		self.fixedPicker.setWidget(self.fixedWidget)
		self.movingPicker.setWidget(self.movingWidget)

		self.fixedPicker.pickedLocation.connect(self.pickedFixedLocation)
		self.movingPicker.pickedLocation.connect(self.pickedMovingLocation)

		# Reset any previous 'free' transforms
		self.multiWidget.resetAllTransforms()

	@overrides(TransformationTool)
	def applyTransform(self):
		self.multiWidget.applyUserTransform()
		self.multiWidget.render()

	@overrides(TransformationTool)
	def cleanUp(self):
		self.fixedPicker.cleanUp()
		self.movingPicker.cleanUp()

		for prop in self.fixedLandmarks:
			self.fixedWidget.renderer.RemoveViewProp(prop)
		for prop in self.movingLandmarks:
			self.movingWidget.renderer.RemoveViewProp(prop)
		for prop in self.fixedMultiLandmarks:
			self.multiWidget.renderer.RemoveViewProp(prop)
		for prop in self.movingMultiLandmarks:
			self.multiWidget.renderer.RemoveViewProp(prop)

		self.fixedPoints = []
		self.fixedLandmarks = []
		self.fixedMultiLandmarks = []
		self.movingPoints = []
		self.movingLandmarks = []
		self.movingMultiLandmarks = []

		self.fixedPicker = Picker()
		self.movingPicker = Picker()
		
		self.multiWidget.resetUserTransform()

		self.fixedWidget.render()
		self.movingWidget.render()
		self.multiWidget.render()

	@Slot(int)
	def setActiveLandmark(self, index):
		self.activeIndex = index
		self._update()
		self.fixedWidget.render()
		self.movingWidget.render()
		self.multiWidget.render()

	@Slot(int)
	def landmarkTypeChanged(self, value):
		self.landmarkTransformType = value
		self.updateTransform()
		self.multiWidget.render()

	def updateTransform(self):
		"""
		Update the landmark transform
		"""
		if len(self.fixedPoints) == 0 or len(self.movingPoints) == 0:
			return

		fixedPoints = vtkPoints()
		movingPoints = vtkPoints()
		numberOfSets = min(len(self.fixedPoints), len(self.movingPoints))
		fixedPoints.SetNumberOfPoints(numberOfSets)
		movingPoints.SetNumberOfPoints(numberOfSets)

		for index in range(numberOfSets):
			fixedPoint = self.fixedPoints[index]
			movingPoint = self.movingPoints[index]
			fixedPoints.SetPoint(index, fixedPoint)
			movingPoints.SetPoint(index, movingPoint)

		landmarkTransform = vtkLandmarkTransform()
		if self.landmarkTransformType == 0:
			landmarkTransform.SetModeToRigidBody()
		elif self.landmarkTransformType == 1:
			landmarkTransform.SetModeToSimilarity()
		elif self.landmarkTransformType == 2:
			landmarkTransform.SetModeToAffine()
		landmarkTransform.SetSourceLandmarks(fixedPoints)
		landmarkTransform.SetTargetLandmarks(movingPoints)
		landmarkTransform.Update()

		matrix = landmarkTransform.GetMatrix()

		transform = vtkTransform()
		transform.Identity()
		transform.SetMatrix(matrix)
		transform.Update()
		transform.Inverse()
		
		self.multiWidget.setUserTransform(transform)
		# TODO: make sure that the multi-render widget updates
		# as soon as possible. Just calling render() does not seem
		# to work, alas...
		# self.multiWidget.render()

	def pickedFixedLocation(self, location):
		"""
		Place spheres in fixed widget and in multi-widget
		"""
		if self.activeIndex >= len(self.fixedPoints):
			sphereSingle = CreateSphere()
			sphereSingle.SetPosition(location[0], location[1], location[2])
			self.fixedPoints.append(location)
			self.fixedLandmarks.append(sphereSingle)
			self.fixedWidget.renderer.AddViewProp(sphereSingle)
		else:
			sphereSingle = self.fixedLandmarks[self.activeIndex]
			sphereSingle.SetPosition(location[0], location[1], location[2])
			self.fixedPoints[self.activeIndex] = location

		self.updateTransform()
		self.updatedLandmarks.emit(self.fixedPoints, self.movingPoints)
		self._update()
		self.multiWidget.render()

	def pickedMovingLocation(self, location):
		"""
		Place spheres in moving widget and in multi-widget
		"""
		if self.activeIndex >= len(self.movingPoints):
			sphereSingle = CreateSphere()
			sphereSingle.SetPosition(location[0], location[1], location[2])
			self.movingPoints.append(location)
			self.movingLandmarks.append(sphereSingle)
			self.movingWidget.renderer.AddViewProp(sphereSingle)
		else:
			sphereSingle = self.movingLandmarks[self.activeIndex]
			sphereSingle.SetPosition(location[0], location[1], location[2])
			self.movingPoints[self.activeIndex] = location

		self.updateTransform()
		self.updatedLandmarks.emit(self.fixedPoints, self.movingPoints)
		self._update()
		self.multiWidget.render()

	def _update(self):
		# Give the active landmarks nice colors
		self._updateSpheres(self.fixedLandmarks, self.activeIndex)
		self._updateSpheres(self.movingLandmarks, self.activeIndex)
		self._updateSpheres(self.fixedMultiLandmarks, self.activeIndex)
		self._updateSpheres(self.movingMultiLandmarks, self.activeIndex)

	def _updateSpheres(self, spheres, activeIndex):
		for index in range(len(spheres)):
			sphere = spheres[index]
			if index == activeIndex:
				sphere.GetProperty().SetColor(1.0, 0.6, 1.0)
			else:
				sphere.GetProperty().SetColor(1.0, 1.0, 0.6)


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
