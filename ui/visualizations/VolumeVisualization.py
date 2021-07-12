"""
VolumeVisualization

:Authors:
    Berend Klein Haneveld
"""
from PySide.QtCore import Signal
from PySide.QtCore import QObject
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction

# Define Render Types
# TODO: Render types are not suited for visualization names
# If name is changed, then the visualization of older projec
VisualizationTypeSimple = "Threshold"
VisualizationTypeGray = "Gray scale"
VisualizationTypeCT = "CT"
VisualizationTypeMIP = "MIP"
VisualizationTypeMIDA = "MIDA"
VisualizationTypeRamp = "Ramp"
VisualizationTypeTransferFunction = "Transfer function"

VolumePropKey = "VolumeVisualization"
VisualizationTypeKey = "VisualizationTypeKey"
ColorFuncKey = "ColorFuncKey"
TransFuncKey = "TransFuncKey"


# Volume properties


class VolumeVisualization(QObject):
    """
    VolumeVisualization is an interface class for the different render types
    """

    updatedTransferFunction = Signal()

    def __init__(self):
        super(VolumeVisualization, self).__init__()

        self.volProp = None
        self.visualizationType = None

    def getParameterWidget(self):
        """
        This method should be overridden in the subclasses.
        :rtype: QWidget
        """
        raise NotImplementedError()

    def setImageData(self, imageData):
        """
        This method should be overridden in the subclasses.
        :type imageData: vtkImageData
        """
        raise NotImplementedError()

    def setMapper(self, mapper):
        raise NotImplementedError()

    def shaderType(self):
        raise NotImplementedError()

    def updateTransferFunction(self):
        raise NotImplementedError()

    def valueChanged(self, value):
        raise NotImplementedError()


def CreateRangeFunctions(imageData, color=None):
    """
    :type imageData: vktImageData
    :type color: array of length 3 (r, g, b)
    :rtype: vtkColorTransferFunction, vtkPiecewiseFunction
    """
    col = [1, 1, 1]
    if color is not None:
        col = color
    minimum, maximum = imageData.GetScalarRange()
    colorFunction = vtkColorTransferFunction()
    colorFunction.AddRGBSegment(minimum, 0, 0, 0, maximum, col[0], col[1], col[2])

    opacityFunction = vtkPiecewiseFunction()
    opacityFunction.AddSegment(minimum, 0.0, maximum, 1.0)

    return colorFunction, opacityFunction
