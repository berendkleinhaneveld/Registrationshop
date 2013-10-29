"""
DataAnalyzer

:Authors:
	Berend Klein Haneveld
"""


class DataAnalyzer(object):
	"""
	DataAnalyzer
	"""

	def __init__(self):
		super(DataAnalyzer, self).__init__()

	@classmethod
	def histogramForData(cls, data, nrBins):
		"""
		Samples the image data in order to create bins
		for making a histogram of the data.
		"""
		dims = data.GetDimensions()
		minVal, maxVal = data.GetScalarRange()
		bins = [0 for x in range(nrBins)]

		stepSize = 3
		for z in range(0, dims[2], stepSize):
			for y in range(0, dims[1], stepSize):
				for x in range(0, dims[0], stepSize):
					element = data.GetScalarComponentAsFloat(x, y, z, 0)
					index = int(((element - minVal) / float(maxVal - minVal)) * (nrBins-1))
					bins[index] += 1

		return bins
