"""
TransformationHistoryWidget

:Authors:
	Berend Klein Haneveld
"""

from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QVBoxLayout
from PySide.QtCore import Qt

class TransformationHistoryWidget(QWidget):
	"""
	TransformationHistoryWidget shows a list of applied transformations.
	"""
	def __init__(self):
		super(TransformationHistoryWidget, self).__init__()

		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("History of transformations."))
		self.setLayout(layout)
		
