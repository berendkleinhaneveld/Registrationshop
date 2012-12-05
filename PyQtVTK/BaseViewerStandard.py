
from SubjectMixin import *
import Vtk
from Vtk.RenderWindowInteractor import *
from Vtk.VtkTextProperty import *
from vtkSSAOPassPython import *
import vtkSSAOPassPython

vtkIdentityMatrix4x4 = vtkMatrix4x4()
vtkIdentityMatrix4x4.Identity()

class ViewingDirection:
    def __init__(self, position, viewup):
        self._Position  = position
        self._ViewUp    = viewup

    def GetPosition(self):
        return self._Position

    def GetViewUp(self):
        return self._ViewUp

class BaseViewer(QFrame, SubjectMixin):
    def __init__(self):
        QFrame.__init__(self)
        SubjectMixin.__init__(self)

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(2)
        self.setMidLineWidth(2)
        self.setStyleSheet("QFrame{color:rgb(230, 153, 51)}")

        self.Renderer = vtk.vtkOpenGLRenderer()
        
        self.Actors    = {}

        self.Layout = QGridLayout(self)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.Layout)
        
        self.Interactor = RenderWindowInteractor(self)

        self.Renderer.SetBackground2(0.4, 0.4, 0.4)
        self.Renderer.SetBackground(0.1, 0.1, 0.1)
        self.Renderer.SetGradientBackground(True)
        
        self.Interactor.Initialize()
        self.Interactor.Start()

        self.Interactor.GetRenderWindow().AddRenderer(self.Renderer)
        
        self.Layout.addWidget(self.Interactor, 0, 0)
        
        self.InteractorStyleTrackballCamera = vtkInteractorStyleTrackballCamera()
        self.InteractorStyleTrackballCamera.AutoAdjustCameraClippingRangeOn()

        self.Interactor.GetRenderWindow().GetInteractor().SetInteractorStyle(self.InteractorStyleTrackballCamera)

        self.OutlineSource = vtk.vtkOutlineSource()

        self.OutlineMapper = vtk.vtkPolyDataMapper()
        self.OutlineMapper.SetInput(self.OutlineSource.GetOutput())

        self.OutlineActor = vtk.vtkActor()
        self.OutlineActor.GetProperty().SetColor(0.9, 0.6, 0.2)
        self.OutlineActor.SetMapper(self.OutlineMapper)
        self.OutlineActor.UseBoundsOff()

        self.Renderer.AddActor(self.OutlineActor)

        self.ViewingDirections = {}

        self.ViewingDirections["AP"] = ViewingDirection(position = (0, -1, 0), viewup = (0, 0, 1))
        self.ViewingDirections["PA"] = ViewingDirection(position = (0, 1, 0), viewup = (0, 0, 1))
        self.ViewingDirections["LR"] = ViewingDirection(position = (1, 0, 0), viewup = (0, 0, 1))
        self.ViewingDirections["RL"] = ViewingDirection(position = (-1, 0, 0), viewup = (0, 0, 1))
        self.ViewingDirections["HF"] = ViewingDirection(position = (0, 0, 1), viewup = (0, 1, 0))
        self.ViewingDirections["FH"] = ViewingDirection(position = (0, 0, -1), viewup = (0, -1, 0))

        self.AnnotationMargin  = 10

        self.AnnotationActors  = {}

        self.AnnotationActors["ViewTitle"] = vtkTextActor()

        self.Renderer.AddActor(self.AnnotationActors["ViewTitle"])

        self.AnnotationActors["ViewTitle"].SetTextProperty(VtkTextProperty(fontsize = 13))

        self.Interactor.CreateOrientationMarker()

        self.Renderer.GetActiveCamera().ParallelProjectionOff()
        self.Renderer.GetActiveCamera().SetViewAngle(30)

        LightsPass              = vtkLightsPass()
        DefaultPass             = vtkDefaultPass()
        Passes                  = vtkRenderPassCollection()

        Passes.AddItem(LightsPass)
        Passes.AddItem(DefaultPass)

        SequencePass            = vtkSequencePass()

        SequencePass.SetPasses(Passes)

        CameraPass              = vtkCameraPass()

        CameraPass.SetDelegatePass(SequencePass)

        AmbientOcclusionPass    = vtkSSAOPassPython.vtkSSAOPass()
        AmbientOcclusionPass.SetDelegatePass(CameraPass)
        AmbientOcclusionPass.SetKernelRadius(10)
        AmbientOcclusionPass.SetRenderMode(4)

        self.Renderer.SetPass(AmbientOcclusionPass)
        self.Renderer.RemoveAllLights()
        self.Light = vtkLight()
        self.Light.SetAmbientColor(0.3, 0.3, 0.3)
        self.Light.SetPosition(0, 0, 200)
        self.Light.SetDiffuseColor(0, 0, 0)
 #       self.Light.SetLightTypeToSceneLight()

        self.Renderer.AddLight(self.Light)

        QApplication.instance().aboutToQuit.connect(self.OnApplicationAboutToQuit)

    def OnApplicationAboutToQuit(self):
        self.Renderer.RemoveAllViewProps()
        self.Interactor.GetRenderWindow().Finalize()
        self.Interactor.SetRenderWindow(None)

    def GetActors(self):
        return self.Actors

    def AddActor(self, name, actor):
        self.Actors[name] = actor
        self.Renderer.AddActor(actor)
        self.UpdateBoundingBox()
        self.NotifyObservers("actors:sizechanged", self.Actors[name])

    def RemoveActor(self, name):
        if self.Actors.has_key(name):
            self.Actors.pop(name)
            self.NotifyObservers("actors:sizechanged", None)

    def GetRenderer(self):
        return self.Renderer

    def GetInteractor(self):
        return self.Interactor

    def GetRenderWindowInteractor(self):
        return self.Interactor.GetRenderWindow().GetInteractor()

    def Invalidate(self):
        self.Interactor.Render()

    def ResetCamera(self):
        self.Renderer.ResetCamera(self.Renderer.ComputeVisiblePropBounds())
        self.Renderer.GetActiveCamera().SetClippingRange(1, 10.0)
        self.Invalidate()

    def UpdateBoundingBox(self):
        self.SetBounds(self.Renderer.ComputeVisiblePropBounds())
        self.ResetCamera()

    def SetBounds(self, bounds):
        self.OutlineSource.SetBounds(bounds)
        self.ResetCamera()

    def SetViewingDirection(self, viewname, offset_matrix = vtkIdentityMatrix4x4):
        if not self.ViewingDirections.has_key(viewname):
            print "View name does not exist!"

        LocalFocalPointTM   = vtkMatrix4x4()
        WorldFocalPointTM   = vtkMatrix4x4()
        LocalPositionTM     = vtkMatrix4x4()
        WorldPositionTM     = vtkMatrix4x4()
        LocalUpTM           = vtkMatrix4x4()
        WorldUpTM           = vtkMatrix4x4()

        LocalFocalPointTM.Identity()
        WorldFocalPointTM.Identity()
        LocalPositionTM.Identity()
        WorldPositionTM.Identity()
        LocalUpTM.Identity()
        WorldUpTM.Identity()

        LocalFocalPoint = [0, 0, 0]

        LocalFocalPointTM.SetElement(0, 3, LocalFocalPoint[0])
        LocalFocalPointTM.SetElement(1, 3, LocalFocalPoint[1])
        LocalFocalPointTM.SetElement(2, 3, LocalFocalPoint[2])

        LocalPosition = self.ViewingDirections[viewname].GetPosition()

        LocalPositionTM.SetElement(0, 3, LocalPosition[0])
        LocalPositionTM.SetElement(1, 3, LocalPosition[1])
        LocalPositionTM.SetElement(2, 3, LocalPosition[2])

        LocalUp = self.ViewingDirections[viewname].GetViewUp()

        LocalUpTM.SetElement(0, 3, LocalUp[0])
        LocalUpTM.SetElement(1, 3, LocalUp[1])
        LocalUpTM.SetElement(2, 3, LocalUp[2])

        vtkMatrix4x4.Multiply4x4(offset_matrix, LocalFocalPointTM, WorldFocalPointTM)
        vtkMatrix4x4.Multiply4x4(offset_matrix, LocalPositionTM, WorldPositionTM)
        vtkMatrix4x4.Multiply4x4(offset_matrix, LocalUpTM, WorldUpTM)

        Up = [WorldUpTM.GetElement(0, 3) - offset_matrix.GetElement(0, 3), WorldUpTM.GetElement(1, 3) - offset_matrix.GetElement(1, 3), WorldUpTM.GetElement(2, 3) - offset_matrix.GetElement(2, 3)]

        ActiveCamera = self.Renderer.GetActiveCamera()

        ActiveCamera.SetFocalPoint(WorldFocalPointTM.GetElement(0, 3), WorldFocalPointTM.GetElement(1, 3), WorldFocalPointTM.GetElement(2, 3))
        ActiveCamera.SetPosition(WorldPositionTM.GetElement(0, 3), WorldPositionTM.GetElement(1, 3), WorldPositionTM.GetElement(2, 3))
        ActiveCamera.SetViewUp(Up)

        self.ResetCamera()
        self.Invalidate()

    def SetViewName(self, viewtitle):
        self.AnnotationActors["ViewTitle"].SetInput(viewtitle)
        self.Invalidate()

    def resizeEvent(self, ev):
        self.AnnotationActors["ViewTitle"].SetDisplayPosition(int(0.5 * self.Interactor.width()), self.Interactor.height() - 3 * self.AnnotationMargin)


