"""
TransferFunctionNodeItem

:Authors:
	Berend Klein Haneveld
"""
from ui.widgets.histogram.NodeItem import NodeItem
from PySide.QtGui import QColor
from PySide.QtCore import QPointF
from PySide.QtCore import Qt


class TransferFunctionNodeItem(NodeItem):
	"""
	TransferFunctionNodeItem
	"""

	def __init__(self):
		super(TransferFunctionNodeItem, self).__init__()

		self.node = None
		self.boundedItem = None
		self.delegate = None
		self.lockX = False

	def setSceneBoundsItem(self, item):
		self.boundedItem = item

	def setPosition(self, position):
		"""
		Position is in values between 0 and 1.
		"""
		margins = self.boundedItem._margins
		rect = self.boundedItem.boundingRect()
		width = rect.width() - (margins.left() + margins.right() + 1)
		height = rect.height() - (margins.top() + margins.bottom() + 1)

		actualX = margins.left() + position[0] * width
		actualY = margins.top() + (1.0 - position[1]) * height

		actualPosition = QPointF()
		actualPosition.setX(actualX)
		actualPosition.setY(actualY)

		self.setPos(actualPosition)

	def updateColor(self, color):
		self._brushNormal.setColor(QColor.fromRgbF(color[0], color[1], color[2]))
		self._brushHighlighted.setColor(QColor.fromRgbF(color[0], color[1], color[2]))
		self.update(self.rect())

	def getPosition(self):
		margins = self.boundedItem._margins
		rect = self.boundedItem.rect()
		width = rect.width() - (margins.left() + margins.right() + 1)
		height = rect.height() - (margins.top() + margins.bottom() + 1)

		pos = self.pos()

		x = (pos.x() - margins.left()) / width
		y = 1.0 - (pos.y() - margins.top()) / height

		return [x, y]

	def setColor(self, color):
		pass

	def setPos(self, position):
		"""
		@overrides(NodeItem)
		"""
		margins = self.boundedItem._margins
		rect = self.boundedItem.rect()
		width = rect.width() - (margins.left() + margins.right() + 1)
		height = rect.height() - (margins.top() + margins.bottom() + 1)

		boundedX = max(position.x(), margins.left())
		boundedX = min(boundedX, margins.left() + width)
		boundedY = max(position.y(), margins.top())
		boundedY = min(boundedY, margins.top() + height)

		boundedPosition = QPointF()
		boundedPosition.setX(boundedX)
		boundedPosition.setY(boundedY)

		super(TransferFunctionNodeItem, self).setPos(boundedPosition)

	def mousePressEvent(self, event):
		super(TransferFunctionNodeItem, self).mousePressEvent(event)
		if event.button() == Qt.LeftButton:
			if self.delegate:
				self.delegate.selectedNode(self)

	def mouseMoveEvent(self, event):
		self.setPos(event.scenePos())
		if self.delegate:
			self.delegate.nodeUpdated(self)
