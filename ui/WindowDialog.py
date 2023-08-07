"""
WindowDialog

:Authors:
    Berend Klein Haneveld
"""
from PySide6.QtCore import QObject, Slot

from ui.dialogs import ExportProgressDialog


class WindowDialog(QObject):
    """
    WindowDialog
    """

    @Slot(str)
    def showProgressBar(self, message):
        self._progressDialog = ExportProgressDialog(self, message)
        self._progressDialog.open()

    @Slot()
    def hideProgressBar(self):
        self._progressDialog.accept()
