"""
RenderPropWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QPushButton
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QTabWidget
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from ui.parameters import RenderParameterWidget
from ui.parameters import RenderInfoWidget
from ui.parameters import RenderSlicerParamWidget


class RenderPropWidget(QWidget):
	"""
	RenderPropWidget is a widget that is displayed under the render widgets. It
	contains a tabwidget in which information of the data can be displayed and
	in which visualization parameters can be shown. One of the tabs is a
	RenderParameterWidget object.
	"""
	def __init__(self, renderController, parent=None):
		super(RenderPropWidget, self).__init__(parent=parent)

		# Three tabs: Visualization, data info and slices
		self.visParamTabWidget = RenderParameterWidget(renderController)
		self.dataInfoTabWidget = RenderInfoWidget()
		self.slicesTabWidget = RenderSlicerParamWidget(renderController)

		# Create the load dataset widget
		self.loadDataWidget = QWidget()
		self.loadDataButton = QPushButton()
		self.loadDataButton.setText("Load a dataset")

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.loadDataButton)
		self.loadDataWidget.setLayout(layout)

		# Create the tab widget
		self.tabWidget = QTabWidget()
		self.tabWidget.addTab(self.visParamTabWidget, "Visualization")
		self.tabWidget.addTab(self.dataInfoTabWidget, "Data info")
		self.tabWidget.addTab(self.slicesTabWidget, "Slices")

		layout = QVBoxLayout()
		layout.addWidget(self.loadDataWidget)
		self.setLayout(layout)

	def setFileChangedSignal(self, signal):
		"""
		:param signal: Signal that is connected to some file-loading slots.
		:type signal: SIGNAL
		"""
		self.signal = signal
		self.signal.connect(self.setFile)
		self.signal.connect(self.dataInfoTabWidget.setFile)

	def setLoadDataSlot(self, slot):
		"""
		The button is connected to the given slot. The slot action should load
		a dataset from disk.

		:type slot: Slot
		"""
		self.loadDataButton.clicked.connect(slot)

	@Slot(basestring)
	def setFile(self, fileName):
		"""
		When a file is loaded, the 'load data' button is removed from the widget
		and the actual tabs with parameters are put on screen.
		"""
		layout = self.layout()
		if fileName is None:
			if layout.indexOf(self.tabWidget) != -1:
				# Remove the parameter widgets
				layout.removeWidget(self.tabWidget)
				self.tabWidget.setParent(None)
				# Show the load data button
				layout.addWidget(self.loadDataWidget)
				self.setLayout(layout)
		else:
			if layout.indexOf(self.loadDataWidget) != -1:
				# Remove the load data button
				layout.removeWidget(self.loadDataWidget)
				self.loadDataWidget.setParent(None)
				# Add the parameter widgets
				layout.addWidget(self.tabWidget)
				self.setLayout(layout)
