"""
RenderSlicerParamWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QCheckBox
from PySide.QtGui import QGroupBox
from PySide.QtGui import QPushButton
from PySide.QtCore import Qt
from PySide.QtCore import Slot


class RenderSlicerParamWidget(QWidget):
	"""
	RenderSlicerParamWidget shows parameters with which slicers can be
	manipulated.
	"""
	def __init__(self, renderController, parent=None):
		super(RenderSlicerParamWidget, self).__init__(parent=parent)

		self.renderController = renderController
		self.renderController.slicesChanged.connect(self.setSlices)
		self.renderController.clippingBoxChanged.connect(self.showsClippingBox)
		self.renderController.clippingPlanesChanged.connect(self.showsClippingPlanes)

		self.sliceLabelTexts = ["Axial:", "Coronal:", "Sagittal:"]
		self.sliceLabels = [QLabel(text) for text in self.sliceLabelTexts]
		self.sliceCheckBoxes = [QCheckBox() for i in range(3)]
		for index in range(3):
			self.sliceCheckBoxes[index].clicked.connect(self.checkBoxChanged)
			self.sliceLabels[index].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
			self.sliceCheckBoxes[index].setEnabled(True)

		slicesLayout = QGridLayout()
		slicesLayout.setAlignment(Qt.AlignTop)
		for index in range(3):
			slicesLayout.addWidget(self.sliceLabels[index], index+1, 0)
			slicesLayout.addWidget(self.sliceCheckBoxes[index], index+1, 1)

		self.slicesGroupBox = QGroupBox()
		self.slicesGroupBox.setTitle("Visible slices")
		self.slicesGroupBox.setLayout(slicesLayout)

		# Create option to show clipping box
		self.clippingCheckBox = QCheckBox()
		self.clippingCheckBox.setChecked(self.renderController.clippingBox)
		self.clippingCheckBox.clicked.connect(self.clippingCheckBoxChanged)
		self.clippingPlanesCheckBox = QCheckBox()
		self.clippingPlanesCheckBox.setChecked(self.renderController.clippingPlanes)
		self.clippingPlanesCheckBox.clicked.connect(self.clippingPlanesCheckBoxChanged)
		self.resetButton = QPushButton("Reset")
		self.resetButton.clicked.connect(self.resetClippingBox)

		clippingLabel = QLabel("Clipping box:")
		clippingLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		clippingPlanesLabel = QLabel("Clipping planes:")
		clippingPlanesLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

		clipLayout = QGridLayout()
		clipLayout.addWidget(clippingLabel, 0, 0)
		clipLayout.addWidget(self.clippingCheckBox, 0, 1)
		clipLayout.addWidget(clippingPlanesLabel, 1, 0)
		clipLayout.addWidget(self.clippingPlanesCheckBox, 1, 1)
		clipLayout.addWidget(self.resetButton, 2, 0)

		self.clippingGroupBox = QGroupBox()
		self.clippingGroupBox.setTitle("Clipping box")
		self.clippingGroupBox.setLayout(clipLayout)

		# Create a nice layout for the labels
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.slicesGroupBox, 0, 0)
		layout.addWidget(self.clippingGroupBox, 0, 1)
		self.setLayout(layout)

	@Slot()
	def checkBoxChanged(self):
		"""
		Callback function for the check boxes.
		"""
		for index in range(3):
			showCheckBox = self.sliceCheckBoxes[index].checkState() == Qt.Checked
			self.renderController.setSliceVisibility(index, showCheckBox)

	@Slot(object)
	def setSlices(self, slices):
		for index in range(len(slices)):
			checkBox = self.sliceCheckBoxes[index]
			checkBox.setChecked(slices[index])

	@Slot()
	def clippingCheckBoxChanged(self):
		"""
		Callback function for the clipping check box.
		"""
		self.renderController.showClippingBox(self.clippingCheckBox.checkState() == Qt.Checked)

	@Slot()
	def clippingPlanesCheckBoxChanged(self):
		"""
		Callback function for the clipping check box.
		"""
		self.renderController.showClippingPlanes(self.clippingPlanesCheckBox.checkState() == Qt.Checked)

	@Slot()
	def resetClippingBox(self):
		self.renderController.resetClippingBox()

	@Slot(bool)
	def showsClippingBox(self, show):
		self.clippingCheckBox.setChecked(show)

	@Slot(bool)
	def showsClippingPlanes(self, show):
		self.clippingPlanesCheckBox.setChecked(show)
