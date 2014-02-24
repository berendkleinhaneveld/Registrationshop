import unittest
import yaml

from core.project import Project


class TestProject(unittest.TestCase):

	def setUp(self):
		super(TestProject, self).setUp()
		self.project = Project(title="TestProject", fixedData="FixedTest",
			movingData="MovingTest", isReference=True)

	def tearDown(self):
		super(TestProject, self).tearDown()
		del self.project

	def testProject(self):
		self.assertTrue(hasattr(self.project, "title"))
		self.assertTrue(hasattr(self.project, "folder"))
		self.assertTrue(hasattr(self.project, "fixedData"))
		self.assertTrue(hasattr(self.project, "movingData"))
		self.assertTrue(hasattr(self.project, "isReference"))

	def testEqual(self):
		testProjectA = Project(title="TestProjectA", fixedData="FixedTest",
			movingData="MovingTest", isReference=True)
		testProjectB = Project(title="TestProjectB", fixedData="FixedTest",
			movingData="MovingTest", isReference=True)
		self.assertEqual(testProjectA, testProjectA)
		self.assertNotEqual(testProjectA, testProjectB)
		testProjectB.title = "TestProjectA"
		self.assertEqual(testProjectA, testProjectB)

	def testYaml(self):
		yamlObjectDump = yaml.dump(self.project)
		self.assertIn("title", yamlObjectDump)

		project = yaml.load(yamlObjectDump)
		self.assertEqual(project, self.project)

	# def testStrategy(self):
	# 	# testProject = Project(title="TestProject", fixedData="FixedTest",
	# 	# 	movingData="MovingTest", isReference=True)
	# 	self.assertIsNotNone(self.project.strategy)
