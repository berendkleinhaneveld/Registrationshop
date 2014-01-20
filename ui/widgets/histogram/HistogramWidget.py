"""
HistogramWidget

Inspired by HistogramView class by T. Kroes from
Exposure Render (http://code.google.com/p/exposure-render/)

:Authors:
	T. Kroes <t.kroes@tudelft.nl>
	B. Klein Haneveld <b.a.kleinhaneveld@student.tudelft.nl>
"""
from PySide.QtGui import *
from PySide.QtCore import *
from BackgroundItem import BackgroundItem
from HistogramItem import HistogramItem
from GridItem import GridItem


class HistogramWidget(QGraphicsView):
	"""
	HistogramWidget
	"""
	AxeClear = "HAC"
	AxeNormal = "HAD"
	AxePercentage = "HAP"
	AxeLog = "HAL"

	def __init__(self):
		super(HistogramWidget, self).__init__()
		self.setFrameShadow(QFrame.Plain)
		self.setFrameShape(QFrame.NoFrame)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setRenderHint(QPainter.Antialiasing)

		self._leftAxeMode = HistogramWidget.AxeClear
		self._bottomAxeMode = HistogramWidget.AxeClear

		self._histogram = None
		self._margin = QMargins(0, 0, 0, 0)
		self._backgroundItem = BackgroundItem()
		self._gridItem = GridItem()
		self._histogramItem = HistogramItem()

		self._items = [self._backgroundItem, self._gridItem, self._histogramItem]
		zValue = 0
		self._scene = QGraphicsScene(self)
		for item in self._items:
			self._scene.addItem(item)
			item.setZValue(zValue)
			zValue += 100
		self.setScene(self._scene)

	def setAxeMode(self, left=None, bottom=None):
		if left:
			self._leftAxeMode = left
			if self._leftAxeMode == self.AxeLog:
				self._histogramItem.functionType = HistogramItem.TypeLog
			else:
				self._histogramItem.functionType = HistogramItem.TypeNormal
			self._histogramItem.update()
		if bottom:
			self._bottomAxeMode = bottom
		self._updateAxis()
		self.updateScene()

	def setHistogram(self, histogram):
		self._histogram = histogram
		self._histogramItem.setHistogram(histogram)
		self._updateAxis()

	def addItem(self, item):
		self._scene.addItem(item)
		self._items.append(item)
		self.update()

	def resizeEvent(self, resizeEv):
		"""
		Overrides QGraphicsView.resizeEvent()
		"""
		super(HistogramWidget, self).resizeEvent(resizeEv)
		self.updateScene()

	def wheelEvent(self, wheelEv):
		"""
		Overrides QGraphicsView.wheelEvent()
		Make sure nothing happens when the user scrolls over this widget.
		"""
		wheelEv.ignore()

	@Slot()
	def updateScene(self):
		"""
		The QGraphicsScene.changed() will automatically be linked to
		this slot. If this slot is missing, then PySide will crash on
		close where it is unable to disconnect this slot...
		Overrides QGraphicsView.updateScene()
		"""
		self.update()

	def update(self):
		"""
		Overrides QGraphicsView.update()
		"""
		rect = self.rect()

		if len(self._gridItem._itemsLeft) > 0 and len(self._gridItem._itemsBottom) > 0:
			# left, top, right, bottom
			self._margin = QMargins(30, 9, 9, 30)
		elif len(self._gridItem._itemsLeft) > 0:
			self._margin = QMargins(30, 9, 9, 9)
		elif len(self._gridItem._itemsBottom) > 0:
			self._margin = QMargins(9, 9, 9, 30)
		else:
			self._margin = QMargins(9, 9, 9, 9)

		for item in self._items:
			item.setRect(rect)
			if hasattr(item, "setMargins"):
				item.setMargins(self._margin)

		self._histogramItem.update()

	def _updateAxis(self):
		leftAxis = []
		bottomAxis = []

		if self._leftAxeMode is HistogramWidget.AxeClear:
			pass
		elif self._leftAxeMode is HistogramWidget.AxeNormal:
			if self._histogramItem.functionType == HistogramItem.TypeLog:
				positions = []
				maxY = self._histogramItem.func(self._histogram.maxY)
				lala = int(round(maxY)+1)
				for i in range(lala):
					positions.append(float(i / float(maxY)))
					val = self._histogramItem.invfunc(i)
					text = "%.0f" % val
					leftAxis.append(text)
				self._gridItem.setLeftGridPositions(positions)
			else:
				minY = self._histogram.minY
				maxY = self._histogram.maxY
				rangeY = maxY - minY
				markerCount = 11
				chunk = rangeY / float(markerCount - 1)
				for i in range(markerCount):
					val = minY + i * chunk
					text = "%.1f" % val
					leftAxis.append(text)
		elif self._leftAxeMode is HistogramWidget.AxePercentage:
			for i in range(11):
				leftAxis.append(str(i * 10) + "%")

		if self._bottomAxeMode is HistogramWidget.AxeClear:
			pass
		elif self._bottomAxeMode is HistogramWidget.AxeNormal:
			rangeX = self._histogram.maxX - self._histogram.minX
			binCount = len(self._histogram.bins)
			markerCount = min(binCount, 11)
			chunk = rangeX / (markerCount - 1)
			for i in range(binCount):
				if i % chunk == 0 or i == binCount-1:
					bottomAxis.append(str(int(self._histogram.minX + i)))
				else:
					bottomAxis.append("")
		elif self._bottomAxeMode is HistogramWidget.AxePercentage:
			pass

		self._gridItem.setLeftGridItems(leftAxis)
		self._gridItem.setBottomGridItems(bottomAxis)
