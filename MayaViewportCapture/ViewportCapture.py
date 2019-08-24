# coding:utf-8
import os
import pymel.core as pm
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.OpenMayaUI as omui
# NOTE 使用 Qt.py 兼容 Qt 4.0 和 Qt 5.0
from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance

class ViewportCapture(QtWidgets.QWidget):

    def __init__(self):
        super(ViewportCapture,self).__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        button = QtWidgets.QPushButton('捕捉图片')
        self.layout().addWidget(button)

        button.clicked.connect(self.captureImage)

    def captureImage(self):
        print "captureImage"
        # # NOTE initHUD.mel 中提取 Maya 所有内置的 HUD 对象
        # # NOTE 提取可以参照 test 目录下的 getHUD.py 脚本 
        # HUD_list = ['HUDObjDetBackfaces', 'HUDObjDetSmoothness', 'HUDObjDetInstance', 'HUDObjDetDispLayer', 'HUDObjDetDistFromCam', 'HUDObjDetNumSelObjs', 'HUDPolyCountVerts', 'HUDPolyCountEdges', 'HUDPolyCountFaces', 'HUDPolyCountTriangles', 'HUDPolyCountUVs', 'HUDSubdLevel', 'HUDSubdMode', 'HUDParticleCount', 'HUDCameraNames',
        # 'HUDViewportRenderer', 'HUDSymmetry', 'HUDCapsLock', 'HUDFrameRate', 'HUDGPUOverride', 'HUDEMState', 'HUDEvaluation', 'HUDLoadingTextures', 'HUDLoadingMaterials', 'HUDCurrentFrame', 'HUDIKSolverState', 'HUDCurrentCharacter', 'HUDPlaybackSpeed', 'HUDHikKeyingMode', 'HUDFbikKeyType', 'HUDSoftSelectState', 'HUDCurrentContainer', 'HUDFocalLength', 'HUDSceneTimecode', 'HUDViewAxis', 'HUDWalkMode', 'HUDBlendShapeEdit', 'HUDActiveSculptMesh', 'HUD3DCutSewUVActiveMesh']

        # # NOTE 隐藏所有UI
        # vis_HUD_list = []
        # for HUD in HUD_list:
        #     if pm.headsUpDisplay(HUD,ex=1) and pm.headsUpDisplay(HUD,q=1,vis=1):
        #         vis_HUD_list.append(HUD)
        #         pm.headsUpDisplay(HUD,e=1,vis=0)

        # NOTE 查询当前激活的面板
        for panel in pm.getPanel(type="modelPanel"):
            if pm.modelEditor(panel,q=1,av=1):
                active_panel = panel
                break

        # NOTE 隐藏界面显示
        pm.modelEditor(active_panel,e=1,hud=0)
        pm.modelEditor(active_panel,e=1,grid=0)
        pm.modelEditor(active_panel,e=1,m=0)
        pm.modelEditor(active_panel,e=1,hos=0)
        pm.modelEditor(active_panel,e=1,sel=0)

        viewport = OpenMayaUI.M3dView.active3dView()
        viewport.refresh()
        img = OpenMaya.MImage()

        viewport.setColorMask(1, 1, 1, 1)
        viewport.readColorBuffer(img, True)

        DIR = os.path.dirname(__file__)
        output = os.path.join(DIR, "viewport.jpg")
        img.writeToFile(output, 'jpg')

        # NOTE 恢复显示UI
        pm.modelEditor(active_panel,e=1,hud=1)
        pm.modelEditor(active_panel,e=1,grid=1)
        pm.modelEditor(active_panel,e=1,m=1)
        pm.modelEditor(active_panel,e=1,hos=1)
        pm.modelEditor(active_panel,e=1,sel=1)

        # for HUD in vis_HUD_list:
        #     pm.headsUpDisplay(HUD,e=1,vis=1)

def mayaWin():
    def mayaToQT( name ):
        # Maya -> QWidget
        ptr = omui.MQtUtil.findControl( name )
        if ptr is None:         ptr = omui.MQtUtil.findLayout( name )
        if ptr is None:         ptr = omui.MQtUtil.findMenuItem( name )
        if ptr is not None:     return wrapInstance( long( ptr ), QtWidgets.QWidget )
    
    # NOTE 如果变量存在 就检查窗口多开
    if pm.window("viewport_capture",q=1,ex=1):
        pm.deleteUI('viewport_capture')
    
    panel = ViewportCapture()
    window = pm.window("viewport_capture",title=u"viewport输出工具")
    pm.showWindow(window)
    ptr = mayaToQT(window)
    ptr.setLayout(QtWidgets.QVBoxLayout())
    ptr.layout().setContentsMargins(0,0,0,0)
    ptr.layout().addWidget(panel)