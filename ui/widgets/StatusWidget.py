"""
StatusWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QFrame
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QPainter
from PySide.QtGui import QPen
from PySide.QtGui import QColor
from PySide.QtGui import QFont
from PySide.QtCore import QRectF
from core.decorators import Singleton


@Singleton
class StatusWidget(QFrame):
	"""
	StatusWidget
	"""

	def __init__(self):
		QFrame.__init__(self)

		self._color = [220, 220, 220]

		self._font = QFont()
		self._font.setPixelSize(10)

		self._pen = QPen(QColor(100, 100, 100, 255))

		self.label = QLabel()
		self.label.setWordWrap(True)
		self.label.setFont(self._font)
		self.label.setMaximumWidth(300)
		self.label.setMaximumHeight(36)
		self.label.setMinimumHeight(36)

		layout = QGridLayout()
		layout.setSpacing(0)
		layout.addWidget(self.label)
		self.setLayout(layout)

		self.setMinimumWidth(360)
		self.setMaximumWidth(360)

	def setText(self, text):
		self.label.setText(text)

	def paintEvent(self, ev):
		size = self.size()
		height = size.height()-5
		width = size.width()-5

		offset = 0.5
		rect = QRectF(2.0+offset, 2.0+offset, width, height)
		painter = QPainter(self)

		painter.setPen(self._pen)
		painter.setBrush(QColor(self._color[0], self._color[1], self._color[2]))
		painter.setRenderHint(QPainter.Antialiasing)
		painter.setRenderHint(QPainter.HighQualityAntialiasing)
		painter.drawRoundedRect(rect, 4, 4)
