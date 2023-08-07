"""
Project

:Authors:
    Berend Klein Haneveld
"""
import os


class Project(object):
    """
    Project holds the basic information of a project for RegistrationShop
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.title = kwargs.get("title")
        self.fixedData = kwargs.get("fixedData")
        self.movingData = kwargs.get("movingData")
        self.isReference = kwargs.get("isReference")
        self.folder = kwargs.get("folder")
        self.fixedSettings = kwargs.get("fixedSettings")
        self.movingSettings = kwargs.get("movingSettings")
        self.multiSettings = kwargs.get("multiSettings")
        self.transformations = kwargs.get("transformations")

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False
        return (
            self.title == other.title
            and self.fixedData == other.fixedData
            and self.movingData == other.movingData
            and self.isReference == other.isReference
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def isValid(self):
        """
        Project is valid when the fixed and moving image data actually
        exits on disk. If this is not the case, then the project is
        invalid.
        """
        if self.fixedData and not os.path.isfile(self.fixedData):
            return False
        if self.movingData and not os.path.isfile(self.movingData):
            return False
        return True
