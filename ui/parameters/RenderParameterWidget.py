"""
RenderParameterWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QLabel
from PySide.QtGui import QComboBox
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QScrollArea
from PySide.QtGui import QFrame
from PySide.QtCore import Slot
from PySide.QtCore import SIGNAL
from PySide.QtCore import Qt
from ui.widgets import Style


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
		self.renderController.visualizationChanged.connect(self.visualizationLoaded)

		self.paramWidget = None

		self.visTypeComboBox = QComboBox()
		for visualizationType in self.renderController.visualizationTypes:
			self.visTypeComboBox.addItem(visualizationType)

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
			if self.renderController.visualization is not None:
				self.renderController.visualization.disconnect(SIGNAL("updatedTransferFunction"), self.transferFunctionChanged)

		# Get a new parameter widget from the render widget
		self.paramWidget = self.renderController.getParameterWidget()
		Style.styleWidgetForTab(self.paramWidget)
		self.scrollArea.setWidget(self.paramWidget)

		if self.renderController.visualization is not None:
			self.renderController.visualization.updatedTransferFunction.connect(self.transferFunctionChanged)

		self.visTypeComboBox.setCurrentIndex(self.visTypeComboBox.findText(self.renderController.visualizationType))

	@Slot(int)
	def visTypeComboBoxChanged(self, index):
		"""
		Slot that changes the render type. Also updates parameters and makes
		sure that the renderWidget renders with the new visualizationType.
		:type index: any
		"""
		self.renderController.setVisualizationType(self.visTypeComboBox.currentText())
		self.UpdateWidgetFromRenderWidget()
		self.renderController.updateVisualization()

	def visualizationLoaded(self, visualization):
		self.UpdateWidgetFromRenderWidget()

	@Slot()
	def transferFunctionChanged(self):
		"""
		Slot that can be used when a transfer function has changed so that
		the render will be updated afterwards.
		Should be called on valueChanged by the widgets from the parameter widget.
		"""
		self.renderController.updateVisualization()
