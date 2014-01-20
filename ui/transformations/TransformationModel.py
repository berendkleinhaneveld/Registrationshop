"""
TransformationModel

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtCore import QAbstractItemModel
from PySide.QtCore import QModelIndex
from PySide.QtCore import Qt
from PySide.QtCore import Slot


class TransformationModel(QAbstractItemModel):
	"""
	TransformationModel
	"""

	def __init__(self):
		super(TransformationModel, self).__init__()

		self.transformations = []
		self.headers = ["Index", "Type"]

	@Slot(object)
	def setTransformations(self, transformations):
		self.transformations = transformations
		self.layoutChanged.emit()

	def removeTransformationAtIndex(self, index):
		del self.transformations[index]
		self.removeRow(index, QModelIndex())

	def removeLastTransformation(self):
		index = len(self.transformations)-1
		if index < 0:
			return
		self.removeTransformationAtIndex(index)

	def index(self, row, column, parent):
		if not self.hasIndex(row, column, parent):
			return self._invalidIndex()

		if column == 0:
			return self.createIndex(row, column, str(row))
		if column == 1:
			return self.createIndex(row, column, str(column))

		return None

	def parent(self, index):
		return self._invalidIndex()

	def rowCount(self, index):
		if index.isValid():
			return 0

		return len(self.transformations)

	def columnCount(self, parent=None):
		return len(self.headers)

	def data(self, index, role):
		if role == Qt.DisplayRole or role == Qt.EditRole:
			transformation = self.transformations[index.row()]
			if index.column() == 0:
				return str(index.row() + 1)
			elif index.column() == 1:
				return transformation.transformType

		return None

	def flags(self, index):
		if not index.isValid():
			return Qt.NoItemFlags
		return (Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
			| Qt.ItemIsDropEnabled)

	def removeRows(self, row, count, parent):
		self.beginRemoveRows(parent, row, row+count-1)
		self.endRemoveRows()
		return True

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self.headers[section]

		return None

	def _invalidIndex(self):
		return self.createIndex(-1, -1, None)
