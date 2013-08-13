"""
RenderParameterWidget

:Authors:
	Berend Klein Haneveld
"""

import sys
from PySide.QtGui import QLabel
from PySide.QtGui import QComboBox
from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QScrollArea
from PySide.QtGui import QFrame
from PySide.QtCore import Slot
from PySide.QtCore import SIGNAL
from PySide.QtCore import Qt

class RenderParameterWidget(QWidget):
	"""
	RenderParameterWidget is a widget that is shown in the render property 
	widget. It holds a combo box with which different visualizations can be 
	chosen. Beneath the combo box it displays a widget in a scroll view that 
	contains widgets with which parameters of the visualization can be adjusted.
	"""

	def __init__(self, renderController, parent=None):
		super(RenderParameterWidget, self).__init__(parent=parent)

		self.renderController = renderController
		self.renderController.dataChanged.connect(self.dataLoaded)
		self.renderController.volumePropertyChanged.connect(self.volumePropertyLoaded)

		self.visTypeLabel = QLabel("Visualization type")
		self.visTypeLabel.setMaximumHeight(20)

		self.visTypeCompoBox = QComboBox()
		for renderType in self.renderController.renderTypes:
			self.visTypeCompoBox.addItem(renderType)

		self.paramWidget = None

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.visTypeLabel)
		layout.addWidget(self.visTypeCompoBox)
		self.setLayout(layout)

		self.scrollArea = QScrollArea()
		self.scrollArea.setFrameShape(QFrame.NoFrame)
		self.scrollArea.setAutoFillBackground(False)
		self.scrollArea.setAttribute(Qt.WA_TranslucentBackground)
		self.scrollArea.setWidgetResizable(True)

		self.visTypeCompoBox.currentIndexChanged.connect(self.renderTypeComboBoxChanged)

	def UpdateWidgetFromRenderWidget(self):
		"""
		Update the parameter widget with a widget from the render widget.
		"""
		# Add the scroll area for the parameter widget if it is not there yet
		layout = self.layout()
		if layout.indexOf(self.scrollArea) == -1:
			layout.addWidget(self.scrollArea)
			self.setLayout(layout)

		# Clear the previous parameter widget
		if self.paramWidget is not None:
			self.paramWidget.setParent(None)
			if self.renderController.volumeProperty is not None:
				self.renderController.volumeProperty.disconnect(SIGNAL("updatedTransferFunction"), self.transferFunctionChanged)

		# Get a new parameter widget from the render widget
		self.paramWidget = self.renderController.getParameterWidget()
		if sys.platform.startswith("darwin"):
			# default background of tabs on OSX is 237, 237, 237
			self.paramWidget.setStyleSheet("background: rgb(229, 229, 229)")
		self.scrollArea.setWidget(self.paramWidget)

		if self.renderController.volumeProperty is not None:
			self.renderController.volumeProperty.updatedTransferFunction.connect(self.transferFunctionChanged)

		self.visTypeCompoBox.setCurrentIndex(self.visTypeCompoBox.findText(self.renderController.renderType))

	@Slot(int)
	def renderTypeComboBoxChanged(self, index):
		"""
		Slot that changes the render type. Also updates parameters and makes
		sure that the renderWidget renders with the new renderType.
		:type index: any
		"""
		self.renderController.setRenderType(self.visTypeCompoBox.currentText())
		self.UpdateWidgetFromRenderWidget()
		self.renderController.updateVolumeProperty()

	@Slot()
	def dataLoaded(self):
		"""
		When data has been changed, the parameters have to be updated. This is because
		some of the parameters are dependent on properties of the data.
		"""
		pass
		# Get the correct widget from the RenderWidget
		# self.UpdateWidgetFromRenderWidget()

	def volumePropertyLoaded(self, volumeProperty):
		self.UpdateWidgetFromRenderWidget()

	@Slot()
	def transferFunctionChanged(self):
		"""
		Slot that can be used when a transfer function has changed so that
		the render will be updated afterwards.
		Should be called on valueChanged by the widgets from the parameter widget.
		"""
		self.renderController.updateVolumeProperty()
