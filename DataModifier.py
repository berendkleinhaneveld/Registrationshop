#!/usr/local/bin/python
"""
ImageDataResizer

:Authors:
	Berend Klein Haneveld
"""
import sys
from PySide.QtGui import QApplication
from PySide.QtGui import QMainWindow
from PySide.QtGui import QWidget
from PySide.QtGui import QLineEdit
from PySide.QtGui import QPushButton
from PySide.QtGui import QLabel
from PySide.QtGui import QGridLayout
from PySide.QtGui import QDoubleValidator
from PySide.QtGui import QFileDialog
from PySide.QtCore import Qt
from PySide.QtCore import Slot

from ui.MainWindow import MainWindow
from ui.parameters.RenderInfoWidget import RenderInfoWidget
from core.data.DataReader import DataReader
from core.data.DataResizer import DataResizer
from core.data.DataWriter import DataWriter

# Define settings parameters
APPNAME = "Image Data Resampler"
ORGNAME = "Delft"
ORGDOMAIN = "student.tudelft.nl"


class ImageDataResizer(MainWindow):
	def __init__(self, args):
		super(ImageDataResizer, self).__init__(args)

		self.fileName = None
		# Initialize the user interface
		self.initUI()

	def initUI(self):
		self.createElements()
		self.statusBar = self.statusBar()
		self.statusBar.setSizeGripEnabled(False)

		# Set some window/application properties
		self.setUnifiedTitleAndToolBarOnMac(True)
		self.setWindowTitle(APPNAME)
		self.setWindowState(Qt.WindowActive)

	def createElements(self):
		self.mainWindow = QMainWindow()
		self.inputLabel = QLabel("")
		self.datasetInfo = RenderInfoWidget()
		self.inputButton = QPushButton("Load file")
		self.factorLine = QLineEdit()
		self.factorLine.setValidator(QDoubleValidator())
		self.outputButton = QPushButton("Export file")

		self.inputButton.clicked.connect(self.setInputFile)
		self.outputButton.clicked.connect(self.exportToFile)

		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		layout.addWidget(QLabel("Input file"), 0, 0)
		layout.addWidget(self.inputButton, 0, 1)
		layout.addWidget(self.datasetInfo, 1, 1, 1, 2)
		layout.addWidget(QLabel("Scale factor"), 2, 0)
		layout.addWidget(self.factorLine, 2, 1)
		layout.addWidget(self.outputButton, 3, 1)

		self.centralWidget = QWidget()
		self.centralWidget.setLayout(layout)
		self.setCentralWidget(self.centralWidget)

	@Slot()
	def setInputFile(self):
		dataReader = DataReader()
		extensions = dataReader.GetSupportedExtensionsAsString()
		fileName, other = QFileDialog.getOpenFileName(self, "Open data set", "", "Images ("+extensions+")", options=QFileDialog.Directory)
		if len(fileName) > 0:
			self.fileName = fileName
			self.datasetInfo.setFile(self.fileName)

	@Slot()
	def exportToFile(self):
		if not self.fileName:
			self.statusBar.showMessage("Please set an input file.")
			return

		if len(self.factorLine.text()) == 0:
			self.statusBar.showMessage("Please set a scale factor.")
			return

		if float(self.factorLine.text()) > 1.0:
			self.statusBar.showMessage("Cannot enlarge datasets.")
			return

		if float(self.factorLine.text()) < 0.0:
			self.statusBar.showMessage("You trying to be funny?")

		self.statusBar.clearMessage()

		dataWriter = DataWriter()
		extensions = dataWriter.GetSupportedExtensionsAsString()
		exportFileName, other = QFileDialog.getSaveFileName(self, "Export resampled data", "", "Images ("+extensions+")")
		if len(exportFileName) > 0:
			self.statusBar.setVisible(True)

			factor = float(self.factorLine.text())

			self.statusBar.showMessage("Reading...")
			dataReader = DataReader()
			imageData = dataReader.GetImageData(self.fileName)

			self.statusBar.showMessage("Resizing...")
			dataResizer = DataResizer()
			resizedData = dataResizer.ResizeData(imageData, factor)

			self.statusBar.showMessage("Writing...")
			dataWriter.WriteToFile(resizedData, exportFileName, DataReader.TypeMHA)

			self.statusBar.showMessage("Done.")


def main():
	app = QApplication(sys.argv)
	app.setObjectName(APPNAME)
	app.setApplicationName(APPNAME)
	app.setOrganizationName(ORGNAME)
	app.setOrganizationDomain(ORGDOMAIN)

	mainWindow = ImageDataResizer(sys.argv)
	mainWindow.raise_()
	mainWindow.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

# if __name__ == '__main__':
# 	fileName = "/Users/beer/Registrationshop/Data/Medical/Noeska/CT.mhd"
# 	exportName = "/Users/beer/Registrationshop/Data/Medical/Noeska/CTQuarter.mhd"
# 	scale = 0.01

# 	print "reading"
# 	dataReader = DataReader()
# 	imageData = dataReader.GetImageData(fileName)

# 	print "resizing"
# 	dataResizer = DataResizer()
# 	resizedData = dataResizer.ResizeData(imageData, scale)

# 	print "writing"
# 	dataWriter = DataWriter()
# 	dataWriter.WriteToFile(resizedData, exportName, DataReader.TypeMHA)
