"""
FileTypeDialog

:Authors:
	Berend Klein Haneveld 2013
"""

from PySide.QtGui import QDialog
from PySide.QtGui import QPushButton
from PySide.QtGui import QGridLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Slot
from core.data import DataReader


class FileTypeDialog(QDialog):
	"""Custom dialog that shows some file type options."""
	def __init__(self, parent):
		super(FileTypeDialog, self).__init__(parent)
		self.result = None

	@Slot()
	def _mhdButtonClicked(self):
		self.result = DataReader.TypeMHD
		self.accept()

	@Slot()
	def _vtiButtonClicked(self):
		self.result = DataReader.TypeVTI
		self.accept()

	@classmethod
	def getFileType(cls, parent, title):
		widget = FileTypeDialog(parent)
		widget.setModal(True)

		mhdButton = QPushButton("MHD")
		mhdButton.clicked.connect(widget._mhdButtonClicked)
		vtiButton = QPushButton("VTI")
		vtiButton.clicked.connect(widget._vtiButtonClicked)

		layout = QGridLayout()
		layout.addWidget(QLabel("Choose file format:"), 0, 0, 1, 2)
		layout.addWidget(mhdButton, 1, 0)
		layout.addWidget(vtiButton, 1, 1)

		widget.setLayout(layout)
		result = widget.exec_()
		if result == QDialog.Accepted:
			return widget.result
		return ""
