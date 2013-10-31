"""
LandmarkTransformationTool (TransformationTool)

:Authors:
	Berend Klein Haneveld
"""
from TransformationTool import TransformationTool
from Landmark import Landmark
from core.decorators import overrides
from ui.widgets.PointsWidget import PointsWidget
from ui.transformations import TwoStepPicker as Picker
from ui.transformations import Transformation
from ui.widgets.StatusWidget import StatusWidget
from vtk import vtkPoints
from vtk import vtkLandmarkTransform
from vtk import vtkTransform
from vtk import vtkMatrix4x4
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
		self.movingPoints = []  # Locations

		self.landmarks = []  # All the landmark objects
		self.originalTransform = None
		self.originalScalingTransform = None

		self.activeIndex = 0
		self.landmarkTransformType = 0  # Rigid, Similarity or Affine

	@overrides(TransformationTool)
	def getParameterWidget(self):
		pointsWidget = PointsWidget()

		self.landmarkComboBox = QComboBox()
		self.landmarkComboBox.addItem("Rigid body")
		self.landmarkComboBox.addItem("Similarity")
		self.landmarkComboBox.addItem("Affine")

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Transform type"), 0, 0)
		layout.addWidget(self.landmarkComboBox, 0, 1)
		layout.addWidget(pointsWidget, 1, 0, 1, 2)
		
		self.updatedLandmarks.connect(pointsWidget.setPoints)
		self.landmarkComboBox.currentIndexChanged.connect(self.landmarkTypeChanged)
		pointsWidget.activeLandmarkChanged.connect(self.setActiveLandmark)

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

		# Save the original complete transform
		self.originalTransform = self.multiWidget.transformations.completeTransform()
		self.originalScalingTransform = self.multiWidget.transformations.scalingTransform()
		transform = Transformation(vtkTransform(), Transformation.TypeLandmark)
		self.multiWidget.transformations.append(transform)

		statusWidget = StatusWidget.Instance()
		statusWidget.setText("Place landmarks in both volumes to create a landmark transform. Hold your " +
			"mouse over a volume and press 'A'. Turn the volume, move your mouse and press 'A' again to set a " +
			"landmark.")

	def setLandmarkWidgets(self, fixed, moving):
		self.fixedLandmarkWidget = fixed
		self.movingLandmarkWidget = moving

		self.fixedPicker.setPropertiesWidget(self.fixedLandmarkWidget)
		self.movingPicker.setPropertiesWidget(self.movingLandmarkWidget)

	@overrides(TransformationTool)
	def cancelTransform(self):
		del self.multiWidget.transformations[-1]

	@overrides(TransformationTool)
	def applyTransform(self):
		pass

	@overrides(TransformationTool)
	def cleanUp(self):
		self.fixedPicker.cleanUp()
		self.movingPicker.cleanUp()

		for landmark in self.landmarks:
			landmark.cleanUp()

		self.fixedPoints = []
		self.movingPoints = []

		self.fixedPicker = Picker()
		self.movingPicker = Picker()

		self.fixedWidget.render()
		self.movingWidget.render()
		self.multiWidget.render()

		self.fixedLandmarkWidget.setVisible(False)
		self.movingLandmarkWidget.setVisible(False)

		self.toolFinished.emit()

	@Slot(int)
	def setActiveLandmark(self, index):
		self.activeIndex = index
		self._update()
		self.fixedWidget.render()
		self.movingWidget.render()
		self.multiWidget.render()

	@Slot(int)
	def landmarkTypeChanged(self, value):
		"""
		Called when the transformation type is changed
		from the combo box. Rigid, Similarity or Affine.
		"""
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
			# Transform the point from the moving landmark with the original transform
			transPoint = self.originalTransform.TransformPoint(movingPoint)
			print str(movingPoint) + " -> " + str(transPoint)
			fixedPoints.SetPoint(index, fixedPoint)
			movingPoints.SetPoint(index, transPoint)

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

		matrix = vtkMatrix4x4()
		matrix.DeepCopy(landmarkTransform.GetMatrix())

		transform = vtkTransform()
		transform.SetMatrix(matrix)
		transform.Inverse()
		
		self.multiWidget.transformations[-1] = Transformation(transform, Transformation.TypeLandmark)
		self._updateLandmarkTransforms()
		self.movingWidget.render()

	def _updateLandmarkTransforms(self):
		# Update the transforms
		for landmark in self.landmarks:
			if landmark.flag == "moving" and landmark.renderer == self.movingWidget.renderer:
				landmark.transform = self.multiWidget.transformations.scalingTransform()
				landmark.update()
			elif landmark.flag == "moving" and landmark.renderer == self.multiWidget.renderer:
				landmark.transform = self.multiWidget.transformations.completeTransform()
				landmark.update()

	def pickedFixedLocation(self, location):
		"""
		Place spheres in fixed widget and in multi-widget.
		The input location should be in local data coordinates.
		"""
		if self.activeIndex >= len(self.fixedPoints):
			# Add the location to the fixed points
			self.fixedPoints.append(location)
			# Create landmark for fixed widget
			landmark = Landmark(index=self.activeIndex,
				renderer=self.fixedWidget.renderer,
				overlay=self.fixedWidget.rendererOverlay,
				flag="fixed")
			landmark.id = self.activeIndex
			landmark.setPosition(location)

			# Create landmark for multi widget
			landmarkMulti = Landmark(index=self.activeIndex,
				renderer=self.multiWidget.renderer,
				overlay=self.multiWidget.rendererOverlay,
				flag="fixed")
			landmarkMulti.id = self.activeIndex
			landmarkMulti.setPosition(location)

			self.landmarks.append(landmark)
			self.landmarks.append(landmarkMulti)
		else:
			landmarks = [x for x in self.landmarks if (x.id == self.activeIndex and x.flag == "fixed")]
			for landmark in landmarks:
				landmark.setPosition(location)
			self.fixedPoints[self.activeIndex] = location

		self.updateTransform()
		self.updatedLandmarks.emit(self.fixedPoints, self.movingPoints)
		self._update()
		self.multiWidget.render()

	def pickedMovingLocation(self, location):
		"""
		Place spheres in moving widget and in multi-widget
		Location is in local coordinates.
		"""
		# Create a new landmark
		if self.activeIndex >= len(self.movingPoints):
			# Add the location to the moving points
			self.movingPoints.append(location)
			# Create landmark for moving widget
			landmark = Landmark(index=self.activeIndex,
				renderer=self.movingWidget.renderer,
				overlay=self.movingWidget.rendererOverlay,
				flag="moving")
			landmark.setPosition(location)

			# Create landmark for multi widget
			landmarkMulti = Landmark(index=self.activeIndex,
				renderer=self.multiWidget.renderer,
				overlay=self.multiWidget.rendererOverlay,
				flag="moving")
			landmarkMulti.id = self.activeIndex
			landmarkMulti.setPosition(location)
			
			self.landmarks.append(landmark)
			self.landmarks.append(landmarkMulti)
		else:
			# Just update the location of the current active landmark
			landmarks = [x for x in self.landmarks if (x.id == self.activeIndex and x.flag == "moving")]
			for landmark in landmarks:
				landmark.setPosition(location)
			self.movingPoints[self.activeIndex] = location

		self.updateTransform()
		self.updatedLandmarks.emit(self.fixedPoints, self.movingPoints)
		self._update()
		self.multiWidget.render()

	def _update(self):
		for landmark in self.landmarks:
			landmark.active = landmark.id == self.activeIndex
			landmark.update()
		self._updateLandmarkTransforms()
