import unittest
import yaml
from ui.VolumeProperty import VolumePropertyFactory
from ui.VolumeProperty import RenderTypeCT
from ui.VolumeProperty import RenderTypeSimple
from ui.VolumeProperty import VolumeProperty
from core.vtkObjectWrapper import vtkVolumePropertyWrapper
from core.vtkObjectWrapper import vtkColorTransferFunctionWrapper
from core.vtkObjectWrapper import vtkPiecewiseFunctionWrapper
from ui.VolumeProperty import VolumePropertyObjectWrapper

class VolumePropertyTest(unittest.TestCase):

	def setUp(self):
		self.volumePropertyCT = VolumePropertyFactory.CreateProperty(renderType=RenderTypeCT)
		self.volumePropertySimple = VolumePropertyFactory.CreateProperty(renderType=RenderTypeSimple)

	def tearDown(self):
		del self.volumePropertyCT

	def testVolumeProperty(self):
		self.assertTrue(self.volumePropertyCT is not None)

	def testVtkVolumePropertyWrapper(self):
		self.assertIsNotNone(self.volumePropertyCT.volumeProperty)

		self.volumePropWrap = vtkVolumePropertyWrapper(self.volumePropertyCT.volumeProperty)

		self.assertIsNotNone(self.volumePropWrap.independentComponents)
		self.assertIsNotNone(self.volumePropWrap.interpolationType)

	def testVtkVolumePropertyWrapperGetter(self):
		volPropWrapper = vtkVolumePropertyWrapper()
		volPropWrapper.setOriginalObject(self.volumePropertyCT.volumeProperty)
		vtkVolProp = volPropWrapper.originalObject()
		# Check that it is a vtkVolumeProperty by checking specific vtkVolumeProperty attributes
		self.assertTrue(hasattr(vtkVolProp, "GetIndependentComponents"))
		self.assertEqual(self.volumePropertyCT.volumeProperty.GetAmbient(), vtkVolProp.GetAmbient())

	def testVtkVolumePropertyWrapperYaml(self):
		volPropWrapper = vtkVolumePropertyWrapper()
		volPropWrapper.setOriginalObject(self.volumePropertyCT.volumeProperty)

		dump = yaml.dump(volPropWrapper)
		
		volumePropertyWrapper2 = yaml.load(dump)

		self.assertEqual(volPropWrapper.independentComponents, volumePropertyWrapper2.independentComponents)
		self.assertEqual(volPropWrapper.interpolationType, volumePropertyWrapper2.interpolationType)
		self.assertEqual(volPropWrapper.shade, volumePropertyWrapper2.shade)

	def testvtkColorTransferFunctionWrapper(self):
		self.volumePropertyCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.volumePropertyCT.colorFunction)

		self.assertEqual(len(colorFunctionWrapper.nodes), self.volumePropertyCT.colorFunction.GetSize())

	def testColorTransferFunctionYaml(self):
		self.volumePropertyCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.volumePropertyCT.colorFunction)
		
		dump = yaml.dump(colorFunctionWrapper)
		colorFunctionWrapper2 = yaml.load(dump)

		self.assertEqual(len(colorFunctionWrapper.nodes), len(colorFunctionWrapper2.nodes))

	def testColorTransferFunctionWrapperGetter(self):
		self.volumePropertyCT.updateTransferFunction()

		colorFunctionWrapper = vtkColorTransferFunctionWrapper()
		colorFunctionWrapper.setOriginalObject(self.volumePropertyCT.colorFunction)

		colorFunction = colorFunctionWrapper.originalObject()

		self.assertEqual(len(colorFunctionWrapper.nodes), colorFunction.GetSize())

	def testPiecewiseFunctionWrapper(self):
		self.volumePropertySimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper()
		piecewiseFunctionWrapper.setOriginalObject(self.volumePropertySimple.opacityFunction)

		self.assertEqual(len(piecewiseFunctionWrapper.nodes), self.volumePropertySimple.opacityFunction.GetSize())

	def testPiecewiseFunctionWrapperGetter(self):
		self.volumePropertySimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper()
		piecewiseFunctionWrapper.setOriginalObject(self.volumePropertySimple.opacityFunction)

		piecewiseFunction = piecewiseFunctionWrapper.originalObject()

		self.assertTrue(piecewiseFunction.GetSize(), self.volumePropertySimple.opacityFunction.GetSize())

	def testPiecewiseFunctionWrapperYaml(self):
		self.volumePropertySimple.updateTransferFunction()

		piecewiseFunctionWrapper = vtkPiecewiseFunctionWrapper(self.volumePropertySimple.opacityFunction)

		dump = yaml.dump(piecewiseFunctionWrapper)

		piecewiseFunctionWrapper2 = yaml.load(dump)

		self.assertEqual(len(piecewiseFunctionWrapper.nodes), len(piecewiseFunctionWrapper2.nodes))


	def testVolumePropertyWrapper(self):
		self.volumePropertySimple.updateTransferFunction()

		volPropWrapper = VolumePropertyObjectWrapper(self.volumePropertySimple)

		self.assertEqual(volPropWrapper.renderType, RenderTypeSimple)
		self.assertIsNotNone(volPropWrapper.volumeProperty)
		self.assertIsNotNone(volPropWrapper.colorFunction)
		self.assertIsNotNone(volPropWrapper.opacityFunction)

		dump = yaml.dump(volPropWrapper)
		volPropWrapper2 = yaml.load(dump)

		self.assertEqual(volPropWrapper.renderType, volPropWrapper2.renderType)
