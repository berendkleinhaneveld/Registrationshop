"""
BackgroundItem

Inspired by BackgroundItem.h and BackgroundItem.cpp by T. Kroes
from Exposure Render (http://code.google.com/p/exposure-render/)

:Authors:
	T. Kroes <t.kroes@tudelft.nl>
	B. Klein Haneveld <b.a.kleinhaneveld@student.tudelft.nl>
"""
from PySide.QtGui import *
from PySide.QtCore import *


class BackgroundItem(QGraphicsRectItem):
	"""
	BackgroundItem
	"""

	def __init__(self, parent=None):
		super(BackgroundItem, self).__init__(parent)

		self._brush = QBrush(QColor(0, 0, 0))
		self._pen = QPen()
		self._margins = QMargins(0, 0, 0, 0)

	def setMargins(self, margins):
		self._margins = margins

	def paint(self, painter, option, widget):
		"""
		Overrides QGraphicsRectItem.paint()
		"""
		x = self._margins.left()
		y = self._margins.top()
		# Qt and rects suck. That is why we need to subtract 1 pixel...
		# Maybe it would be better to create a custom rect class that fixes all stupid
		# Qt conventions that are the result of legacy conventions.
		width = self.rect().width() - (self._margins.left() + self._margins.right() + 1)
		height = self.rect().height() - (self._margins.top() + self._margins.bottom() + 1)
		newRect = QRectF(x, y, width, height)

		self._updateBrush()
		painter.setRenderHint(QPainter.Antialiasing, False)
		painter.setBrush(self._brush)
		painter.setPen(self._pen)
		painter.drawRect(newRect)

	def _updateBrush(self):
		if self.isEnabled():
			self._brush.setColor(QColor.fromHsl(0, 0, 185))
			self._pen.setColor(QColor.fromHsl(0, 0, 140))
		else:
			self._brush.setColor(QColor.fromHsl(0, 0, 210))
			self._pen.setColor(QColor.fromHsl(0, 0, 160))
