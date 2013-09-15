"""
MultiVolumeVisualizationFactory

:Authors:
	Berend Klein Haneveld
"""
from multivolumevisualization import MultiVisualizationTypeMix
from multivolumevisualization import MultiVisualizationTypeMIP
from multivolumevisualization import MultiVisualizationTypeMIDA
from multivolumevisualizationmix import MultiVolumeVisualizationMix
from multivolumevisualizationmip import MultiVolumeVisualizationMIP
from multivolumevisualizationmida import MultiVolumeVisualizationMIDA


class MultiVolumeVisualizationFactory(object):
	"""
	MultiVolumeVisualizationFactory can be used to make
	MultiVolumeVisualization objects.
	"""
	def __init__(self):
		super(MultiVolumeVisualizationFactory, self).__init__()

	@classmethod
	def CreateProperty(cls, visualizationType):
		if visualizationType == MultiVisualizationTypeMix:
			return MultiVolumeVisualizationMix()
		elif visualizationType == MultiVisualizationTypeMIP:
			return MultiVolumeVisualizationMIP()
		elif visualizationType == MultiVisualizationTypeMIDA:
			return MultiVolumeVisualizationMIDA()
		else:
			print "Warning: unknown visualizationType given:", visualizationType
			return MultiVolumeVisualizationMix()
			# assert False
