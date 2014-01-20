"""
TransformationListView

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QTreeView
from PySide.QtGui import QAbstractItemView


class TransformationListView(QTreeView):
	"""
	TransformationListView
	"""

	def __init__(self):
		super(TransformationListView, self).__init__()

		self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

	def removeSelectedRow(self):
		model = self.model()
		if len(self.selectedIndexes()) > 0:
			index = self.selectedIndexes()[0]
			model.removeTransformationAtIndex(index.row())

	def removeLastRow(self):
		model = self.model()
		model.removeLastTransformation()
