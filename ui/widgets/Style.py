"""
Style

Contains convenience functions for styling widgets.

:Authors:
	Berend Klein Haneveld
"""
import sys


def styleWidgetForTab(widget):
	"""
	This function style a widget that can be used inside a QScrollArea that
	is inside a QTabWidget. On OS X the background color inside a tab
	widget is slightly darker than the default, so it has to be styled
	otherwise it would stand out.

	There is a bug in Qt where QComboBox will not render properly
	on OS X when the background style of a parent is adjusted.
	In order to solve this, the background style of such a widget
	should only be set for that object, so by naming it and setting
	the style only for objects with that name the bug can be worked
	around.

	Use this function whenever a (container) widget is needed inside a
	QScrollArea in a QTabWidget.
	:type widget: QWidget
	"""
	if sys.platform.startswith("darwin"):
		widget.setObjectName("tabWidget")
		widget.setStyleSheet("#tabWidget {background: rgb(229, 229, 229);}")
	elif sys.platform.startswith("linux"):
		# This makes it look pretty on Elementary theme
		widget.setObjectName("tabWidget")
		widget.setStyleSheet("#tabWidget {background: rgb(236, 236, 236);}")
