"""
MultiVolumeVisualizationFactory

:Authors:
    Berend Klein Haneveld
"""
from .MultiVolumeVisualization import (
    MultiVisualizationTypeMIDA,
    MultiVisualizationTypeMIP,
    MultiVisualizationTypeMix,
)
from .MultiVolumeVisualizationMIDA import MultiVolumeVisualizationMIDA
from .MultiVolumeVisualizationMIP import MultiVolumeVisualizationMIP
from .MultiVolumeVisualizationMix import MultiVolumeVisualizationMix


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
            print("Warning: unknown visualizationType given:", visualizationType)
            return MultiVolumeVisualizationMix()
            # assert False
