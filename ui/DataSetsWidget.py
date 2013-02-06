"""
DataSetsWidget

Holds 2 slicers. Basically a kind of container

author: Berend Klein Haneveld
"""

try:
	from PySide.QtGui import QWidget
	from PySide.QtGui import QHBoxLayout
except ImportError:
	raise ImportError("Could not import PySide")
	
from SlicerWidget import SlicerWidget
from core.ProjectController import ProjectController

class DataSetsWidget(QWidget):
	def __init__(self):
		"""
		Initializes the UI.
		"""
		super(DataSetsWidget, self).__init__()
		
		self.fixedDataWidget = SlicerWidget("Fixed data set")
		self.movingDataWidget = SlicerWidget("Moving data set")

		projectController = ProjectController.Instance()
		self.fixedDataWidget.loadedFileName.connect(projectController.loadFixedDataSetFileName)
		self.movingDataWidget.loadedFileName.connect(projectController.loadMovingDataSetFileName)
		
		self.layout = QHBoxLayout()
		self.layout.setSpacing(2)
		self.layout.setContentsMargins(0, 0, 0, 0)

		self.layout.addWidget(self.fixedDataWidget)
		self.layout.addWidget(self.movingDataWidget)
		
		self.setLayout(self.layout)
		pass
