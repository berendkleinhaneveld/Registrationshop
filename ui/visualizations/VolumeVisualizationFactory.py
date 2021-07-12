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
from VolumeVisualization import VisualizationTypeTransferFunction
from VolumeVisualizationSimple import VolumeVisualizationSimple
from VolumeVisualizationCT import VolumeVisualizationCT
from VolumeVisualizationMIP import VolumeVisualizationMIP
from VolumeVisualizationMIDA import VolumeVisualizationMIDA
from VolumeVisualizationRamp import VolumeVisualizationRamp
from VolumeVisualizationTransferFunction import VolumeVisualizationTransferFunction


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
        elif visualizationType == VisualizationTypeTransferFunction:
            return VolumeVisualizationTransferFunction()
        else:
            print(visualizationType)
            assert False
