
from PySide.QtGui import QTreeView
from PySide.QtCore import Signal
from core.Transformation import Transformation

class TransformationListView(QTreeView):
	"""docstring for TransformationListView"""

	# Signals
	selectedTransformation = Signal(Transformation)

	def __init__(self):
		super(TransformationListView, self).__init__()
		
		pass

	def selectionChanged(self, selected, deselected):
		"""
		Emit a signal when the selection has changed
		"""
		if len(selected.indexes()) > 0:
			index = selected.indexes()[0]
			transformation = index.internalPointer()
			self.selectedTransformation.emit(transformation)

	def addTransformation(self):
		"""
		Adds a transformation to the model
		"""
		model = self.model()
		model.addTransformation()
		pass

	def removeSelectedTransformation(self):
		"""
		Removes the selected transformation
		"""
		model = self.model()
		for index in self.selectedIndexes():
			model.removeTransformationAtIndex(index)
