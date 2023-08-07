"""
VolumeVisualizationFactory

:Authors:
    Berend Klein Haneveld
"""
from .VolumeVisualization import (
    VisualizationTypeCT,
    VisualizationTypeMIDA,
    VisualizationTypeMIP,
    VisualizationTypeRamp,
    VisualizationTypeSimple,
    VisualizationTypeTransferFunction,
)
from .VolumeVisualizationCT import VolumeVisualizationCT
from .VolumeVisualizationMIDA import VolumeVisualizationMIDA
from .VolumeVisualizationMIP import VolumeVisualizationMIP
from .VolumeVisualizationRamp import VolumeVisualizationRamp
from .VolumeVisualizationSimple import VolumeVisualizationSimple
from .VolumeVisualizationTransferFunction import VolumeVisualizationTransferFunction


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
