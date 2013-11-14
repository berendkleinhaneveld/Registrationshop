"""
TransferFunctionWidget

:Authors:
	Berend Klein Haneveld
"""
from ui.widgets.histogram import Histogram
from ui.widgets.histogram import HistogramWidget
from ui.widgets.transferfunction import TransferFunctionNodeItem
from ui.widgets.transferfunction import TransferFunctionItem
from ui.widgets.ColorWidget import ColorButton
from core.data.DataAnalyzer import DataAnalyzer
from PySide.QtGui import QWidget
from PySide.QtGui import QGridLayout
from PySide.QtGui import QGraphicsLineItem
from PySide.QtGui import QPen
from PySide.QtGui import QLabel
from PySide.QtGui import QLineEdit
from PySide.QtGui import QPushButton
from PySide.QtGui import QColorDialog
from PySide.QtGui import QColor
from PySide.QtCore import QLineF
from PySide.QtCore import Signal
from PySide.QtCore import Slot
from ui.widgets import Style


class TransferFunctionWidget(QWidget):
	"""
	TransferFunctionWidget
	"""

	valueChanged = Signal(object)

	def __init__(self):
		super(TransferFunctionWidget, self).__init__()

		self.nodes = []
		self.lines = []
		self.histogram = Histogram()
		self.histogram.enabled = False

		# Create a histogram widget for the background of the transfer function editor
		self.histogramWidget = HistogramWidget()
		self.histogramWidget.setHistogram(self.histogram)
		self.histogramWidget.setAxeMode(bottom=HistogramWidget.AxeClear, left=HistogramWidget.AxeLog)
		self.histogramWidget.update()
		self.histogramWidget._histogramItem.delegate = self
		Style.styleWidgetForTab(self.histogramWidget)

		# Invisible item that catches mouse events on top of the histogram
		self.transferfunctionItem = TransferFunctionItem()
		self.transferfunctionItem.setZValue(250)
		self.transferfunctionItem.delegate = self
		self.histogramWidget.addItem(self.transferfunctionItem)

		# Create a widget for editing the selected node of the transfer function
		self.nodeItemWidget = NodeItemWidget()
		self.nodeItemWidget.setEnabled(False)
		self.nodeItemWidget.nodeUpdated.connect(self.updateNode)
		self.nodeItemWidget.removePoint.connect(self.removePoint)

		layout = QGridLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.histogramWidget, 0, 0)
		layout.addWidget(self.nodeItemWidget, 1, 0)
		self.setLayout(layout)

	def setImageData(self, imageData):
		# Clear any previous nodes
		for node in self.nodes:
			self.histogramWidget.scene().removeItem(node)
		self.nodes = []

		# Clear any previous lines
		for line in self.lines:
			self.histogramWidget.scene().removeItem(line)
		self.lines = []

		bins = DataAnalyzer.histogramForData(imageData, 256)
		self.histogram.bins = bins
		self.histogram.enabled = True
		self.range = imageData.GetScalarRange()

		# Create and add nodes from the transfer function
		self.updateNodes()
		self.valueChanged.emit(self)

	def resizeEvent(self, event):
		self.histogramWidget.update()
		self.updateNodes()

	def updateNodes(self):
		for index in range(len(self.transferFunction.points)):
			point = self.transferFunction.points[index]

			if index < len(self.nodes):
				# Just update the node item
				nodeItem = self.nodes[index]
			else:
				# Create a new node item
				nodeItem = TransferFunctionNodeItem()
				nodeItem.setSceneBoundsItem(self.histogramWidget._histogramItem)
				nodeItem.setZValue(300)
				nodeItem.delegate = self
				self.histogramWidget.scene().addItem(nodeItem)
				self.nodes.append(nodeItem)
			nodeItem.setPosition([(point.value - self.range[0]) / (self.range[1] - self.range[0]), point.opacity])
			nodeItem.updateColor(point.color)
			nodeItem.node = point
			if nodeItem.isSelected():
				self.selectedNode(nodeItem)

		# Clean up redundant node items
		if len(self.nodes) > len(self.transferFunction.points):
			# Remove node items from scene
			for index in range(len(self.transferFunction.points), len(self.nodes)):
				nodeItem = self.nodes[index]
				self.histogramWidget.scene().removeItem(nodeItem)

			# Remove them from the nodes
			del self.nodes[len(self.transferFunction.points):]
			assert len(self.nodes) == len(self.transferFunction.points)

		self.updateLines()

	def updateLines(self):
		pen = QPen(QColor.fromHsl(0, 100, 100))
		sortedNodes = sorted(self.nodes, key=lambda x: x.pos().x())
		for index in range(len(self.nodes)-1):
			node = sortedNodes[index]
			nextNode = sortedNodes[index+1]
			if index < len(self.lines):
				# Just update the line segment
				lineItem = self.lines[index]
			else:
				# Create a new line segment
				lineItem = QGraphicsLineItem()
				lineItem.setZValue(250)
				lineItem.setPen(pen)
				self.histogramWidget.scene().addItem(lineItem)
				self.lines.append(lineItem)
			line = QLineF(node.pos(), nextNode.pos())
			lineItem.setLine(line)

		# Clean up redundent lines
		if len(self.lines) >= len(self.nodes):
			# Remove the redundant line segments from the scene
			for index in range(len(self.nodes)-1, len(self.lines)):
				lineItem = self.lines[index]
				self.histogramWidget.scene().removeItem(lineItem)

			# Delete the line segments from the list
			del self.lines[len(self.nodes)-1:]
			assert len(self.lines) == len(self.nodes) - 1

		self.histogramWidget._scene.update()

	def nodeUpdated(self, node):
		position = node.getPosition()
		index = self._indexForNode(node)
		self.transferFunction.updatePointAtIndex(index, position)
		self.nodeItemWidget.setNode(self.transferFunction.points[index])
		self.updateNodes()
		self.valueChanged.emit(self)

	@Slot(object)
	def updateNode(self, point):
		index = self._indexForPoint(point)
		nodeItem = self.nodes[index]
		nodeItem.updateColor(point.color)
		self.transferFunction.updateTransferFunction()
		self.valueChanged.emit(self)

	def selectedNode(self, nodeItem):
		self.nodeItemWidget.setNode(nodeItem.node)

	def addNodeAtCoord(self, coord):
		self.transferFunction.addPointAtCoord(coord, [1, 1, 1])
		self.updateNodes()
		self.valueChanged.emit(self)

	def removePoint(self, point):
		index = self._indexForPoint(point)
		self.transferFunction.removePointAtIndex(index)
		self.updateNodes()

	def unselect(self):
		for node in self.nodes:
			if node.isSelected():
				node.setSelected(False)
		self.nodeItemWidget.setNode(None)
		self.updateNodes()

	def _indexForPoint(self, point):
			for index in range(len(self.transferFunction.points)):
				if point == self.transferFunction.points[index]:
					return index

	def _indexForNode(self, node):
		for index in range(len(self.nodes)):
			if node == self.nodes[index]:
				return index


class NodeItemWidget(QWidget):

	nodeUpdated = Signal(object)
	removePoint = Signal(object)

	def __init__(self):
		super(NodeItemWidget, self).__init__()
		self.node = None

		self.valueEdit = QLineEdit()
		self.opacityEdit = QLineEdit()
		self.colorButton = ColorButton()
		self.colorButton.setMaximumWidth(100)
		self.deleteButton = QPushButton("x")

		layout = QGridLayout()
		layout.addWidget(QLabel("Value:"), 0, 0)
		layout.addWidget(QLabel("Opacity:"), 0, 1)
		layout.addWidget(QLabel("Color:"), 0, 2)
		layout.addWidget(self.valueEdit, 1, 0)
		layout.addWidget(self.opacityEdit, 1, 1)
		layout.addWidget(self.colorButton, 1, 2)
		layout.addWidget(self.deleteButton, 1, 3)

		self.colorButton.clicked.connect(self.showColorDialog)
		self.deleteButton.clicked.connect(self.deleteNode)

		self.setLayout(layout)
		
	def setNode(self, node):
		self.node = node
		if not node:
			self.setEnabled(False)
			self.valueEdit.setText(" ")
			self.opacityEdit.setText(" ")
			self.colorButton.setColor([0.8, 0.8, 0.8])
			return

		self.setEnabled(True)
		self.valueEdit.setText("%.1f" % self.node.value)
		self.opacityEdit.setText("%.3f" % self.node.opacity)
		self.colorButton.setColor(self.node.color)

	def deleteNode(self):
		self.removePoint.emit(self.node)

	def showColorDialog(self):
		color = QColorDialog.getColor()
		if not color.isValid():
			return
		rgba = list(color.getRgbF())
		self.node.color = [rgba[0], rgba[1], rgba[2]]
		self.colorButton.setColor(self.node.color)
		self.nodeUpdated.emit(self.node)
