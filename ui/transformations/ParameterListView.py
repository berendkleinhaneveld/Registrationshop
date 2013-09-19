"""
ParameterListView

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QTreeView
from PySide.QtGui import QAbstractItemView


class ParameterListView(QTreeView):
	"""
	List view of the parameters of a transformation.
	"""

	def __init__(self):
		super(ParameterListView, self).__init__()

		self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

	# Public methods

	def addParameter(self):
		model = self.model()
		model.addParameter()

	def removeSelectedParameter(self):
		model = self.model()

		if len(self.selectedIndexes()) > 0:
			index = self.selectedIndexes()[0]
			model.removeParameterAtIndex(index.row())

	# Overriden methods

	def resizeEvent(self, event):
		"""
		:type event: QResizeEvent
		"""
		size = event.size()
		width = size.width()
		widthOfFirstColumn = int(2.0/3.0 * width)
		
		self.setColumnWidth(0, widthOfFirstColumn)
		self.setColumnWidth(1, width - widthOfFirstColumn)
