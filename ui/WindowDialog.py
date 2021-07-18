"""
WindowDialog

:Authors:
    Berend Klein Haneveld
"""
from ui.dialogs import ExportProgressDialog
from PySide6.QtCore import QObject
from PySide6.QtCore import Slot


class WindowDialog(QObject):
    """
    WindowDialog
    """

    def __init__(self):
        super(WindowDialog, self).__init__()

    @Slot(str)
    def showProgressBar(self, message):
        self._progressDialog = ExportProgressDialog(self, message)
        self._progressDialog.open()

    @Slot()
    def hideProgressBar(self):
        self._progressDialog.accept()
