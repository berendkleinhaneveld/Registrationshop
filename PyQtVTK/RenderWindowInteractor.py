
try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except ImportError:
    raise ImportError("Cannot load PyQt!")

try:
    from vtk import *
except ImportError:
    raise ImportError("Cannot load VTK!")
 
class RenderWindowInteractor(QFrame): 
    
    # Map between VTK and Qt cursors.
    _CURSOR_MAP = {
        0:  Qt.ArrowCursor,          # VTK_CURSOR_DEFAULT
        1:  Qt.ArrowCursor,          # VTK_CURSOR_ARROW
        2:  Qt.SizeBDiagCursor,      # VTK_CURSOR_SIZENE
        3:  Qt.SizeFDiagCursor,      # VTK_CURSOR_SIZENWSE
        4:  Qt.SizeBDiagCursor,      # VTK_CURSOR_SIZESW
        5:  Qt.SizeFDiagCursor,      # VTK_CURSOR_SIZESE
        6:  Qt.SizeVerCursor,        # VTK_CURSOR_SIZENS
        7:  Qt.SizeHorCursor,        # VTK_CURSOR_SIZEWE
        8:  Qt.SizeAllCursor,        # VTK_CURSOR_SIZEALL
        9:  Qt.PointingHandCursor,   # VTK_CURSOR_HAND
        10: Qt.CrossCursor,          # VTK_CURSOR_CROSSHAIR
    }
     
    def CreateOrientationMarker(self):
    
        self._AxesActor = vtkAnnotatedCubeActor();
        self._AxesActor.SetXPlusFaceText('RL')
        self._AxesActor.SetXMinusFaceText('LR')
        #self._AxesActor.SetXFaceTextRotation(-90)
        self._AxesActor.SetYMinusFaceText('PA')
        self._AxesActor.SetYPlusFaceText('AP')
        #self._AxesActor.SetYFaceTextRotation(-180)
        self._AxesActor.SetZMinusFaceText('FH')
        self._AxesActor.SetZPlusFaceText('HF')
        self._AxesActor.SetZFaceTextRotation(90)
        self._AxesActor.SetTextEdgesVisibility(0)
        self._AxesActor.SetFaceTextScale(0.36)

        # text face properties        
        self._AxesActor.GetXMinusFaceProperty().SetColor(0.9, 0.6, 0.1)
        self._AxesActor.GetXPlusFaceProperty().SetColor(0.9, 0.6, 0.1)
        self._AxesActor.GetYMinusFaceProperty().SetColor(0.9, 0.6, 0.1)
        self._AxesActor.GetYPlusFaceProperty().SetColor(0.9, 0.6, 0.1)
        self._AxesActor.GetZMinusFaceProperty().SetColor(0.9, 0.6, 0.1)
        self._AxesActor.GetZPlusFaceProperty().SetColor(0.9, 0.6, 0.1)
        
        self._AxesActor.GetTextEdgesProperty().SetColor(0.9, 0.0, 0.0)
        self._AxesActor.GetTextEdgesProperty().SetDiffuseColor(0.9, 0.6, 0.1)
        self._AxesActor.GetTextEdgesProperty().SetEdgeVisibility(0)
        self._AxesActor.GetTextEdgesProperty().SetLineWidth(1)
        self._AxesActor.GetCubeProperty().SetColor(0.3, 0.3, 0.3)
        self._AxesActor.GetCubeProperty().SetEdgeVisibility(1)
        self._AxesActor.GetCubeProperty().SetLineWidth(1)
        self._AxesActor.GetCubeProperty().SetEdgeColor(0.1, 0.1, 0.1)
 
        self._Axes = vtk.vtkOrientationMarkerWidget()

        axes = vtkAxesActor();

        self._Axes.SetViewport(0.05, 0.05, 0.3, 0.3)
        self._Axes.SetOrientationMarker(axes)
        self._Axes.SetInteractor(self.GetRenderWindow().GetInteractor())
        self._Axes.EnabledOn()
        self._Axes.InteractiveOff()
        
    def HideOrientationMarker(self):
        
        self._AxesActor.SetCubeVisibility(0)
        
    def ShowOrientationMarker(self):
        
        self._AxesActor.SetCubeVisibility(1)

    def __init__(self, parent=None, wflags = Qt.WindowFlags(), **kw):
        
       
        
        
        # the current button
        self._ActiveButton = Qt.NoButton

        # private attributes
        self.__oldFocus = None
        self.__saveX = 0
        self.__saveY = 0
        self.__saveModifiers = Qt.NoModifier
        self.__saveButtons = Qt.NoButton

        # do special handling of some keywords:
        # stereo, rw

        stereo = 0

        if kw.has_key('stereo'):
            if kw['stereo']:
                stereo = 1

        rw = None

        if kw.has_key('rw'):
            rw = kw['rw']

        # create qt-level widget
        QFrame.__init__(self, parent, wflags|Qt.MSWindowsOwnDC)

        self.setFrameStyle(QFrame.Panel)
        
        if rw: # user-supplied render window
            self._RenderWindow = rw
        else:
            self._RenderWindow = vtk.vtkRenderWindow()

        self._RenderWindow.SetWindowInfo(str(int(self.winId())))

        if stereo: # stereo mode
            self._RenderWindow.StereoCapableWindowOn()
            self._RenderWindow.SetStereoTypeToCrystalEyes()

        if kw.has_key('iren'):
            self._Iren = kw['iren']
        else:
            self._Iren = vtk.vtkGenericRenderWindowInteractor()
            self._Iren.SetRenderWindow(self._RenderWindow)

        # do all the necessary qt setup
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_PaintOnScreen)
        self.setMouseTracking(True) # get all mouse events
        self.setFocusPolicy(Qt.WheelFocus)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self._Timer = QTimer(self)
        self.connect(self._Timer, SIGNAL('timeout()'), self.TimerEvent)

        self._Iren.AddObserver('CreateTimerEvent', self.CreateTimer)
        self._Iren.AddObserver('DestroyTimerEvent', self.DestroyTimer)
        self._Iren.GetRenderWindow().AddObserver('CursorChangedEvent',
                                                 self.CursorChangedEvent)

    def __getattr__(self, attr):
        """Makes the object behave like a vtkGenericRenderWindowInteractor"""
        if attr == '__vtk__':
            return lambda t=self._Iren: t
        elif hasattr(self._Iren, attr):
            return getattr(self._Iren, attr)
        else:
            raise AttributeError, self.__class__.__name__ + \
                  " has no attribute named " + attr

    def resizeEvent(self, ev):
        
        w = self.width()
        h = self.height()
        
        # Dirty hack to get the render window the right size
        # (and prevent the mouse cursor from having an offset)
        self._RenderWindow.SetSize(w, h)
        resultSize = self._RenderWindow.GetSize()
        correctionX = resultSize[0] - w
        correctionY = resultSize[1] - h
        self._RenderWindow.SetSize(w - correctionX, h - correctionY)
        self._Iren.SetSize(w, h)
        
    def CreateTimer(self, obj, evt):
        self._Timer.start(10)

    def DestroyTimer(self, obj, evt):
        self._Timer.stop()
        return 1

    def TimerEvent(self):
        self._Iren.TimerEvent()

    def CursorChangedEvent(self, obj, evt):
        """Called when the CursorChangedEvent fires on the render window."""
        # This indirection is needed since when the event fires, the current
        # cursor is not yet set so we defer this by which time the current
        # cursor should have been set.
        QTimer.singleShot(0, self.ShowCursor)

    def HideCursor(self):
        """Hides the cursor."""
        self.setCursor(Qt.BlankCursor)

    def ShowCursor(self):
        """Shows the cursor."""
        vtk_cursor = self._Iren.GetRenderWindow().GetCurrentCursor()
        qt_cursor = self._CURSOR_MAP.get(vtk_cursor, Qt.ArrowCursor)
        #self.setCursor(cursor)

    def sizeHint(self):
        return QSize(400, 400)

    def paintEngine(self):
        return None

    def paintEvent(self, ev):
        self._Iren.Render()

    def _GetCtrlShift(self, ev):
        ctrl = shift = False

        if hasattr(ev, 'modifiers'):
            if ev.modifiers() & Qt.ShiftModifier:
                shift = True
            if ev.modifiers() & Qt.ControlModifier:
                ctrl = True
        else:
            if self.__saveModifiers & Qt.ShiftModifier:
                shift = True
            if self.__saveModifiers & Qt.ControlModifier:
                ctrl = True

        return ctrl, shift

    def enterEvent(self, ev):
        if not self.hasFocus():
            self.__oldFocus = self.focusWidget()
            self.setFocus()

        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, chr(0), 0, None)
        self._Iren.EnterEvent()

    def leaveEvent(self, ev):
        if self.__saveButtons == Qt.NoButton and self.__oldFocus:
            self.__oldFocus.setFocus()
            self.__oldFocus = None

        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, chr(0), 0, None)
        self._Iren.LeaveEvent()

    def mousePressEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        repeat = 0
        if ev.type() == QEvent.MouseButtonDblClick:
            repeat = 1
        self._Iren.SetEventInformationFlipY(ev.x(), ev.y(),
                                            ctrl, shift, chr(0), repeat, None)

        self._ActiveButton = ev.button()

        if self._ActiveButton == Qt.LeftButton:
            self._Iren.LeftButtonPressEvent()
        elif self._ActiveButton == Qt.RightButton:
            self._Iren.RightButtonPressEvent()
        elif self._ActiveButton == Qt.MidButton:
            self._Iren.MiddleButtonPressEvent()

    def mouseReleaseEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(ev.x(), ev.y(),
                                            ctrl, shift, chr(0), 0, None)

        if self._ActiveButton == Qt.LeftButton:
            self._Iren.LeftButtonReleaseEvent()
        elif self._ActiveButton == Qt.RightButton:
            self._Iren.RightButtonReleaseEvent()
        elif self._ActiveButton == Qt.MidButton:
            self._Iren.MiddleButtonReleaseEvent()

    def mouseMoveEvent(self, ev):
        self.__saveModifiers = ev.modifiers()
        self.__saveButtons = ev.buttons()
        self.__saveX = ev.x()
        self.__saveY = ev.y()

        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(ev.x(), ev.y(),
                                            ctrl, shift, chr(0), 0, None)
        self._Iren.MouseMoveEvent()

    def keyPressEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        if ev.key() < 256:
            key = str(ev.text())
        else:
            key = chr(0)

        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, key, 0, None)
        self._Iren.KeyPressEvent()
        self._Iren.CharEvent()

    def keyReleaseEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        if ev.key() < 256:
            key = chr(ev.key())
        else:
            key = chr(0)

        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, key, 0, None)
        self._Iren.KeyReleaseEvent()

    def wheelEvent(self, ev):
        if ev.delta() >= 0:
            self._Iren.MouseWheelForwardEvent()
        else:
            self._Iren.MouseWheelBackwardEvent()

    def GetRenderWindow(self):
        return self._RenderWindow

    def Render(self):
        self.update()

