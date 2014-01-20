"""
MultiRenderPropWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QTabWidget
from PySide.QtCore import Slot
from ui.parameters import RenderParameterWidget
from ui.parameters import RenderSlicerParamWidget
from ui.parameters import TransformationHistoryWidget
from ui.parameters import TransformationParameterWidget


class MultiRenderPropWidget(QWidget):
	"""
	MultiRenderPropWidget is a widget that is displayed under the multi render
	widget. It contains tabs with some controls for interaction and
	visualization of the combined / multi-volume render widget.
	"""
	def __init__(self, multiRenderController, parent=None):
		super(MultiRenderPropWidget, self).__init__(parent=parent)

		# Two tabs: Visualization and Data info
		self.mixParamWidget = RenderParameterWidget(multiRenderController)
		self.transformParamWidget = TransformationParameterWidget()
		self.registrationHistoryWidget = TransformationHistoryWidget()
		self.slicesTabWidget = RenderSlicerParamWidget(multiRenderController)

		# Create the tab widget
		self.tabWidget = QTabWidget()
		self.tabWidget.addTab(self.mixParamWidget, "Visualization")
		self.tabWidget.addTab(self.registrationHistoryWidget, "History")
		self.tabWidget.addTab(self.slicesTabWidget, "Slices")

		self.currentTabIndex = 0
		self.tabWidget.currentChanged.connect(self.tabIndexChanged)

		layout = QVBoxLayout()
		self.setLayout(layout)
		layout.addWidget(self.tabWidget)

		self.registrationHistoryWidget.setMultiRenderWidget(multiRenderController.multiRenderWidget)

	def setTransformTool(self, transformTool):
		if self.tabWidget.indexOf(self.transformParamWidget) < 0:
			self.tabWidget.addTab(self.transformParamWidget, "Transformation")
		
		self.tabWidget.setCurrentWidget(self.transformParamWidget)
		self.transformParamWidget.setTransformationTool(transformTool)

	def transformToolFinished(self):
		index = self.tabWidget.indexOf(self.transformParamWidget)
		if index >= 0:
			# Restore the last tab index that wasn't the transform tab
			self.tabWidget.setCurrentIndex(self.currentTabIndex)
			self.tabWidget.removeTab(index)

	@Slot(int)
	def tabIndexChanged(self, index):
		transformIndex = self.tabWidget.indexOf(self.transformParamWidget)
		if index != transformIndex:
			self.currentTabIndex = index
