import unittest
import yaml
from ui.visualizations import VolumeVisualizationFactory
from ui.visualizations import VisualizationTypeCT
from ui.visualizations import VisualizationTypeSimple
from ui.visualizations import VolumeVisualizationWrapper
from core.vtkObjectWrapper import vtkVolumePropertyWrapper
from core.vtkObjectWrapper import vtkColorTransferFunctionWrapper
from core.vtkObjectWrapper import vtkPiecewiseFunctionWrapper


class VolumeVisualizationTest(unittest.TestCase):

	def setUp(self):
		self.visualizationCT = VolumeVisualizationFactory.CreateProperty(visualizationType=VisualizationTypeCT)
		self.visualizationSimple = VolumeVisualizationFactory.CreateProperty(visualizationType=VisualizationTypeSimple)

	def tearDown(self):
		del self.visualizationCT

	def testVolumeVisualization(self):
		self.assertTrue(self.visualizationCT is not None)

	def testvtkVolumePropertyWrapper(self):
		self.assertIsNotNone(self.visualizationCT.volProp)

		self.volumePropWrap = vtkVolumePropertyWrapper(self.visualizationCT.volProp)

		self.assertIsNotNone(self.volumePropWrap.independentComponents)
		self.assertIsNotNone(self.volumePropWrap.interpolationType)

	def testvtkVolumePropertyWrapperGetter(self):
		volPropWrapper = vtkVolumePropertyWrapper()
		volPropWrapper.setOriginalObject(self.visualizationCT.volProp)
		vtkVolProp = volPropWrapper.originalObject()
		# Check that it is a vtkVolumeProperty by checking specific vtkVolumeProperty attributes
		self.assertTrue(hasattr(vtkVolProp, "GetIndependentComponents"))
		self.assertEqual(self.visualizationCT.volProp.GetAmbient(), vtkVolProp.GetAmbient())

	def testvtkVolumePropertyWrapperYaml(self):
		volPropWrapper = vtkVolumePropertyWrapper()
		volPropWrapper.setOriginalObject(self.visualizationCT.volProp)

		dump = yaml.dump(volPropWrapper)
		VolumeVisualizationWrapper2 = yaml.load(dump)

		self.assertEqual(volPropWrapper.independentComponents, VolumeVisualizationWrapper2.independentComponents)
		self.assertEqual(volPropWrapper.interpolationType, VolumeVisualizationWrapper2.interpolationType)
		self.assertEqual(volPropWrapper.shade, VolumeVisualizationWrapper2.shade)

	def testvtkColorTransferFunctionWrapper(self):
		self.visualizationCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.visualizationCT.colorFunction)

		self.assertEqual(len(colorFunctionWrapper.nodes), self.visualizationCT.colorFunction.GetSize())

	def testColorTransferFunctionYaml(self):
		self.visualizationCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.visualizationCT.colorFunction)
		dump = yaml.dump(colorFunctionWrapper)
		colorFunctionWrapper2 = yaml.load(dump)

		self.assertEqual(len(colorFunctionWrapper.nodes), len(colorFunctionWrapper2.nodes))

	def testColorTransferFunctionWrapperGetter(self):
		self.visualizationCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.visualizationCT.colorFunction)
		colorFunction = colorFunctionWrapper.originalObject()

		self.assertEqual(len(colorFunctionWrapper.nodes), colorFunction.GetSize())

	def testPiecewiseFunctionWrapper(self):
		self.visualizationSimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper()
		piecewiseFunctionWrapper.setOriginalObject(self.visualizationSimple.opacityFunction)

		self.assertEqual(len(piecewiseFunctionWrapper.nodes), self.visualizationSimple.opacityFunction.GetSize())

	def testPiecewiseFunctionWrapperGetter(self):
		self.visualizationSimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper()
		piecewiseFunctionWrapper.setOriginalObject(self.visualizationSimple.opacityFunction)
		piecewiseFunction = piecewiseFunctionWrapper.originalObject()

		self.assertTrue(piecewiseFunction.GetSize(), self.visualizationSimple.opacityFunction.GetSize())

	def testPiecewiseFunctionWrapperYaml(self):
		self.visualizationSimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper(self.visualizationSimple.opacityFunction)
		dump = yaml.dump(piecewiseFunctionWrapper)
		piecewiseFunctionWrapper2 = yaml.load(dump)

		self.assertEqual(len(piecewiseFunctionWrapper.nodes), len(piecewiseFunctionWrapper2.nodes))

	def testVolumeVisualizationWrapper(self):
		self.visualizationSimple.updateTransferFunction()

		volPropWrapper = VolumeVisualizationWrapper(self.visualizationSimple)

		self.assertEqual(volPropWrapper.visualizationType, VisualizationTypeSimple)
		self.assertIsNotNone(volPropWrapper.volProp)
		self.assertIsNotNone(volPropWrapper.colorFunction)
		self.assertIsNotNone(volPropWrapper.opacityFunction)

		dump = yaml.dump(volPropWrapper)
		volPropWrapper2 = yaml.load(dump)

		self.assertEqual(volPropWrapper.visualizationType, volPropWrapper2.visualizationType)
