"""
TrackingHistogramWidget

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtGui import *
from PySide.QtCore import *
from HistogramWidget import HistogramWidget
from TrackingNodeItem import TrackingNodeItem


class TrackingHistogramWidget(HistogramWidget):
	"""
	TrackingHistogramWidget
	"""
	updatePosition = Signal(float)

	def __init__(self):
		super(TrackingHistogramWidget, self).__init__()
		self.nodeItem = None

	def update(self):
		super(TrackingHistogramWidget, self).update()
		if not self.nodeItem:
			return

		self.nodeItem.update()

	def setHistogram(self, histogram):
		super(TrackingHistogramWidget, self).setHistogram(histogram)
		if not self.nodeItem:
			self.nodeItem = TrackingNodeItem()
			self.scene().addItem(self.nodeItem)
		self.nodeItem.setHistogramItem(self._histogramItem)
		self.nodeItem.setPos(QPoint(0, 0))
		self.nodeItem.setZValue(300)
		self.nodeItem.delegate = self

	def updatePos(self, position):
		self.updatePosition.emit(position)
