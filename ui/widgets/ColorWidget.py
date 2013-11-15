"""
ColorWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QPainter
from PySide.QtGui import QColor
from PySide.QtGui import QPushButton
from PySide.QtGui import QColorDialog
from PySide.QtGui import QButtonGroup
from PySide.QtGui import QGridLayout
from PySide.QtGui import QPen
from PySide.QtCore import QSize
from PySide.QtCore import QRectF
from PySide.QtCore import Signal


class ColorWidget(QWidget):
	"""
	ColorWidget
	"""

	valueChanged = Signal(object)

	def __init__(self):
		super(ColorWidget, self).__init__()

		self.label = QLabel()
		self.color = [1.0, 1.0, 1.0]
		
		buttonLayout = QHBoxLayout()
		buttonLayout.setContentsMargins(8, 0, 0, 0)

		self.buttonWidget = QWidget()
		self.buttonWidget.setLayout(buttonLayout)

		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		layout.addWidget(self.label, 0, 0)
		layout.addWidget(self.buttonWidget, 0, 1)
		self.setLayout(layout)

	def setName(self, name):
		self.label.setText(name)


class ColorPickerWidget(ColorWidget):
	def __init__(self):
		super(ColorPickerWidget, self).__init__()

		self.colorButton = ColorButton()
		self.colorButton.setColor(self.color)
		self.colorButton.clicked.connect(self.showColorDialog)

		layout = self.buttonWidget.layout()
		layout.addWidget(self.colorButton)

	def showColorDialog(self):
		color = QColorDialog.getColor()
		if not color.isValid():
			return
		rgba = list(color.getRgbF())

		self.colorButton.setColor(rgba[0:3])
		self.color = self.colorButton.color
		self.valueChanged.emit(self.color)
		

class ColorChoiceWidget(ColorWidget):
	def __init__(self):
		super(ColorChoiceWidget, self).__init__()

		self.buttons = []

		self.buttonGroup = QButtonGroup()
		self.buttonGroup.setExclusive(True)
		self.buttonGroup.buttonClicked.connect(self.selectColor)

	def setColors(self, colors):
		layout = self.buttonWidget.layout()
		id = 0
		for color in colors:
			button = ColorButton()
			button.setColor(color)
			button.setCheckable(True)
			layout.addWidget(button)
			self.buttonGroup.addButton(button)
			self.buttonGroup.setId(button, id)
			id += 1
		layout.addStretch(10)

	def setColor(self, color):
		self.color = color
		for button in self.buttonGroup.buttons():
			diffs = map(lambda x, y: abs(x - y), button.color, color)
			if sum(diffs) < 0.0001:
				button.setChecked(True)
				break

	def selectColor(self, button):
		self.color = button.color
		self.valueChanged.emit(self.color)
		

class ColorButton(QPushButton):
	def __init__(self):
		super(ColorButton, self).__init__()
		self.color = [0.8, 0.8, 0.8]

		self.setMinimumSize(QSize(24, 24))
		self.setMaximumSize(QSize(24, 24))
	
	def setColor(self, color):
		self.color = color
		self.update(self.rect())

	def paintEvent(self, ev):
		if self.isEnabled():
			color = self.color
			colorBorder = [0.4, 0.4, 0.4]
		else:
			color = [0.8, 0.8, 0.8]
			colorBorder = [0.7, 0.7, 0.7]

		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.setRenderHint(QPainter.HighQualityAntialiasing)

		if self.isChecked():
			pen = QPen(QColor.fromRgbF(0.2, 0.2, 0.2))
			pen.setWidth(2.0)
		else:
			pen = QPen(QColor.fromRgbF(colorBorder[0], colorBorder[1], colorBorder[2]))
			pen.setWidth(1.0)

		size = self.size()
		sizeCircle = 12.0
		x = size.width() / 2.0 - (sizeCircle / 2.0)
		y = size.height() / 2.0 - (sizeCircle / 2.0)
		rect = QRectF(x, y, sizeCircle, sizeCircle)
		painter.setPen(pen)
		painter.setBrush(QColor.fromRgbF(color[0], color[1], color[2]))
		painter.drawEllipse(rect)


if __name__ == '__main__':
	from PySide.QtGui import QApplication
	from PySide.QtGui import QVBoxLayout
	app = QApplication([])

	colorWidget = ColorPickerWidget()
	colorWidget.setName("Color")

	colorChooser = ColorChoiceWidget()
	colorChooser.setName("Pick a color:")
	colorChooser.setColors([[1.0, 1.0, 1.0], [0.3, 0.7, 0.9], [0.9, 0.3, 0.8], [0, 0, 0]])

	layout = QVBoxLayout()
	layout.addWidget(QLabel("Test color widget"))
	layout.addWidget(colorWidget)
	layout.addWidget(colorChooser)

	widget = QWidget()
	widget.setLayout(layout)
	widget.show()
	app.exec_()
