"""
SliderFloatWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QSlider
from PySide.QtGui import QDoubleSpinBox
from PySide.QtGui import QGridLayout
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from PySide.QtCore import Qt


class SliderFloatWidget(QWidget):
	"""
	SliderFloatWidget
	"""
	valueChanged = Signal(int)

	def __init__(self):
		super(SliderFloatWidget, self).__init__()

		self.label = QLabel()
		self.slider = QSlider(Qt.Horizontal)
		self.spinbox = QDoubleSpinBox()

		self.slider.valueChanged.connect(self.changedValueFromSlider)
		self.spinbox.valueChanged.connect(self.changedValueFromSpinBox)

		# Keep track of whether one of the values was changed
		# By setting the value of the slider and the spinbox, valueChanged
		# events are fired. These events have to be ignored
		self._changed = False

		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setVerticalSpacing(0)
		layout.addWidget(self.label, 0, 0)
		layout.addWidget(self.slider, 0, 1)
		layout.addWidget(self.spinbox, 0, 2)
		self.setLayout(layout)

	def setName(self, name):
		"""
		Set the name for the slider
		"""
		self.label.setText(name)

	def setRange(self, range):
		"""
		Set the range for the value
		"""
		self.range = range
		self.slider.setMinimum(0.0)
		self.slider.setMaximum(100.0)
		self.spinbox.setRange(self.range[0], self.range[1])

		diff = self.range[1] - self.range[0]
		if diff <= 1:
			self.spinbox.setSingleStep(0.01)

	def setValue(self, value):
		"""
		Set the value for the slider and the spinbox
		"""
		ratio = (value - self.range[0]) / (self.range[1] - self.range[0])
		self._changed = False
		self.slider.setValue(ratio * 100)
		self._changed = False
		self.spinbox.setValue(value)
		self._changed = False

	def value(self):
		return self.spinbox.value()

	@Slot(int)
	def changedValueFromSlider(self, value):
		if self._changed:
			self._changed = False
			return
		ratio = value / 100.0
		val = self.range[0] + ratio * (self.range[1] - self.range[0])
		self._changed = True
		self.spinbox.setValue(val)
		self.valueChanged.emit(val)

	@Slot(float)
	def changedValueFromSpinBox(self, value):
		if self._changed:
			self._changed = False
			return
		ratio = (value - self.range[0]) / (self.range[1] - self.range[0])
		self._changed = True
		self.slider.setValue(ratio * 100.0)
		self.valueChanged.emit(value)


if __name__ == '__main__':
	from PySide.QtGui import QApplication
	from PySide.QtGui import QVBoxLayout
	app = QApplication([])

	sliderWidget = SliderFloatWidget()
	sliderWidget.setName("Test value")
	sliderWidget.setRange([0, 1])
	sliderWidget.setValue(0.5)

	label = QLabel()

	def updateLabel(value):
		label.setText(str(sliderWidget.value()))

	sliderWidget.valueChanged.connect(updateLabel)

	layout = QVBoxLayout()
	layout.addWidget(QLabel("Test sliders"))
	layout.addWidget(sliderWidget)
	layout.addWidget(label)

	widget = QWidget()
	widget.setLayout(layout)
	widget.show()
	app.exec_()
