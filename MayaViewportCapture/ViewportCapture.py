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
from Qt.QtCompat import QFileDialog

import webbrowser
import json
from functools import partial
from ImgUtil import MayaImageUtil

DIR = os.path.dirname(__file__)
INSTRUNCTION_PATH = "file:///" + os.path.join(DIR,"instruction","README.html")
CAM_SETTING_PATH  = os.path.join(DIR,"json","cam_setting.json")
SETTING_PATH      = os.path.join(DIR,"json","setting.json")


class ViewportCaptureGeneral(QtWidgets.QWidget):

    def __init__(self):
        super(ViewportCaptureGeneral,self).__init__()

    def addHelpMenu(self,widget,menu):
        help_menu = menu.addMenu(u'帮助')
        help_action = QtWidgets.QAction(u'使用帮助', widget)    
        help_menu.addAction(help_action)
        help_action.triggered.connect(lambda x:webbrowser.open_new_tab(INSTRUNCTION_PATH))

    def showProcess(self):
        pass

    def managerSignal(self,manager):
        pass
        


class ViewportCaptureSetting(ViewportCaptureGeneral):

    def __init__(self):
        super(ViewportCaptureSetting,self).__init__()
        # NOTE 加载UI文件
        ui_file = os.path.join(DIR,"ui","setting.ui")
        loadUi(ui_file,self)

        self.menu = QtWidgets.QMenuBar(self)
        self.edit_menu = self.menu.addMenu(u'编辑')
        self.back_action = QtWidgets.QAction(u'返回', self)    
        self.edit_menu.addAction(self.back_action)
        self.addHelpMenu(self,self.menu)

    def managerSignal(self,manager):
        func = partial(manager.changeWidgetTo,manager.main)
        self.back_action.triggered.connect(func)
        self.Back_BTN.clicked.connect(func)

    
class ViewportCaptureCameraSetting(ViewportCaptureGeneral):

    def __init__(self):
        super(ViewportCaptureCameraSetting,self).__init__()

        self.camera_setting = self.importJsonSetting()

        # NOTE 加载UI文件
        ui_file = os.path.join(DIR,"ui","cam_setting.ui")
        loadUi(ui_file,self)

        self.menu = QtWidgets.QMenuBar(self)
        self.edit_menu = self.menu.addMenu(u'编辑')
        self.import_json_action = QtWidgets.QAction(u'导入设置', self)    
        self.export_json_action = QtWidgets.QAction(u'导出设置', self)  
        self.reset_json_action  = QtWidgets.QAction(u'重置设置', self)    
        self.back_action        = QtWidgets.QAction(u'返回', self)    

        self.edit_menu.addAction(self.import_json_action)
        self.edit_menu.addAction(self.export_json_action)
        self.edit_menu.addAction(self.reset_json_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.back_action)

        self.addHelpMenu(self,self.menu)
    
    def managerSignal(self,manager):
        func = partial(manager.changeWidgetTo,manager.main)
        self.back_action.triggered.connect(func)
        self.Back_BTN.clicked.connect(func)
    
    def importJsonSetting(self,path=CAM_SETTING_PATH):
        if path != CAM_SETTING_PATH:
            path = QFileDialog.getOpenFileName(self, caption=u"获取摄像机设置",filter= u"json (*.json)")
            path = path[0]
            if not path:return

        # NOTE 如果文件不存在则返回空
        if not os.path.exists(path):return

        with open(path,'r') as f:
            return json.load(f,encoding="utf-8")

    def ExportJsonSetting(self,path=CAM_SETTING_PATH):
        if path != CAM_SETTING_PATH:
            path = QFileDialog.getOpenFileName(self, caption=u"获取摄像机设置",filter= u"json (*.json)")
            path = path[0]
            if not path:return
                
        
        # NOTE 如果文件不存在则返回空
        if not os.path.exists(path):return

        try:
            with open(path,'w') as f:
                json.dump(self.camera_setting,f,indent=4)
        except:
            QMessageBox.warning(self, "Warning", "保存失败")

    

class ViewportCapture(ViewportCaptureGeneral):

    def __init__(self):
        super(ViewportCapture,self).__init__()
        # NOTE 加载UI文件
        ui_file = os.path.join(DIR,"ui","ViewportCapture.ui")
        loadUi(ui_file,self)

        self.menu = QtWidgets.QMenuBar(self)
        self.edit_menu = self.menu.addMenu(u'编辑')
        self.cam_setting_action = QtWidgets.QAction(u'摄像机设置', self)    
        self.setting_action     = QtWidgets.QAction(u'插件设置', self)    
        self.close_action       = QtWidgets.QAction(u'关闭', self)    

        # NOTE 添加 action 
        self.edit_menu.addAction(self.cam_setting_action)
        self.edit_menu.addAction(self.setting_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.close_action)

        self.addHelpMenu(self,self.menu)

        self.Process_BTN.clicked.connect(self.capture)
    
    def managerSignal(self,manager):
        # NOTE 添加 mian 的窗口切换
        func = partial(manager.changeWidgetTo,manager.setting)
        self.setting_action.triggered.connect(func)
        func = partial(manager.changeWidgetTo,manager.cam_setting)
        self.cam_setting_action.triggered.connect(func)

        # NOTE 添加关闭窗口触发
        self.close_action.triggered.connect(self.window().close)

    def capture(self):
        print "captureImage"

        file_path = QFileDialog.getSaveFileName(self, caption=u"获取输出图片路径",filter= u"jpg (*.jpg)")
        # NOTE 获取路径
        file_path = file_path[0]
        # NOTE 判断是否是合法的路径
        if not os.path.isdir(os.path.dirname(file_path)):
            return

        # NOTE 获取当前激活的面板 (modelPanel4)
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
        
        # NOTE 触发截屏处理
        self.captureImage(file_path)

        # NOTE 恢复显示UI
        pm.modelEditor(active_panel,e=1,hud=1)
        pm.modelEditor(active_panel,e=1,grid=1)
        pm.modelEditor(active_panel,e=1,m=1)
        pm.modelEditor(active_panel,e=1,hos=1)
        pm.modelEditor(active_panel,e=1,sel=1)
    
    def captureImage(self,file_path):
        util = MayaImageUtil()
        img = util.getActiveM3dViewImage()
        img = util.centerCropImage(img)
        if not img:
            QtWidgets.QMessageBox.warning(self, u"警告", u"图片输出失败")
            return

        return img



class ViewportCaptureManager(QtWidgets.QWidget):
    def __init__(self):
        super(ViewportCaptureManager,self).__init__()

        self.main = ViewportCapture()
        self.setting = ViewportCaptureSetting()
        self.cam_setting = ViewportCaptureCameraSetting()

        # NOTE 存到索引的数组中 避免 Python 的回收机制将 组件 删除
        self.widget_list = [self.main,self.setting,self.cam_setting]

        
        # NOTE 默认添加 mian 组件为当前显示
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.cam_setting)
    
    def managerSignal(self):
        for widget in self.widget_list:
            widget.managerSignal(self)
            widget.manager = self

    def changeWidgetTo(self,widget):
        # Note 清空当前页面
        for i in reversed(range(self.layout().count())): 
            widgetToRemove = self.layout().itemAt(i).widget()
            self.layout().removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)
        # Note 显示组件
        self.layout().addWidget(widget)
        widget.showProcess()
            

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
    
    panel = ViewportCaptureManager()
    window = pm.window("viewport_capture",title=u"viewport输出工具")

    pm.showWindow(window)
    ptr = mayaToQT(window)
    ptr.setLayout(QtWidgets.QVBoxLayout())
    ptr.layout().setContentsMargins(0,0,0,0)
    ptr.layout().addWidget(panel)
    # NOTE 添加管理事件
    panel.managerSignal()