"""
RenderMixerParamWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QSlider
from PySide.QtGui import QCheckBox
from PySide.QtCore import Qt
from PySide.QtCore import Slot


class RenderMixerParamWidget(QWidget):
	"""
	RenderMixerParamWidget is a widget that shows some mixer controls
	for the multi-volume render widget.
	"""
	def __init__(self, multiRenderController):
		super(RenderMixerParamWidget, self).__init__()
		self.multiRenderController = multiRenderController

		self.labelFixedOpacity = QLabel("Opacity of fixed volume")
		self.labelFixedOpacity.setVisible(False)
		self.labelMovingOpacity = QLabel("Opacity of moving volume")
		self.labelMovingOpacity.setVisible(False)

		self.sliderFixedOpacity = QSlider(Qt.Horizontal)
		self.sliderFixedOpacity.valueChanged.connect(self.fixedSliderChangedValue)
		self.sliderFixedOpacity.setVisible(False)
		self.sliderFixedOpacity.setValue(100)

		self.sliderMovingOpacity = QSlider(Qt.Horizontal)
		self.sliderMovingOpacity.valueChanged.connect(self.movingSliderChangedValue)
		self.sliderMovingOpacity.setValue(100)
		self.sliderMovingOpacity.setVisible(False)

		self.transformCheckBox = QCheckBox()
		self.transformCheckBox.clicked.connect(self.transformCheckBoxChanged)
		self.multiRenderController.fixedDataChanged.connect(self.dataChanged)
		self.multiRenderController.movingDataChanged.connect(self.dataChanged)
		self.transformCheckBox.setVisible(False)

		self.multiRenderController.fixedVolumePropertyUpdated.connect(self.update)
		self.multiRenderController.movingVolumePropertyUpdated.connect(self.update)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(self.labelFixedOpacity, 0, 0)
		layout.addWidget(self.sliderFixedOpacity, 0, 1)
		layout.addWidget(self.labelMovingOpacity, 1, 0)
		layout.addWidget(self.sliderMovingOpacity, 1, 1)
		layout.addWidget(self.transformCheckBox, 2, 0)
		self.setLayout(layout)

	@Slot(object)
	def dataChanged(self):
		self.sliderFixedOpacity.setVisible(self.multiRenderController.fixedImageData is not None)
		self.sliderMovingOpacity.setVisible(self.multiRenderController.movingImageData is not None)
		self.labelFixedOpacity.setVisible(self.sliderFixedOpacity.isVisible())
		self.labelMovingOpacity.setVisible(self.sliderMovingOpacity.isVisible())
		self.transformCheckBox.setVisible(self.sliderMovingOpacity.isVisible())

	@Slot(int)
	def fixedSliderChangedValue(self, value):
		opacity = self.applyOpacityFunction(float(value) / 100.0)
		self.multiRenderController.setFixedOpacity(opacity)

	@Slot(int)
	def movingSliderChangedValue(self, value):
		opacity = self.applyOpacityFunction(float(value) / 100.0)
		self.multiRenderController.setMovingOpacity(opacity)

	@Slot(bool)
	def transformCheckBoxChanged(self):
		showTransformWidget = self.transformCheckBox.checkState() == Qt.Checked
		self.multiRenderController.setTransformBoxVisibility(showTransformWidget)

	@Slot(object)
	def update(self, volumeProperty):
		opacity = self.multiRenderController.fixedOpacity
		self.sliderFixedOpacity.setValue(pow(opacity, 1.0/3.0) * 100.0)
		opacity = self.multiRenderController.movingOpacity
		self.sliderMovingOpacity.setValue(pow(opacity, 1.0/3.0) * 100.0)

	def applyOpacityFunction(self, value):
		"""
		Make sure that the slider opacity values are not linear.
		"""
		return value * value * value
