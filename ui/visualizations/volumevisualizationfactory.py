"""
VolumeVisualizationFactory

:Authors:
	Berend Klein Haneveld
"""
from volumevisualization import VisualizationTypeSimple
from volumevisualization import VisualizationTypeCT
from volumevisualization import VisualizationTypeMIP
from volumevisualization import VisualizationTypeRamp
from volumevisualizationsimple import VolumeVisualizationSimple
from volumevisualizationct import VolumeVisualizationCT
from volumevisualizationmip import VolumeVisualizationMIP
from volumevisualizationramp import VolumeVisualizationRamp


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
		else:
			assert False
