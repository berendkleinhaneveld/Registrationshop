"""
TransferFunctionEditor

:Authors:
	Berend Klein Haneveld
"""
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction
from PySide.QtCore import QObject


class TransferFunction(QObject):
	"""
	TransferFunction.
	"""

	def __init__(self):
		super(TransferFunction, self).__init__()

		self.points = []
		self.range = [0.0, 100.0]
		self.opacityFunction = None
		self.colorFunction = None

	def setRange(self, range):
		"""
		Resets all the points and creates the default range function.
		"""
		self.range = range
		self.points = []
		self.addPointAtCoord([0, 0], [0, 0, 0])
		self.addPointAtCoord([1, 1], [1, 1, 1])

	def addPointAtCoord(self, coord, color=[0.0, 0.0, 0.0]):
		value = self.range[0] + coord[0] * (self.range[1] - self.range[0])
		opacity = coord[1]
		self.addPoint(value, opacity, color)

	def addPoint(self, value, opacity, color=[0.0, 0.0, 0.0]):
		point = Point()
		point.value = value
		point.color = color
		point.opacity = opacity
		self.points.append(point)

	def updatePointAtIndex(self, index, coord):
		self.points[index].value = coord[0] * (self.range[1] - self.range[0]) + self.range[0]
		self.points[index].opacity = coord[1]

	def removePointAtIndex(self, index):
		if len(self.points) > 2:
			del self.points[index]

	def setPoints(self, points):
		self.points = points
		self.updateTransferFunction()

	def updateTransferFunction(self):
		if not self.colorFunction or not self.opacityFunction:
			self.colorFunction = vtkColorTransferFunction()
			self.opacityFunction = vtkPiecewiseFunction()

		points = sorted(self.points, key=lambda x: x.value)

		nrOfPoints = self.colorFunction.GetSize()
		index = 0
		for point in points:
			if index >= nrOfPoints:
				self.colorFunction.AddRGBPoint(point.value, point.color[0], point.color[1], point.color[2])
				self.opacityFunction.AddPoint(point.value, pow(point.opacity, 5))
			else:
				self.colorFunction.SetNodeValue(index, [point.value] + point.color + [0.5, 0.0])
				self.opacityFunction.SetNodeValue(index, [point.value, pow(point.opacity, 5), 0.5, 0.0])
			index += 1

		if nrOfPoints > len(points):
			self.colorFunction.AdjustRange([points[0].value, points[-1].value])
			assert self.colorFunction.GetSize() == len(points)


class Point(object):
	"""
	Point
	"""

	def __init__(self):
		super(Point, self).__init__()

		self.value = 0.0
		self.color = [0.0, 0.0, 0.0]
		self.opacity = 0.0
