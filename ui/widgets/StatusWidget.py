"""
StatusWidget

:Authors:
	Berend Klein Haneveld
"""

import sys
from PySide.QtGui import QFrame
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QPainter
from PySide.QtGui import QPen
from PySide.QtGui import QColor
from PySide.QtGui import QScrollArea
from PySide.QtGui import QFont
from PySide.QtCore import Qt
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

		self._osx = sys.platform.startswith("darwin")
		self._font = QFont()
		self._font.setPointSize(10)

		self.label = QLabel()
		self.label.setWordWrap(True)
		self.label.setFont(self._font)

		self.scrollArea = QScrollArea()
		self.scrollArea.setFrameShape(QFrame.NoFrame)
		self.scrollArea.setAutoFillBackground(False)
		self.scrollArea.setAttribute(Qt.WA_TranslucentBackground)
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setMinimumHeight(40)
		self.scrollArea.setMaximumHeight(40)
		self.scrollArea.setWidget(self.label)

		if self._osx:
			self.scrollArea.setStyleSheet("background: rgb("
				+ str(self._color[0]) + ", "
				+ str(self._color[1]) + ", "
				+ str(self._color[2]) + ")")

		layout = QGridLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(7, 7, 7, 7)
		layout.addWidget(self.scrollArea)
		self.setLayout(layout)

		self.setMinimumWidth(350)
		self.setMaximumWidth(350)

	def setText(self, text):
		self.label.setText(text)

	def paintEvent(self, ev):
		if not self._osx:
			return

		size = self.size()
		height = size.height()-3
		width = size.width()-3

		offset = 0.5
		rect = QRectF(2.0+offset, 2.0+offset, width+offset, height+offset)
		painter = QPainter(self)
		pen = QPen(QColor(100, 100, 100, 255))
		pen.setWidth(.1)
		painter.setPen(pen)
		painter.setBrush(QColor(self._color[0], self._color[1], self._color[2]))
		painter.setRenderHint(QPainter.Antialiasing)
		painter.setRenderHint(QPainter.HighQualityAntialiasing)
		painter.drawRoundedRect(rect, 4, 4)
