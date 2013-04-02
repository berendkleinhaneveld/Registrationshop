"""
SlicerController

:Authors:
	Berend Klein Haneveld
"""

from UAHCore.UAHViewer.slicer import *
from core.ProjectController import *
from registrationshop import *

class SlicerController(QObject):
	"""
	Class that manages three slicer widgets. Listens to changes of a project
	so that it will update the interface accordingly.
	"""

	def __init__(self, mainSlicer=None, fixedSlicer=None, movingSlicer=None):
		"""
		:type mainSlicer: Slicer
		:type fixedSlicer: Slicer
		:type movingSlicer: Slicer
		"""
		QObject.__init__(self)

		if mainSlicer is None or fixedSlicer is None or movingSlicer is None:
			print "Warning: one of the slicers is none existent"

		self.mainSlicer = mainSlicer
		self.fixedSlicer = fixedSlicer
		self.movingSlicer = movingSlicer

		# TODO: subscribe to changes of the project controller
		self.projectController = RegistrationshopMainWindow.projectController
		self.projectController.currentProject.modified.connect(self.projectChanged)

		self.projectChanged()
#		if self.projectController.currentProject.fixedDataSet() is None:
			# Show button iot load fixed data set
#			self.projectChanged()

	def projectChanged(self):
		"""
		:returns::
		:rtype:
		"""
		print "Project changed"
		project = self.projectController.currentProject
		if project.fixedDataSet() is None:
			self.showFixedButton()
		else:
			self.showFixedData()

		if project.movingDataSet() is None:
			self.showMovingButton()


	def showFixedButton(self):
		# Hide the slicer
		self.fixedSlicer.rwi.setHidden(True)

		# TODO: check to see if parent is not None
		parent = self.fixedSlicer.rwi.parent()
		# Add the button to the base widget
		button = QPushButton("Load fixed data set", parent)
		button.resize(button.sizeHint())
		button.clicked.connect(self.loadFixedDataSet)

	def showFixedData(self):
		self.fixedSlicer.rwi.setHidden(False)

	def showMovingButton(self):
		# Hide the slicer
		self.movingSlicer.rwi.setHidden(True)

		# TODO: check to see if parent is not None
		parent = self.movingSlicer.rwi.parent()
		# Add the button to the base widget
		button = QPushButton("Load moving data set", parent)
		button.resize(button.sizeHint())
		button.clicked.connect(self.loadMovingDataSet)

	def loadFixedDataSet(self):
		fileName, other = QFileDialog.getOpenFileName(self.fixedSlicer.rwi, "Open fixed data set", "", "Images (*.mhd *.vtk)")
		if len(fileName) > 0:
			print "Name:", fileName
			self.projectController.loadFixedDataSet(fileName)

	def loadMovingDataSet(self):
		fileName, other = QFileDialog.getOpenFileName(self.movingSlicer.rwi, "Open moving data set", "", "Images (*.mhd *.vtk)")
		if len(fileName) > 0:
			print "Name:", fileName
			self.projectController.loadMovingDataSet(fileName)
