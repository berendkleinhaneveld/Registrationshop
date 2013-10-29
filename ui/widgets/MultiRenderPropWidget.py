"""
MultiRenderPropWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QTabWidget
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
		self.tabWidget.addTab(self.mixParamWidget, "Mix")
		self.tabWidget.addTab(self.transformParamWidget, "Transformation")
		self.tabWidget.addTab(self.registrationHistoryWidget, "History")
		self.tabWidget.addTab(self.slicesTabWidget, "Slices")

		layout = QVBoxLayout()
		self.setLayout(layout)
		layout.addWidget(self.tabWidget)

		self.registrationHistoryWidget.setMultiRenderWidget(multiRenderController.multiRenderWidget)
