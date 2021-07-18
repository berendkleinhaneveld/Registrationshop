"""
StatusWidget

:Authors:
    Berend Klein Haneveld
"""

import darkdetect
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen
from PySide6.QtGui import QColor
from PySide6.QtGui import QFont
from PySide6.QtCore import QRectF

from core.decorators import Singleton


@Singleton
class StatusWidget(QFrame):
    """
    StatusWidget
    """

    def __init__(self):
        QFrame.__init__(self)

        self._color = [220, 220, 220] if not darkdetect.isDark() else [80, 80, 80]

        self._font = QFont()
        self._font.setPixelSize(10)

        self._pen = QPen(QColor(100, 100, 100, 255))

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setFont(self._font)
        self.label.setMaximumWidth(300)
        self.label.setMaximumHeight(36)
        self.label.setMinimumHeight(36)

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setMinimumWidth(360)
        self.setMaximumWidth(360)

    def setText(self, text):
        self.label.setText(text)

    def paintEvent(self, ev):
        size = self.size()
        height = size.height() - 5
        width = size.width() - 5

        offset = 0.5
        rect = QRectF(2.0 + offset, 2.0 + offset, width, height)
        painter = QPainter(self)

        painter.setPen(self._pen)
        painter.setBrush(QColor(self._color[0], self._color[1], self._color[2]))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.drawRoundedRect(rect, 4, 4)
