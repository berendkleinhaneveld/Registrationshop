"""
TitleWidget

:Authors:
	Berend Klein Haneveld
"""

import sys
from PySide.QtGui import QWidget
from PySide.QtGui import QColor
from PySide.QtGui import QLinearGradient
from PySide.QtGui import QBrush
from PySide.QtGui import QPalette
from PySide.QtGui import QLabel
from PySide.QtGui import QVBoxLayout
from PySide.QtCore import Qt


class TitleWidget(QWidget):
	"""
	TitleWidget holds a title. And paints the background with a gradient.
	"""
	TitleHeight = 20

	def __init__(self, title=None):
		super(TitleWidget, self).__init__()

		if sys.platform.startswith("darwin"):
			color1 = QColor(230, 230, 230, 255)
			color2 = QColor(177, 177, 177, 255)

			gradient = QLinearGradient()
			gradient.setStart(0, 0)
			gradient.setFinalStop(0, TitleWidget.TitleHeight)
			gradient.setColorAt(0, color1)
			gradient.setColorAt(1, color2)

			brush = QBrush(gradient)
			palette = QPalette()
			palette.setBrush(QPalette.Background, brush)
			self.setPalette(palette)
			self.setAutoFillBackground(True)

		self.setMaximumHeight(TitleWidget.TitleHeight)
		self.setMinimumHeight(TitleWidget.TitleHeight)

		self.titleLabel = QLabel("", parent=self)
		font = self.titleLabel.font()
		font.setPixelSize(11)
		self.titleLabel.setFont(font)
		self.titleLabel.setAlignment(Qt.AlignCenter)
		self.titleLabel.setText(title)

		layout = QVBoxLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.titleLabel)
		self.setLayout(layout)

	def setText(self, title):
		self.title = title
		self.titleLabel.setText(self.title)
