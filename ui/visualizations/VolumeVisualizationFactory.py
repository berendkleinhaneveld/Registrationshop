"""
VolumeVisualizationFactory

:Authors:
	Berend Klein Haneveld
"""
from VolumeVisualization import VisualizationTypeSimple
from VolumeVisualization import VisualizationTypeCT
from VolumeVisualization import VisualizationTypeMIP
from VolumeVisualization import VisualizationTypeMIDA
from VolumeVisualization import VisualizationTypeRamp
from VolumeVisualizationSimple import VolumeVisualizationSimple
from VolumeVisualizationCT import VolumeVisualizationCT
from VolumeVisualizationMIP import VolumeVisualizationMIP
from VolumeVisualizationMIDA import VolumeVisualizationMIDA
from VolumeVisualizationRamp import VolumeVisualizationRamp


# Factory
class VolumeVisualizationFactory(object):
	"""
	VolumeVisualizationFactory makes and creates proper VolumeVisualization objects.
	"""

	@classmethod
	def CreateProperty(cls, visualizationType):
		if visualizationType == VisualizationTypeSimple:
			return VolumeVisualizationSimple()
		elif visualizationType == VisualizationTypeCT:
			return VolumeVisualizationCT()
		elif visualizationType == VisualizationTypeMIP:
			return VolumeVisualizationMIP()
		elif visualizationType == VisualizationTypeRamp:
			return VolumeVisualizationRamp()
		elif visualizationType == VisualizationTypeMIDA:
			return VolumeVisualizationMIDA()
		else:
			print visualizationType
			assert False
