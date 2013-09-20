import unittest
import os
from core.project import ProjectController


class ProjectControllerTest(unittest.TestCase):

	def testProjectController(self):
		projectController = ProjectController.Instance()
		self.assertIsNotNone(projectController.currentProject)

		projectController.newProject()
		self.assertIsNone(projectController.currentProject.title)

	def testSavingAndLoadingProjectsToDisk(self):
		projectController = ProjectController.Instance()

		# Save the project in the current directory
		path = os.path.dirname(os.path.abspath(__file__))
		projectPath = path + "/project"
		if not os.path.exists(projectPath):
			os.makedirs(projectPath)
		projectController.currentProject.title = "Unique title"
		projectController.currentProject.folder = unicode(projectPath)
		projectController.saveProject()

		# Reset the project controller
		projectController.newProject()
		self.assertIsNone(projectController.currentProject.title)
		self.assertIsNone(projectController.currentProject.folder)

		# Test for existance of a project file in the project folder
		self.assertTrue(os.path.exists(projectPath + "/project.yaml"))
		self.assertTrue(projectController.loadProject(projectPath))

		# Load the project again from disk
		projectController.loadProject(projectPath)
		self.assertIsNotNone(projectController.currentProject.title)
		self.assertIn("Unique", projectController.currentProject.title)

		try:
			os.remove(projectPath + "/project.yaml")
		except Exception:
			self.assertTrue(False)
