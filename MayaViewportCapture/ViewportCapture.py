# coding:utf-8
import os
import time
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


from functools import partial

import ImgUtil
reload(ImgUtil)
from ImgUtil import MayaImageUtil,QtImageUtil

import ViewportCaptureGeneral
reload(ViewportCaptureGeneral)
import ViewportCaptureSetting
reload(ViewportCaptureSetting)
import ViewportCaptureCameraSetting
reload(ViewportCaptureCameraSetting)

from ViewportCaptureGeneral import ViewportCaptureGeneral
from ViewportCaptureSetting import ViewportCaptureSetting
from ViewportCaptureCameraSetting import ViewportCaptureCameraSetting

DIR = os.path.dirname(__file__)

class ViewportCapture(ViewportCaptureGeneral):
    u"""
    ViewportCapture 主界面
    """
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
        """
        managerSignal 继承自 General 类
        
        Manager 依附到 Maya 窗口后触发事件

        Arguments:
            manager {ViewportCaptureManager} -- Manager
        """
        # NOTE 添加 mian 的窗口切换
        func = partial(manager.changeWidgetTo,manager.setting)
        self.setting_action.triggered.connect(func)
        func = partial(manager.changeWidgetTo,manager.cam_setting)
        self.cam_setting_action.triggered.connect(func)

        # NOTE 添加关闭窗口触发
        self.close_action.triggered.connect(manager.window().close)

    def capture(self):
        """
        capture 截取图片输出
        """
        file_path,_ = QFileDialog.getSaveFileName(self, caption=u"获取输出图片路径",filter= u"png (*.png);;jpg (*.jpg)")

        # NOTE 判断是否是空路径
        if not file_path:
            return
        
        # NOTE 获取当前激活的面板 (modelPanel4)
        for panel in pm.getPanel(type="modelPanel"):
            if pm.modelEditor(panel,q=1,av=1):
                active_cam = pm.modelEditor(panel,q=1,camera=1)
                active_panel = panel
                break

        # NOTE 获取当前 HUD 相关的显示状态
        display_1 = pm.modelEditor(active_panel,q=1,hud=1)
        display_2 = pm.modelEditor(active_panel,q=1,grid=1)
        display_3 = pm.modelEditor(active_panel,q=1,m=1)
        display_4 = pm.modelEditor(active_panel,q=1,hos=1)
        display_5 = pm.modelEditor(active_panel,q=1,sel=1)
        
        # NOTE 隐藏界面显示
        pm.modelEditor(active_panel,e=1,hud=0)
        pm.modelEditor(active_panel,e=1,grid=0)
        pm.modelEditor(active_panel,e=1,m=0)
        pm.modelEditor(active_panel,e=1,hos=0)
        pm.modelEditor(active_panel,e=1,sel=0)
        
        # NOTE 触发截屏处理
        self.cam_setting = self.manager.cam_setting
        self.setting = self.manager.setting
        # NOTE 根据设置窗口的选项 获取图片处理的API
        API = self.setting.Maya_RB.isChecked()
        if API:
            self.util = MayaImageUtil()
        else:
            self.util = QtImageUtil()

        # NOTE 创建临时摄像机组
        self.cam_setting.showProcess()
        
        # NOTE 获取摄像机截取的画面
        img_list = []
        for cam in self.cam_setting.camera_setting:
            pm.lookThru(cam)
            img = self.captureImage()
            if img: img_list.append(img)
        
        # Note 合并图片
        img = self.util.mergeImage(img_list,horizontal=self.setting.Horizontal_RB.isChecked())

        ext = os.path.splitext(file_path)[-1][1:]
        # Note 不同API的输出指令不一样进行区分
        if API:
            img.writeToFile(file_path, ext)
        else:
            img.save(file_path,format = ext)

        # NOTE 恢复HUD显示
        pm.modelEditor(active_panel,e=1,hud=display_1)
        pm.modelEditor(active_panel,e=1,grid=display_2)
        pm.modelEditor(active_panel,e=1,m=display_3)
        pm.modelEditor(active_panel,e=1,hos=display_4)
        pm.modelEditor(active_panel,e=1,sel=display_5)

        # NOTE 恢复之前的摄像机视角并删除临时的摄像机组
        pm.lookThru(active_cam)
        pm.delete(self.cam_setting.grp)

        # NOTE 输出成功信息
        QtWidgets.QMessageBox.information(self,u"输出完成",u"图片输出成功\n输出路径:%s"%file_path)

    def captureImage(self):
        """
        captureImage 截取单个视角的图片
        
        Returns:
            [Image] -- 根据图片处理API返回相应的图片
        """
        img = self.util.getActiveM3dViewImage()
        
        if self.setting.Crop_CB.isChecked():
            width = self.setting.Width_SP.value()
            height = self.setting.Height_SP.value()
            img = self.util.centerCropImage(img,width,height)

        if not img:
            QtWidgets.QMessageBox.warning(self, u"警告", u"图片输出失败")
            return

        return img


class ViewportCaptureManager(QtWidgets.QWidget):
    u"""
    ViewportCaptureManager 组件管理容器
    """
    def __init__(self):
        super(ViewportCaptureManager,self).__init__()

        self.main = ViewportCapture()
        self.setting = ViewportCaptureSetting()
        self.cam_setting = ViewportCaptureCameraSetting()

        # # NOTE 存到索引的数组中 避免 Python 的回收机制将 组件 删除
        self.widget_list = [self.main,self.setting,self.cam_setting]
        
        # NOTE 默认添加 mian 组件为当前显示
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.main)
    
    def managerSignal(self):
        """
        managerSignal 触发内部组件事件
        """
        for widget in self.widget_list:
            widget.manager = self
            widget.managerSignal(self)
        
        # NOTE 添加删除摄像机组的事件
        def deleteTempData():
            if pm.objExists("temp_capture_grp"):
                pm.delete("temp_capture_grp")
            if hasattr(self.cam_setting,"active_cam") and pm.objExists(self.cam_setting.active_cam):
                pm.lookThru(self.cam_setting.active_cam)
        
        self.window().destroyed.connect(deleteTempData)

        # NOTE 最后调整显示大小
        self.window().resize(300,100)

    def changeWidgetTo(self,widget):
        """changeWidgetTo 切换组件
        
        Arguments:
            widget {QWidget} -- 要切换到的组件
        """
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
    # NOTE 将Maya窗口转换成 Qt 组件
    ptr = mayaToQT(window)
    ptr.setLayout(QtWidgets.QVBoxLayout())
    ptr.layout().setContentsMargins(0,0,0,0)
    ptr.layout().addWidget(panel)
    # NOTE 添加管理事件
    panel.managerSignal()

    return panel