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

		# Connect the project controller to the widgets so that when
		# one of the widgets loads a new data set it is loaded into
		# the current project
		projectController = ProjectController.Instance()
		self.fixedDataWidget.loadedFileName.connect(projectController.loadFixedDataSet)
		self.movingDataWidget.loadedFileName.connect(projectController.loadMovingDataSet)
		
		# Connect the widgets to the project controller so that when the 
		# project controller has set the new filename, it gets passed through
		# to the slicer widgets so they can load their data
		projectController.changedFixedData.connect(self.fixedDataWidget.setFileName)
		projectController.changedMovingData.connect(self.movingDataWidget.setFileName)

		# Create horizontal layout so the slicer widgets are next to eachother
		self.layout = QHBoxLayout()
		self.layout.setSpacing(2)
		self.layout.setContentsMargins(0, 0, 0, 0)

		self.layout.addWidget(self.fixedDataWidget)
		self.layout.addWidget(self.movingDataWidget)
		
		self.setLayout(self.layout)
