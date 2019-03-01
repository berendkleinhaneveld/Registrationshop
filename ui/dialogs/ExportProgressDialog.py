"""
ExportProgressDialog

:Authors:
	Berend Klein Haneveld 2013
"""

from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QGridLayout
from PySide2.QtWidgets import QProgressBar
from PySide2.QtWidgets import QLabel


class ExportProgressDialog(QDialog):
	"""
	ExportProgressDialog is a dialog that
	shows a progress bar or busy indicator
	"""
	def __init__(self, parent, message):
		super(ExportProgressDialog, self).__init__(parent)

		self.setModal(True)
		self.setWindowTitle(message)

		indicator = QProgressBar()
		indicator.setMinimum(0)
		indicator.setMaximum(0)

		messageLabel = QLabel(message)

		layout = QGridLayout()
		layout.addWidget(messageLabel)
		layout.addWidget(indicator)
		self.setLayout(layout)
