"""
GridItem

Inspired by GridItem.h and GridItem.cpp by T. Kroes
from Exposure Render (http://code.google.com/p/exposure-render/)

:Authors:
	T. Kroes <t.kroes@tudelft.nl>
	B. Klein Haneveld <b.a.kleinhaneveld@student.tudelft.nl>
"""
from PySide.QtGui import *
from PySide.QtCore import *


class GridItem(QGraphicsRectItem):
	"""
	GridItem
	"""

	def __init__(self, parent=None):
		super(GridItem, self).__init__(parent)

		self._brush = QBrush()
		self._pen = QPen()
		
		self._font = QFont()
		self._font.setFamily("Arial")
		self._font.setPointSize(8)

		# Lists of string items
		self._itemsLeft = []
		self._itemsBottom = []

		# Custom positionings of the items on the left
		# Should be values in range 0.0 to 1.0
		self._positionsLeft = None

		self.setAcceptHoverEvents(True)
		self.setEnabled(True)

	def setLeftGridItems(self, items):
		self._itemsLeft = items

	def setLeftGridPositions(self, positions):
		self._positionsLeft = positions

	def setBottomGridItems(self, items):
		self._itemsBottom = items

	def setMargins(self, margins):
		self._margins = margins

	def setEnabled(self, enabled):
		"""
		Overrides QGraphicsRectItem.setEnabled()
		"""
		super(GridItem, self).setEnabled(enabled)
		if enabled:
			self._brush.setColor(QColor.fromHsl(0, 0, 170))
			self._pen.setColor(QColor.fromHsl(0, 0, 170))
		else:
			self._brush.setColor(QColor.fromHsl(0, 0, 210))
			self._pen.setColor(QColor.fromHsl(0, 0, 190))

	def paint(self, painter, option, widget):
		"""
		Overrides QGraphicsRectItem.paint()
		"""
		painter.setRenderHint(QPainter.Antialiasing, False)
		painter.setBrush(self._brush)
		painter.setPen(self._pen)
		painter.setFont(self._font)

		xOffset = self._margins.left()
		yOffset = self._margins.top()
		# Qt and rects suck. That is why we need to subtract 1 pixel...
		# Maybe it would be better to create a custom rect class that fixes all stupid
		# Qt conventions that are the result of legacy conventions.
		width = self.rect().width() - (self._margins.left() + self._margins.right() + 1)
		height = self.rect().height() - (self._margins.top() + self._margins.bottom() + 1)

		# Horizontal lines
		deltaY = height / float(len(self._itemsLeft)-1)
		for i in range(len(self._itemsLeft)):
			# Draw line through main rect
			if not self._positionsLeft:
				yPos = (yOffset + height) - (i * deltaY)
			else:
				yPos = (yOffset + height) - (self._positionsLeft[i] * height)
			if i > 0 and i < len(self._itemsLeft)-1:
				painter.drawLine(QPointF(xOffset, yPos), QPointF(width + xOffset, yPos))

			# Draw little extruding part on left scale + text item
			if self._margins.left() > 2:
				painter.drawLine(QPointF(xOffset - 2, yPos), QPointF(xOffset, yPos))
				painter.drawText(QRectF(0, (-0.5 * 10) + yPos, xOffset-3, 10), (Qt.AlignVCenter | Qt.AlignRight), self._itemsLeft[i])

		# Vertical lines
		deltaX = width / float(len(self._itemsBottom)-1)
		for i in range(len(self._itemsBottom)):
			# If the item at the bottom is an empty string, don't draw a line
			# and continue to the next item
			if len(self._itemsBottom[i]) > 0:
				xPos = i * deltaX + xOffset
				if i > 0 and i < len(self._itemsBottom)-1:
					painter.drawLine(QPointF(xPos, yOffset), QPointF(xPos, height+yOffset))
				painter.drawText(QRectF(xPos - (0.5 * xOffset), height + 10, xOffset, 10), Qt.AlignCenter, self._itemsBottom[i])
