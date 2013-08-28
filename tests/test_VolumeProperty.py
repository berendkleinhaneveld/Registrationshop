import unittest
import yaml
from ui.VolumeVisualization import VolumeVisualizationFactory
from ui.VolumeVisualization import VisualizationTypeCT
from ui.VolumeVisualization import VisualizationTypeSimple
from core.vtkObjectWrapper import vtkVolumePropertyWrapper
from core.vtkObjectWrapper import vtkColorTransferFunctionWrapper
from core.vtkObjectWrapper import vtkPiecewiseFunctionWrapper
from ui.VolumeVisualization import VolumeVisualizationObjectWrapper


class VolumeVisualizationTest(unittest.TestCase):

	def setUp(self):
		self.VolumeVisualizationCT = VolumeVisualizationFactory.CreateProperty(visualizationType=VisualizationTypeCT)
		self.VolumeVisualizationSimple = VolumeVisualizationFactory.CreateProperty(visualizationType=VisualizationTypeSimple)

	def tearDown(self):
		del self.VolumeVisualizationCT

	def testVolumeVisualization(self):
		self.assertTrue(self.VolumeVisualizationCT is not None)

	def testvtkVolumePropertyWrapper(self):
		self.assertIsNotNone(self.VolumeVisualizationCT.VolumeVisualization)

		self.volumePropWrap = vtkVolumePropertyWrapper(self.VolumeVisualizationCT.VolumeVisualization)

		self.assertIsNotNone(self.volumePropWrap.independentComponents)
		self.assertIsNotNone(self.volumePropWrap.interpolationType)

	def testvtkVolumePropertyWrapperGetter(self):
		volPropWrapper = vtkVolumePropertyWrapper()
		volPropWrapper.setOriginalObject(self.VolumeVisualizationCT.VolumeVisualization)
		vtkVolProp = volPropWrapper.originalObject()
		# Check that it is a vtkVolumeProperty by checking specific vtkVolumeProperty attributes
		self.assertTrue(hasattr(vtkVolProp, "GetIndependentComponents"))
		self.assertEqual(self.VolumeVisualizationCT.VolumeVisualization.GetAmbient(), vtkVolProp.GetAmbient())

	def testvtkVolumePropertyWrapperYaml(self):
		volPropWrapper = vtkVolumePropertyWrapper()
		volPropWrapper.setOriginalObject(self.VolumeVisualizationCT.VolumeVisualization)

		dump = yaml.dump(volPropWrapper)
		VolumeVisualizationWrapper2 = yaml.load(dump)

		self.assertEqual(volPropWrapper.independentComponents, VolumeVisualizationWrapper2.independentComponents)
		self.assertEqual(volPropWrapper.interpolationType, VolumeVisualizationWrapper2.interpolationType)
		self.assertEqual(volPropWrapper.shade, VolumeVisualizationWrapper2.shade)

	def testvtkColorTransferFunctionWrapper(self):
		self.VolumeVisualizationCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.VolumeVisualizationCT.colorFunction)

		self.assertEqual(len(colorFunctionWrapper.nodes), self.VolumeVisualizationCT.colorFunction.GetSize())

	def testColorTransferFunctionYaml(self):
		self.VolumeVisualizationCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.VolumeVisualizationCT.colorFunction)
		dump = yaml.dump(colorFunctionWrapper)
		colorFunctionWrapper2 = yaml.load(dump)

		self.assertEqual(len(colorFunctionWrapper.nodes), len(colorFunctionWrapper2.nodes))

	def testColorTransferFunctionWrapperGetter(self):
		self.VolumeVisualizationCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.VolumeVisualizationCT.colorFunction)
		colorFunction = colorFunctionWrapper.originalObject()

		self.assertEqual(len(colorFunctionWrapper.nodes), colorFunction.GetSize())

	def testPiecewiseFunctionWrapper(self):
		self.VolumeVisualizationSimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper()
		piecewiseFunctionWrapper.setOriginalObject(self.VolumeVisualizationSimple.opacityFunction)

		self.assertEqual(len(piecewiseFunctionWrapper.nodes), self.VolumeVisualizationSimple.opacityFunction.GetSize())

	def testPiecewiseFunctionWrapperGetter(self):
		self.VolumeVisualizationSimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper()
		piecewiseFunctionWrapper.setOriginalObject(self.VolumeVisualizationSimple.opacityFunction)
		piecewiseFunction = piecewiseFunctionWrapper.originalObject()

		self.assertTrue(piecewiseFunction.GetSize(), self.VolumeVisualizationSimple.opacityFunction.GetSize())

	def testPiecewiseFunctionWrapperYaml(self):
		self.VolumeVisualizationSimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper(self.VolumeVisualizationSimple.opacityFunction)
		dump = yaml.dump(piecewiseFunctionWrapper)
		piecewiseFunctionWrapper2 = yaml.load(dump)

		self.assertEqual(len(piecewiseFunctionWrapper.nodes), len(piecewiseFunctionWrapper2.nodes))

	def testVolumeVisualizationWrapper(self):
		self.VolumeVisualizationSimple.updateTransferFunction()

		volPropWrapper = VolumeVisualizationObjectWrapper(self.VolumeVisualizationSimple)

		self.assertEqual(volPropWrapper.visualizationType, VisualizationTypeSimple)
		self.assertIsNotNone(volPropWrapper.VolumeVisualization)
		self.assertIsNotNone(volPropWrapper.colorFunction)
		self.assertIsNotNone(volPropWrapper.opacityFunction)

		dump = yaml.dump(volPropWrapper)
		volPropWrapper2 = yaml.load(dump)

		self.assertEqual(volPropWrapper.visualizationType, volPropWrapper2.visualizationType)
