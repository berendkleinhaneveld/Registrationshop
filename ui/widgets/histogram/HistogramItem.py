"""
HistogramItem

Inspired by HistogramItem.h and HistogramItem.cpp by T. Kroes
from Exposure Render (http://code.google.com/p/exposure-render/)

:Authors:
	T. Kroes <t.kroes@tudelft.nl>
	B. Klein Haneveld <b.a.kleinhaneveld@student.tudelft.nl>
"""
from PySide.QtGui import *
from PySide.QtCore import *
from Histogram import Histogram
import math


class HistogramItem(QGraphicsRectItem):
	"""
	HistogramItem
	"""

	TypeNormal = "TypeNormal"
	TypeLog = "TypeLog"

	def __init__(self, parent=None):
		super(HistogramItem, self).__init__()

		self._histogram = Histogram()
		self._brush = QBrush()
		self._pen = QPen()
		self._polygonItem = QGraphicsPolygonItem(self)
		self._lines = []
		self._margins = QMargins(0, 0, 0, 0)
		self.functionType = self.TypeNormal

		self.setBrush(Qt.NoBrush)
		self.setPen(Qt.NoPen)

	def setHistogram(self, histogram):
		self._histogram = histogram
		self.update()

	def setMargins(self, margins):
		self._margins = margins

	def func(self, value):
		if self.functionType == self.TypeLog:
			return math.log10(value - self._histogram.minY + 1)
		return value

	def invfunc(self, value):
		if self.functionType == self.TypeLog:
			return math.pow(10, value)
		return value

	def update(self):
		"""
		Overrides QGraphicsRectItem.update()
		"""
		self.setVisible(self._histogram.enabled)
		if not self._histogram.enabled:
			return

		# Clear the lines from previous drawing
		for i in range(len(self._lines)):
			self.scene().removeItem(self._lines[i])
		self._lines = []

		xOffset = self._margins.left()
		yOffset = self._margins.top()+1
		width = self.rect().width() - (self._margins.left() + self._margins.right() + 1)
		height = self.rect().height() - (self._margins.top() + self._margins.bottom() + 1)
		binCount = len(self._histogram.bins)

		polygon = QPolygonF()
		cachedCanvasPoint = QPointF(xOffset, height + yOffset)

		for i in range(len(self._histogram.bins)):
			canvasPoint = QPointF()
			canvasPoint.setX(xOffset + width * float(i) / float(binCount-1))

			currVal = self.func(float(self._histogram.bins[i]))
			minimum = self.func(self._histogram.minY)
			maximum = self.func(self._histogram.maxY)

			if currVal <= minimum:
				# Clip at the bottom of the histogram
				canvasPoint.setY(height + yOffset)
			elif currVal >= maximum:
				canvasPoint.setY(yOffset)
			else:
				ratio = (currVal - minimum) / float(maximum - minimum)
				y = (yOffset + height) - (ratio * height)
				canvasPoint.setY(y)

			if i == 0:
				centerCopy = QPointF()
				centerCopy.setX(canvasPoint.x())
				centerCopy.setY(height+yOffset)
				polygon.append(centerCopy)

			polygon.append(canvasPoint)

			if i == binCount-1:
				centerCopy = QPointF()
				centerCopy.setX(canvasPoint.x())
				centerCopy.setY(height+yOffset)
				polygon.append(centerCopy)

			if i > 0:
				pLineItem = QGraphicsLineItem(self)
				pLineItem.setLine(QLineF(cachedCanvasPoint, canvasPoint))
				pLineItem.setPen(QPen(QColor.fromHsl(0, 30, 140)))
				self._lines.append(pLineItem)

			cachedCanvasPoint.setX(canvasPoint.x())
			cachedCanvasPoint.setY(canvasPoint.y())

		linearGradient = QLinearGradient()
		linearGradient.setStart(xOffset, height + yOffset)
		linearGradient.setFinalStop(xOffset, yOffset)
		linearGradient.setColorAt(0, QColor.fromHsl(0, 10, 150, 0))
		linearGradient.setColorAt(1, QColor.fromHsl(0, 100, 150, 150))

		self._polygonItem.setPolygon(polygon)
		self._polygonItem.setBrush(QBrush(linearGradient))
		self._polygonItem.setPen(Qt.NoPen)
