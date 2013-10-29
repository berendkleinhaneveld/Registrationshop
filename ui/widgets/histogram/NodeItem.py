"""
NodeItem

Inspired by NodeItem.h and NodeItem.cpp by T. Kroes
from Exposure Render (http://code.google.com/p/exposure-render/)

:Authors:
	T. Kroes <t.kroes@tudelft.nl>
	B. Klein Haneveld <b.a.kleinhaneveld@student.tudelft.nl>
"""
from PySide.QtGui import *
from PySide.QtCore import *


class NodeItem(QGraphicsEllipseItem):
	"""
	NodeItem
	"""

	def __init__(self):
		super(NodeItem, self).__init__()

		self._node = None
		self._cursor = QCursor()
		self._lastPos = QPointF()
		self._pen = QPen()
		self._brush = QBrush()

		self._radius = 4.0
		self._selectedRadius = 6.6
		self._brushNormal = QBrush(QColor.fromHsl(0, 100, 150))
		self._brushHighlighted = QBrush(QColor.fromHsl(0, 130, 150))
		self._brushDisabled = QBrush(QColor.fromHsl(0, 0, 230))
		self._brushSelection = QBrush(QColor.fromHsl(43, 140, 140, 255))

		self._penNormal = QPen(QColor.fromHsl(0, 100, 100))
		self._penHighlighted = QPen(QColor.fromHsl(0, 150, 50))
		self._penDisabled = QPen(QColor.fromHsl(0, 0, 200))
		self._penSelection = QPen(QColor.fromHsl(0, 150, 100, 150))

		self.setBrush(self._brushNormal)
		self.setPen(self._penNormal)

		self.setFlag(QGraphicsItem.ItemIsMovable)
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
		self.setFlag(QGraphicsItem.ItemIsSelectable)

	def setPos(self, position):
		"""
		@overrides(QGraphicsEllipseItem)
		"""
		if self.pos() == position:
			return

		super(NodeItem, self).setPos(position)

		rect = QRectF()
		rect.setTopLeft(QPointF(-self._selectedRadius, -self._selectedRadius))
		rect.setWidth(2.0 * self._selectedRadius)
		rect.setHeight(2.0 * self._selectedRadius)
		self.setRect(rect)

	def paint(self, painter, option, widget):
		"""
		@overrides(QGraphicsEllipseItem)
		"""
		brush = pen = None
		if self.isEnabled():
			if self.isUnderMouse() or self.isSelected():
				brush = self._brushHighlighted
				pen = self._penHighlighted
			else:
				brush = self._brushNormal
				pen = self._penNormal
			if self.isUnderMouse() or self.isSelected():
				painter.setBrush(self._brushSelection)
				painter.setPen(self._penSelection)
				painter.drawEllipse(self.rect())
		else:
			brush = self._brushDisabled
			pen = self._penDisabled

		selRect = self.rect()
		selRect.adjust(2.6, 2.6, -2.6, -2.6)
		painter.setBrush(brush)
		painter.setPen(pen)
		painter.drawEllipse(selRect)

	def mousePressEvent(self, event):
		"""
		@overrides(QGraphicsEllipseItem)
		"""
		super(NodeItem, self).mousePressEvent(event)
		if event.button() == Qt.LeftButton:
			self._cursor.setShape(Qt.SizeAllCursor)
			self.setCursor(self._cursor)

	def mouseReleaseEvent(self, event):
		"""
		@overrides(QGraphicsEllipseItem)
		"""
		super(NodeItem, self).mouseReleaseEvent(event)
		self._cursor.setShape(Qt.ArrowCursor)
		self.setCursor(self._cursor)

	def mouseMoveEvent(self, event):
		"""
		@overrides(QGraphicsEllipseItem)
		"""
		super(NodeItem, self).mouseMoveEvent(event)
		if event.button() == Qt.LeftButton:
			self._cursor.setShape(Qt.SizeAllCursor)
			self.setCursor(self._cursor)

	def itemChange(self, change, value):
		"""
		@overrides(QGraphicsEllipseItem)
		"""
		return super(NodeItem, self).itemChange(change, value)
