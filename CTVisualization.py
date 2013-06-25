
"""
LayerVisualization

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtCore import Qt
from PySide.QtGui import QIcon
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QFileDialog
from PySide.QtGui import QSlider
from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QMainWindow
from PySide.QtGui import QAction
from PySide.QtGui import QSizePolicy
from core.AppVars import AppVars
from core.DataReader import DataReader
from RenderWidget import RenderWidget
from RenderWidget import RenderTypeCT
from RenderWidget import RenderTypeSimple
from RenderWidget import RenderTypeMIP


class LayerVisualization(QMainWindow):
	"""
	LayerVisualization
	"""

	def __init__(self):
		super(LayerVisualization, self).__init__()
		
		self.sliderWidth = 300

		self.mainWidget = QWidget(self)
		self.setCentralWidget(self.mainWidget)
		self.renderWidget = RenderWidget()

		# Create interface actions
		self.actionLoadData = QAction('Load data set', self, shortcut='Ctrl+O')
		self.actionLoadData.setIcon(QIcon(AppVars.imagePath() + "AddButton.png"))
		self.actionLoadData.triggered.connect(self.loadFile)
		self.actionShowSimple = QAction('Switch to simple rendering', self, shortcut='Ctrl+1')
		self.actionShowSimple.setText("Simple")
		self.actionShowSimple.triggered.connect(self.switchToSimple)
		self.actionShowCT = QAction('Switch to CT rendering', self, shortcut='Ctrl+2')
		self.actionShowCT.setText("CT")
		self.actionShowCT.triggered.connect(self.switchToCT)
		self.actionShowMIP = QAction('Switch to MIP rendering', self, shortcut='Ctrl+3')
		self.actionShowMIP.setText("MIP")
		self.actionShowMIP.triggered.connect(self.switchToMIP)

		# Align the dock buttons to the right with a spacer widget
		spacer = QWidget()
		spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		# Add buttons to container on top
		self.toolbar = self.addToolBar('Main tools')
		self.toolbar.addAction(self.actionShowSimple)
		self.toolbar.addAction(self.actionShowCT)
		self.toolbar.addAction(self.actionShowMIP)

		self.toolbar.addWidget(spacer)
		self.toolbar.addAction(self.actionLoadData)
		self.setUnifiedTitleAndToolBarOnMac(True)

		# Slider for simple visualization
		self.slidersSimpleWidget = QSlider(Qt.Horizontal)
		self.slidersSimpleWidget.setMinimumWidth(self.sliderWidth)
		self.slidersSimpleWidget.setMaximumWidth(self.sliderWidth)
		self.slidersSimpleWidget.setMinimum(0)
		self.slidersSimpleWidget.setMaximum(1000)
		self.slidersSimpleWidget.valueChanged.connect(self.simpleSliderValueChanged)
		self.slidersSimpleWidget.setHidden(True)

		# Create sliders for CT transfer function
		slidersLayout = QVBoxLayout()
		slidersLayout.setContentsMargins(0, 0, 0, 0)
		slidersLayout.setSpacing(0)
		self.sliders = []
		for x in range(0, 7):
			slider = QSlider(Qt.Horizontal)
			slider.setMinimum(0)
			slider.setMaximum(1000)
			slider.valueChanged.connect(self.valueChanged)
			self.sliders.append(slider)
			slidersLayout.addWidget(slider)
		
		self.slidersCTWidget = QWidget()
		self.slidersCTWidget.setMinimumWidth(self.sliderWidth)
		self.slidersCTWidget.setMaximumWidth(self.sliderWidth)
		self.slidersCTWidget.setLayout(slidersLayout)
		self.slidersCTWidget.setHidden(True)

		self.minSlider = QSlider(Qt.Horizontal)
		self.minSlider.setMinimum(0)
		self.minSlider.setMaximum(1000)
		self.minSlider.valueChanged.connect(self.mipSliderValueChanged)

		self.maxSlider = QSlider(Qt.Horizontal)
		self.maxSlider.setMinimum(0)
		self.maxSlider.setMaximum(1000)
		self.maxSlider.setValue(1000)
		self.maxSlider.valueChanged.connect(self.mipSliderValueChanged)

		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		layout.addWidget(self.minSlider)
		layout.addWidget(self.maxSlider)

		self.slidersMIPWidget = QWidget()
		self.slidersMIPWidget.setMinimumWidth(self.sliderWidth)
		self.slidersMIPWidget.setMaximumWidth(self.sliderWidth)
		self.slidersMIPWidget.setLayout(layout)
		self.slidersMIPWidget.setHidden(True)

		layout = QHBoxLayout(self.mainWidget)
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.renderWidget)
		layout.addWidget(self.slidersMIPWidget)
		layout.addWidget(self.slidersCTWidget)
		layout.addWidget(self.slidersSimpleWidget)
		self.mainWidget.setLayout(layout)

		self.resize(800, 500)

	def switchToSimple(self):
		self.renderWidget.SetRenderType(RenderTypeSimple)

		self.slidersSimpleWidget.setDisabled(False)
		self.slidersCTWidget.setDisabled(True)
		self.slidersMIPWidget.setDisabled(True)

		self.slidersSimpleWidget.setHidden(False)
		self.slidersCTWidget.setHidden(True)
		self.slidersMIPWidget.setHidden(True)

	def switchToCT(self):
		self.renderWidget.SetRenderType(RenderTypeCT)

		self.slidersSimpleWidget.setDisabled(True)
		self.slidersCTWidget.setDisabled(False)
		self.slidersMIPWidget.setDisabled(True)

		self.slidersSimpleWidget.setHidden(True)
		self.slidersCTWidget.setHidden(False)
		self.slidersMIPWidget.setHidden(True)

	def switchToMIP(self):
		self.renderWidget.SetRenderType(RenderTypeMIP)

		self.slidersSimpleWidget.setDisabled(True)
		self.slidersCTWidget.setDisabled(True)
		self.slidersMIPWidget.setDisabled(False)

		self.slidersSimpleWidget.setHidden(True)
		self.slidersCTWidget.setHidden(True)
		self.slidersMIPWidget.setHidden(False)

	def simpleSliderValueChanged(self):
		sliderValue = float(self.slidersSimpleWidget.value()) / float(self.slidersSimpleWidget.maximum())
		self.renderWidget.lowerBound = self.renderWidget.minimum + (self.renderWidget.maximum - self.renderWidget.minimum) * sliderValue
		self.renderWidget.Update()

	def mipSliderValueChanged(self):
		minValue = float(self.minSlider.value()) / float(self.minSlider.maximum())
		maxValue = float(self.maxSlider.value()) / float(self.maxSlider.maximum())

		self.renderWidget.mipMin = self.renderWidget.minimum + (self.renderWidget.maximum - self.renderWidget.minimum) * minValue
		self.renderWidget.mipMax = self.renderWidget.minimum + (self.renderWidget.maximum - self.renderWidget.minimum) * maxValue

		self.renderWidget.Update()

	def valueChanged(self):
		for x in range(0, len(self.sliders)):
			slider = self.sliders[x]
			sliderValue = float(slider.value()) / float(slider.maximum())
			# Use an square function for easier opacity adjustments
			convertedValue = sliderValue * sliderValue * sliderValue
			self.renderWidget.sectionsOpacity[x] = convertedValue

		self.renderWidget.Update()

	def loadFile(self):
		extensions = DataReader().GetSupportedExtensionsAsString()
		fileName, other = QFileDialog.getOpenFileName(self, "Open data set", "", "Images ("+extensions+")")
		if len(fileName) == 0:
			return

		self.renderWidget.loadFile(fileName)

		# layout = self.mainWidget.layout()
		# layout.setContentsMargins(0, 0, 0, 0)
		# layout.setSpacing(0)
		# layout.addWidget(self.slidersMIPWidget, 0, 1)
		# layout.addWidget(self.slidersCTWidget, 0, 2)
		# layout.addWidget(self.slidersSimpleWidget, 0, 3)
		# self.mainWidget.setLayout(layout)

		self.switchToSimple()

		# layout = self.mainWidget.layout()
		# layout.setContentsMargins(0, 0, 0, 0)
		# layout.setSpacing(0)
		# self.mainWidget.setLayout(layout)

if __name__ == '__main__':
	import sys
	from PySide.QtGui import QApplication
	app = QApplication(sys.argv)

	viewer = LayerVisualization()

	viewer.renderWidget.rwi.Start()
	viewer.raise_()
	viewer.show()
	sys.exit(app.exec_())
