"""
DataSetsWidget

Holds 2 slicers. Basically a kind of container

author: Berend Klein Haneveld
"""

try:
	from PySide import QtGui, QtCore
	from PySide.QtGui import *
except ImportError:
	raise ImportError("Could not import PySide")
	
from SlicerWidget import *

class DataSetsWidget(QWidget):
	def __init__(self):
		super(DataSetsWidget, self).__init__()
		
		self.fixedDataWidget = SlicerWidget()
		self.movingDataWidget = SlicerWidget()
		
		self.layout = QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		
		self.layout.addWidget(self.movingDataWidget)
		self.layout.addWidget(self.fixedDataWidget)
		
		self.setLayout(self.layout)
		pass