"""
VolumeVisualizationMIP

:Authors:
    Berend Klein Haneveld
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QGroupBox
from PySide6.QtCore import Qt
from vtk import vtkVolumeProperty
from vtk import vtkColorTransferFunction
from vtk import vtkPiecewiseFunction

from .VolumeVisualization import VolumeVisualization
from .VolumeVisualization import VisualizationTypeMIP
from core.decorators import overrides
from ui.widgets.SliderFloatWidget import SliderFloatWidget


class VolumeVisualizationMIP(VolumeVisualization):
    """
    VolumeVisualization subclass for MIP visualization.
    """

    def __init__(self):
        super(VolumeVisualizationMIP, self).__init__()

        self.visualizationType = VisualizationTypeMIP
        self.mapper = None

        # Create property and attach the transfer function
        self.volProp = vtkVolumeProperty()
        self.volProp.SetIndependentComponents(True)
        self.volProp.SetInterpolationTypeToLinear()

    @overrides(VolumeVisualization)
    def getParameterWidget(self):
        """
        Returns a widget with sliders / fields with which properties of this
        volume property can be adjusted.
        :rtype: QWidget
        """
        self.windowSlider = SliderFloatWidget()
        self.windowSlider.setName("Window:")
        self.windowSlider.setRange([0, abs(self.maximum - self.minimum)])
        self.windowSlider.setValue(self.window)
        self.windowSlider.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.windowSlider.valueChanged.connect(self.valueChanged)

        self.levelSlider = SliderFloatWidget()
        self.levelSlider.setName("Level:")
        self.levelSlider.setRange([self.minimum, self.maximum])
        self.levelSlider.setValue(self.level)
        self.levelSlider.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.levelSlider.valueChanged.connect(self.valueChanged)

        self.lowerBoundSlider = SliderFloatWidget()
        self.lowerBoundSlider.setName("Lower:")
        self.lowerBoundSlider.setRange([self.minimum, self.maximum])
        self.lowerBoundSlider.setValue(self.lowerBound)
        self.lowerBoundSlider.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lowerBoundSlider.valueChanged.connect(self.valueChanged)

        self.upperBoundSlider = SliderFloatWidget()
        self.upperBoundSlider.setName("Upper:")
        self.upperBoundSlider.setRange([self.minimum, self.maximum])
        self.upperBoundSlider.setValue(self.upperBound)
        self.upperBoundSlider.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.upperBoundSlider.valueChanged.connect(self.valueChanged)

        windowLevelLayout = QGridLayout()
        windowLevelLayout.setAlignment(Qt.AlignTop)
        windowLevelLayout.setContentsMargins(5, 0, 0, 0)
        windowLevelLayout.setSpacing(0)
        windowLevelLayout.addWidget(self.windowSlider)
        windowLevelLayout.addWidget(self.levelSlider)

        windowLevelGroup = QGroupBox()
        windowLevelGroup.setLayout(windowLevelLayout)

        thresholdLayout = QGridLayout()
        thresholdLayout.setAlignment(Qt.AlignTop)
        thresholdLayout.setContentsMargins(5, 0, 0, 0)
        thresholdLayout.setSpacing(0)
        thresholdLayout.addWidget(self.lowerBoundSlider)
        thresholdLayout.addWidget(self.upperBoundSlider)

        thresholdGroup = QGroupBox("Thresholds:")
        thresholdGroup.setLayout(thresholdLayout)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setHorizontalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(windowLevelGroup)
        layout.addWidget(thresholdGroup)

        widget = QWidget()
        widget.setLayout(layout)

        try:
            from ColumnResizer import ColumnResizer

            self.columnResizer = ColumnResizer()
            self.columnResizer.addWidgetsFromLayout(self.windowSlider.layout(), 0)
            self.columnResizer.addWidgetsFromLayout(self.levelSlider.layout(), 0)
            self.columnResizer.addWidgetsFromLayout(self.lowerBoundSlider.layout(), 0)
            self.columnResizer.addWidgetsFromLayout(self.upperBoundSlider.layout(), 0)

            self.otherColRes = ColumnResizer()
            self.otherColRes.addWidgetsFromLayout(self.windowSlider.layout(), 2)
            self.otherColRes.addWidgetsFromLayout(self.levelSlider.layout(), 2)
            self.otherColRes.addWidgetsFromLayout(self.lowerBoundSlider.layout(), 2)
            self.otherColRes.addWidgetsFromLayout(self.upperBoundSlider.layout(), 2)
        except Exception as e:
            print(e)

        return widget

    @overrides(VolumeVisualization)
    def setImageData(self, imageData):
        if imageData is None:
            self.minimum = 0.0
            self.maximum = 1.0
            self.window = 1.0
            self.level = 0.5
            self.lowerBound = self.minimum
            self.upperBound = self.maximum
            return

        self.minimum, self.maximum = imageData.GetScalarRange()
        self.lowerBound = self.minimum
        self.upperBound = self.maximum
        self.window = self.maximum - self.minimum
        self.level = self.minimum + (self.maximum - self.minimum) * 0.5

    @overrides(VolumeVisualization)
    def setMapper(self, mapper):
        self.mapper = mapper

    @overrides(VolumeVisualization)
    def shaderType(self):
        return 1

    @overrides(VolumeVisualization)
    def updateTransferFunction(self):
        self.colorFunction, self.opacityFunction = CreateRangeFunctions(
            self.minimum,
            self.maximum,
            self.window,
            self.level,
            self.lowerBound,
            self.upperBound,
        )
        self.volProp.SetColor(self.colorFunction)
        self.volProp.SetScalarOpacity(self.opacityFunction)

        lowerBound = (self.lowerBound - self.minimum) / (self.maximum - self.minimum)
        upperBound = (self.upperBound - self.minimum) / (self.maximum - self.minimum)

        if self.mapper:
            self.mapper.SetWindow(self.window)
            self.mapper.SetLevel(self.level)
            self.mapper.SetLowerBound(lowerBound)
            self.mapper.SetUpperBound(upperBound)

        self.updatedTransferFunction.emit()

    @overrides(VolumeVisualization)
    def valueChanged(self, value):
        """
        This method is called when the value of one of the sliders / fields is
        adjusted. Argument value is unused. It is just there so that it can be
        connected to the signals of the interface elements.

        :type value: int
        """
        self.lowerBound = self.lowerBoundSlider.value()
        self.upperBound = self.upperBoundSlider.value()
        self.level = self.levelSlider.value()
        self.window = self.windowSlider.value()

        self.updateTransferFunction()


def CreateRangeFunctions(minimum, maximum, window, level, lowerBound, upperBound):
    """
    :type imageData: vktImageData
    :type color: array of length 3 (r, g, b)
    :rtype: vtkColorTransferFunction, vtkPiecewiseFunction
    """
    minV = level - 0.5 * window
    maxV = level + 0.5 * window

    colorFunction = vtkColorTransferFunction()
    colorFunction.AddRGBSegment(minV, 0, 0, 0, maxV, 1, 1, 1)

    opacityFunction = vtkPiecewiseFunction()
    opacityFunction.AddSegment(minimum - 0.0001, 0.0, lowerBound, 0.0)
    opacityFunction.AddSegment(lowerBound + 0.0001, 1.0, upperBound, 1.0)
    opacityFunction.AddSegment(upperBound + 0.0001, 0.0, maximum + 0.0001, 0.0)

    return colorFunction, opacityFunction
