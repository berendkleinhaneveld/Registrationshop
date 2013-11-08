"""
TransferFunctionItem

:Authors:
	B. Klein Haneveld <b.a.kleinhaneveld@student.tudelft.nl>
"""
from PySide.QtGui import *
from PySide.QtCore import *


class TransferFunctionItem(QGraphicsRectItem):
	"""
	TransferFunctionItem
	"""

	def __init__(self, parent=None):
		super(TransferFunctionItem, self).__init__(parent)

		self._margins = None
		self.delegate = None

	def mouseDoubleClickEvent(self, event):
		if self.delegate:
			margins = self._margins
			rect = self.rect()
			width = rect.width() - (margins.left() + margins.right() + 1)
			height = rect.height() - (margins.top() + margins.bottom() + 1)

			position = event.pos()

			boundedX = max(position.x() - margins.left(), 0)
			boundedX = min(boundedX, width)
			boundedY = max(position.y() - margins.top(), 0)
			boundedY = min(boundedY, height)

			coord = [boundedX / width, 1.0 - boundedY / height]

			self.delegate.addNodeAtCoord(coord)

	def mousePressEvent(self, event):
		if self.delegate:
			self.delegate.unselect()

	def setMargins(self, margins):
		self._margins = margins

	def paint(self, painter, option, widget):
		pass

	def update(self):
		"""
		Overrides QGraphicsRectItem.update()
		"""
		super(TransferFunctionItem, self).update()
