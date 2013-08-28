"""
MultiRenderParamWidget

:Authors:
	Berend Klein Haneveld
"""

import sys
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QScrollArea
from PySide.QtGui import QFrame
from PySide.QtGui import QComboBox
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from PySide.QtCore import SIGNAL


class MultiRenderParamWidget(QWidget):
	"""
	MultiRenderParamWidget is a widget that shows parameter controls
	for the multi-volume render widget.
	"""
	def __init__(self, multiRenderController, parent=None):
		super(MultiRenderParamWidget, self).__init__(parent=parent)

		self.multiRenderController = multiRenderController
		self.multiRenderController.visualizationChanged.connect(self.visualizationLoaded)

		self.paramWidget = None

		self.visTypeComboBox = QComboBox()
		for visualization in self.multiRenderController.visualizationTypes:
			self.visTypeComboBox.addItem(visualization)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Visualization type"), 0, 0)
		layout.addWidget(self.visTypeComboBox, 0, 1)
		self.setLayout(layout)

		self.scrollArea = QScrollArea()
		self.scrollArea.setFrameShape(QFrame.NoFrame)
		self.scrollArea.setAutoFillBackground(False)
		self.scrollArea.setAttribute(Qt.WA_TranslucentBackground)
		self.scrollArea.setWidgetResizable(True)

		self.visTypeComboBox.currentIndexChanged.connect(self.visTypeComboBoxChanged)

	def UpdateWidgetFromRenderWidget(self):
		"""
		Update the parameter widget with a widget from the render widget.
		"""
		# Add the scroll area for the parameter widget if it is not there yet
		layout = self.layout()
		if layout.indexOf(self.scrollArea) == -1:
			layout.addWidget(self.scrollArea, 1, 0, 1, 2)
			self.setLayout(layout)

		# Clear the previous parameter widget
		if self.paramWidget is not None:
			self.paramWidget.setParent(None)
			if self.multiRenderController.visualization is not None:
				self.multiRenderController.visualization.disconnect(SIGNAL("updatedTransferFunctions"), self.transferFunctionChanged)

		# Get a new parameter widget from the render widget
		self.paramWidget = self.multiRenderController.getParameterWidget()
		if sys.platform.startswith("darwin"):
			# default background of tabs on OSX is 237, 237, 237
			self.paramWidget.setStyleSheet("background: rgb(229, 229, 229)")
		self.scrollArea.setWidget(self.paramWidget)

		if self.multiRenderController.visualization is not None:
			self.multiRenderController.visualization.updatedTransferFunctions.connect(self.transferFunctionChanged)

		self.visTypeComboBox.setCurrentIndex(self.visTypeComboBox.findText(self.multiRenderController.visualizationType))
		
	@Slot(int)
	def visTypeComboBoxChanged(self, index):
		"""
		Slot that changes the render type. Also updates parameters and makes
		sure that the renderWidget renders with the new visualizationType.
		:type index: any
		"""
		self.multiRenderController.setVisualizationType(self.visTypeComboBox.currentText())
		self.UpdateWidgetFromRenderWidget()
		self.multiRenderController.updateVisualization()

	def visualizationLoaded(self, visualization):
		self.UpdateWidgetFromRenderWidget()

	@Slot()
	def transferFunctionChanged(self):
		"""
		Slot that can be used when a transfer function has changed so that
		the render will be updated afterwards.
		Should be called on valueChanged by the widgets from the parameter widget.
		"""
		self.multiRenderController.updateVisualization()
