"""
ParameterModel

:Authors:
	Berend Klein Haneveld
"""
from PySide.QtCore import QAbstractItemModel
from PySide.QtCore import QModelIndex
from PySide.QtCore import Qt
from PySide.QtCore import Slot
from core.elastix import Parameter
from core.elastix import ParameterList


class ParameterModel(QAbstractItemModel):
	"""
	Model for parameters to be viewed in a view
	"""

	def __init__(self):
		super(ParameterModel, self).__init__()

		self.parameters = []
		self.headers = ["Parameter", "Value"]
	
	# Public interface functions

	def setParameters(self, parameters):
		"""
		The parameter value should be a list of Parameter items.
		The use of a dictionary has no use here, because a dictionary
		has no fixed ordering.

		:type parameters: list
		"""
		self.parameters = parameters
		self.layoutChanged.emit()

	def addParameter(self):
		"""
		Add a standard parameter to the end of the list.
		"""
		standardParameter = Parameter("ParameterName", "Value")
		self.parameters.append(standardParameter)
		self.insertRows(len(self.parameters), 1, QModelIndex())

	def removeParameterAtIndex(self, index):
		"""
		:type index: int
		"""
		del self.parameters[index]
		self.removeRow(index, QModelIndex())

	@Slot(ParameterList)
	def setTransformation(self, transformation):
		"""
		:type transformation: ParameterList
		"""
		self.setParameters(transformation.parameters)

	# Functions needed for read only behaviour

	def index(self, row, column, parent):
		"""
		:type row: int
		:type column: int
		:type parent: QModelIndex
		:rtype: QModelIndex
		"""
		#If the model does not have this index
		if not self.hasIndex(row, column, parent):
			return self.invalidIndex()

		if column == 0:
			return self.createIndex(row, column, str(self.parameters[row].key()))
		if column == 1:
			return self.createIndex(row, column, str(self.parameters[row].value()))

		return None

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

		return len(self.parameters)

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
			parameter = self.parameters[index.row()]
			if index.column() == 0:
				return str(parameter.key())
			if index.column() == 1:
				return str(parameter.value())
		
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

		parameter = self.parameters[index.row()]
		if index.column() == 0:
			parameter.setKey(value)
		elif index.column() == 1:
			parameter.setValue(value)

		self.dataChanged.emit(index, index)
		self.layoutChanged.emit()
		return True

	def flags(self, index):
		if not index.isValid():
			return Qt.NoItemFlags
		return (Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
			| Qt.ItemIsDropEnabled | Qt.ItemIsEditable)

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
