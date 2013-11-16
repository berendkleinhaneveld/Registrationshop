"""
RenderSlicerParamWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QCheckBox
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

		self.slicesLabel = QLabel("Show slices for directions:")
		self.sliceLabelTexts = ["x:", "y:", "z:"]
		self.sliceLabels = [QLabel(text) for text in self.sliceLabelTexts]
		self.sliceCheckBoxes = [QCheckBox() for i in range(3)]
		for index in range(3):
			self.sliceCheckBoxes[index].clicked.connect(self.checkBoxChanged)
			self.sliceLabels[index].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
			self.sliceCheckBoxes[index].setEnabled(True)

		# Create a nice layout for the labels
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 3)
		layout.addWidget(self.slicesLabel, 0, 0, 1, -1)
		for index in range(3):
			layout.addWidget(self.sliceLabels[index], index+1, 0)
			layout.addWidget(self.sliceCheckBoxes[index], index+1, 1)

		# Create option to show clipping box
		self.clippingCheckBox = QCheckBox()
		self.clippingCheckBox.clicked.connect(self.clippingCheckBoxChanged)
		self.clippingLabel = QLabel("Clipping box:")
		self.clippingLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

		layout.addWidget(self.clippingLabel, 5, 0)
		layout.addWidget(self.clippingCheckBox, 5, 1)
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

	@Slot(bool)
	def showsClippingBox(self, show):
		self.clippingCheckBox.setChecked(show)
