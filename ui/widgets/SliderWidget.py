"""
SliderWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QSlider
from PySide2.QtWidgets import QSpinBox
# from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QGridLayout
from PySide2.QtCore import Signal
from PySide2.QtCore import Slot
from PySide2.QtCore import Qt


class SliderWidget(QWidget):
	"""
	SliderWidget
	"""
	valueChanged = Signal(int)

	def __init__(self):
		super(SliderWidget, self).__init__()

		self.label = QLabel()
		self.slider = QSlider(Qt.Horizontal)
		self.spinbox = QSpinBox()

		self.slider.valueChanged.connect(self.changedValue)
		self.spinbox.valueChanged.connect(self.changedValue)

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
		self.slider.setMinimum(range[0])
		self.spinbox.setMinimum(range[0])
		self.slider.setMaximum(range[1])
		self.spinbox.setMaximum(range[1])

	def setValue(self, value):
		"""
		Set the value for the slider and the spinbox
		"""
		self.slider.setValue(value)
		self.spinbox.setValue(value)

	def value(self):
		return self.slider.value()

	@Slot(int)
	def changedValue(self, value):
		self.setValue(value)
		self.valueChanged.emit(value)


if __name__ == '__main__':
	from PySide2.QtWidgets import QApplication
	from PySide2.QtWidgets import QVBoxLayout
	app = QApplication([])

	sliderWidget = SliderWidget()
	sliderWidget.setName("Test value")
	sliderWidget.setRange([-100, 200])
	sliderWidget.setValue(300)

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
