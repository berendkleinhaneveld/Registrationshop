"""
TransformationModel

:Authors:
	Berend Klein Haneveld
"""
from core.Transformation import Transformation
from PySide.QtCore import Qt
from PySide.QtCore import QAbstractItemModel
from PySide.QtCore import QModelIndex

from core.AppVars import AppVars

class TransformationModel(QAbstractItemModel):
	"""
	TransformationModel that wraps around a collection of transformations.

	TODO: should be connected to Strategy class, instead of using a simple list
	to keep track of transformations.
	"""

	def __init__(self):
		super(TransformationModel, self).__init__()
		
		self.headers = ["Name"]
		self.transformations = []

	# Public interface functions

	def addTransformation(self):
		"""
		Adds transformation at the end of the list
		"""
		transformation = Transformation()
		transformation.loadFromFile(AppVars.transformationsPath() + "/Default B-spline.c")
		self.transformations.append(transformation)
		self.insertRows(len(self.transformations), 1, QModelIndex())

	def removeTransformationAtIndex(self, index):
		"""
		:type index: QModelIndex
		"""
		del self.transformations[index.row()]
		self.removeRow(index.row(), self.parent(None))

	# Functions needed for read only behaviour

	def index(self, row, column, parent):
		"""
		:type row: int
		:type column: int
		:type parent: QModelIndex
		:rtype: QModelIndex
		"""
		if row < 0 or row >= len(self.transformations):
			return self.invalidIndex()
			
		ind = self.createIndex(row, column, self.transformations[row])

		return ind

	def parent(self, index):
		"""
		:type index: QModelIndex
		:rtype: QModelIndex
		"""
		return self.invalidIndex()

	def rowCount(self, index):
		"""
		:type parent: QModelIndex
		:rtype: int
		"""
		if index.isValid():
			return 0
		
		return len(self.transformations)

	def columnCount(self, parent=None):
		"""
		:type parent: QModelIndex
		:rtype: int
		"""
		return len(self.headers)

	def data(self, index, role):
		"""
		:type index: QModelIndex
		:type role: Qt.ItemDataRole
		:rtype: QVariant
		"""
		if role == Qt.DisplayRole or role == Qt.EditRole:
			transform = index.internalPointer()
			return transform.name
		else:
			return None

	# Functions needed for editing

	def setData(self, index, value, role):
		"""
		:type index: QModelIndex
		:type value: QVariant
		:type role: Qt.ItemDataRole
		:rtype: bool
		"""
		if not role == Qt.EditRole:
			return False

		self.transformations[index.row()].name = value
		self.dataChanged.emit(index, index)
		return True

	def flags(self, index):
		"""
		:type index: QModelIndex
		:rtype: int
		"""
		if not index.isValid():
			return Qt.ItemIsEnabled
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled \
			| Qt.ItemIsDropEnabled | Qt.ItemIsEditable

	def insertRows(self, row, count, parent):
		"""
		:type row: int
		:type count: int
		:type parent: QModelIndex
		:rtype: bool
		"""
		self.beginInsertRows(parent, row, row+count-1)
		self.endInsertRows()
		return True

	def removeRows(self, row, count, parent):
		"""
		:type row: int
		:type count: int
		:type parent: QModelIndex
		:rtype: bool
		"""
		self.beginRemoveRows(parent, row, row+count-1)
		self.endRemoveRows()
		return True

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		"""
		:type section: int
		:type orientation: Qt.Orientation
		"""
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self.headers[section]

		return None

	def invalidIndex(self):
		"""
		Convenience method for creating an invalid QModelIndex object 
		for use in some methods.
		
		:rtype: QModelIndex
		"""
		return self.createIndex(-1, -1, None)

