"""
Histogram

Ported from Histogram.h and Histogram.cpp by T. Kroes
from Exposure Render (http://code.google.com/p/exposure-render/)

:Authors:
	T. Kroes <t.kroes@tudelft.nl>
	B. Klein Haneveld <b.a.kleinhaneveld@student.tudelft.nl>
"""
from PySide.QtGui import *
from PySide.QtCore import *


class Histogram(QObject):
	"""
	Histogram
	"""

	histogramChanged = Signal()

	def __init__(self, parent=None):
		super(Histogram, self).__init__(parent)

		self._enabled = False
		self._bins = []
		self.maxY = 0
		self.minY = 0
		self.maxX = 0
		self.minX = 0

	@property
	def enabled(self):
		return self._enabled

	@enabled.setter
	def enabled(self, value):
		self._enabled = value
		self.histogramChanged.emit()

	@property
	def bins(self):
		return self._bins

	@bins.setter
	def bins(self, bins):
		self._bins = bins
		self._updateMaxAndMin()
		self._enabled = True
		self.histogramChanged.emit()
	
	def setBins(self, pBins, nBins):
		self._bins = []
		for i in range(nBins):
			self._bins.append(pBins[i])

		self._updateMaxAndMin()
		self._enabled = True
		self.histogramChanged.emit()

	def reset(self):
		self._enabled = False
		self._bins = []
		self.maxY = 0
		self.minY = 0
		self.maxX = 0
		self.minX = 0
		self.histogramChanged.emit()

	def _updateMaxAndMin(self):
		if len(self._bins) == 0:
			self.minY = 0
			self.maxY = 0
			return

		self.minY = self._bins[0]
		self.maxY = self._bins[0]
		for x in self._bins:
			self.minY = min(x, self.minY)
			self.maxY = max(x, self.maxY)

		self.minX = 0
		self.maxX = len(self._bins)-1
