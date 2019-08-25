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
from collections import OrderedDict
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


class ViewportCaptureCameraSettingItem(QtWidgets.QWidget):

    def __init__(self,cam):
        super(ViewportCaptureCameraSettingItem,self).__init__()
        ui_file = os.path.join(DIR,"ui","item.ui")
        loadUi(ui_file,self)

        self.cam = cam
        self.loadCamData()

        self.setting = cam.setting[self.cam.name()]

        # NOTE 添加属性调整触发修改
        self.TX_SP.valueChanged.connect(self.txValueChange)
        self.TY_SP.valueChanged.connect(self.tyValueChange)
        self.TZ_SP.valueChanged.connect(self.tzValueChange)
        self.RX_SP.valueChanged.connect(self.rxValueChange)
        self.RY_SP.valueChanged.connect(self.ryValueChange)
        self.RZ_SP.valueChanged.connect(self.rzValueChange)
        self.Orthographic_CB.stateChanged.connect(self.orthographicState)

        # NOTE 添加按钮点击事件
        self.Cam_BTN.clicked.connect(lambda :pm.select(cam))
        self.Preview_BTN.clicked.connect(lambda :pm.lookThru(cam))
        self.Delete_BTN.clicked.connect(self.deleteLater)
        self.Save_BTN.clicked.connect(self.loadCamData)

    def loadCamData(self):
        self.Cam_BTN.setText(self.cam.name())
        self.TX_SP.setValue(self.cam.tx.get())
        self.TY_SP.setValue(self.cam.ty.get())
        self.TZ_SP.setValue(self.cam.tz.get())
        self.RX_SP.setValue(self.cam.rx.get())
        self.RY_SP.setValue(self.cam.ry.get())
        self.RZ_SP.setValue(self.cam.rz.get())
        self.Orthographic_CB.setChecked(self.cam.orthographic.get())
        
    def deleteLater(self):
        super(ViewportCaptureCameraSettingItem,self).deleteLater()
        del self.cam.setting[self.cam.name()]


    def orthographicState(self,check):
        check = False if check == 0 else True
        self.cam.orthographic.set(check)

    def txValueChange(self,value):
        self.setting["translate"][0] = value
        self.cam.tx.set(value)

    def tyValueChange(self,value):
        self.setting["translate"][1] = value
        self.cam.ty.set(value)

    def tzValueChange(self,value):
        self.setting["translate"][2] = value
        self.cam.tz.set(value)

    def rxValueChange(self,value):
        self.setting["rotate"][0] = value
        self.cam.rx.set(value)

    def ryValueChange(self,value):
        self.setting["rotate"][1] = value
        self.cam.ry.set(value)

    def rzValueChange(self,value):
        self.setting["rotate"][2] = value
        self.cam.rz.set(value)

    
class ViewportCaptureCameraSetting(ViewportCaptureGeneral):

    def __init__(self):
        super(ViewportCaptureCameraSetting,self).__init__()

        self.camera_setting = OrderedDict()
        self.grp = ""
        self.cam_list = []
        self.initialzie_cam = True

        # NOTE 加载UI文件
        self.item_ui = os.path.join(DIR,"ui","item.ui")
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

        # NOTE 添加下拉菜单的功能触发
        self.import_json_action.triggered.connect(self.importJsonSetting)
        self.export_json_action.triggered.connect(self.exportJsonSetting)
        self.reset_json_action.triggered.connect(self.resetJsonSetting)

        self.addHelpMenu(self,self.menu)
    
    def importJsonSetting(self):
        path = QFileDialog.getOpenFileName(self, caption=u"获取摄像机设置",filter= u"json (*.json)")
        path = path[0]
        if not path:return

        # NOTE 如果文件不存在则返回空
        if not os.path.exists(path):return

        with open(path,'r') as f:
            self.camera_setting = json.load(f,encoding="utf-8",object_pairs_hook=OrderedDict)
        
        # NOTE 更新面板内容
        self.showProcess()

    def exportJsonSetting(self):
        path = QFileDialog.getSaveFileName(self, caption=u"输出摄像机设置",filter= u"json (*.json)")
        path = path[0]
        if not path:return
                
        try:
            with open(path,'w') as f:
                json.dump(self.camera_setting,f,indent=4)
        except:
            QtWidgets.QMessageBox.warning(self, "Warning", "保存失败")

    def resetJsonSetting(self):
        self.initialzie_cam = True
        # NOTE 更新面板内容
        self.showProcess()

    def managerSignal(self,manager):
        func = partial(self.clearTempGrp,manager)
        self.back_action.triggered.connect(func)
        self.Back_BTN.clicked.connect(func)

    def clearTempGrp(self,manager):
        manager.changeWidgetTo(manager.main)
        pm.delete(self.grp)

    def showProcess(self):
        
        # NOTE 获取当前使用的摄像机视角
        for panel in pm.getPanel(type="modelPanel"):
            if pm.modelEditor(panel,q=1,av=1):
                active_cam = pm.modelEditor(panel,q=1,camera=1)
                break

        self.cam_list = []
        if pm.objExists("temp_capture_grp"):
            pm.delete("temp_capture_grp")
        self.grp = pm.group(n="temp_capture_grp",em=1)
        
        # NOTE 默认添加五个位置的视角 初始化输出默认摄像机视角
        if self.initialzie_cam:
            self.initialzie_cam = False
            self.camera_setting = OrderedDict()
            self.cam_list.append(self.addCam("front_cam",0,0,ortho=1))
            self.cam_list.append(self.addCam("side_cam",0,-90,ortho=1))
            self.cam_list.append(self.addCam("top_cam",-90,0,ortho=1))
            self.cam_list.append(self.addCam("fs45_cam",-45,45))
            self.cam_list.append(self.addCam("bs45_cam",-45,-135))
        else:
            # NOTE 已经经过初始化则读取 setting 数据
            for cam in self.camera_setting:
                r_list = self.camera_setting[cam]["rotate"]
                t_list = self.camera_setting[cam]["translate"]
                ortho = self.camera_setting[cam]["orthographic"]
                self.cam_list.append(self.addCam(cam,ortho=ortho,json=0,t_r_list=(t_list,r_list)))
        
        # NOTE 清空当前列表中的内容 除了弹簧
        count = self.Cam_Item_Scroll.layout().count()-1
        for i in reversed(range(self.Cam_Item_Scroll.layout().count())): 
            if i != count:
                widgetToRemove = self.Cam_Item_Scroll.layout().itemAt(i).widget()
                self.Cam_Item_Scroll.layout().removeWidget(widgetToRemove)
                if widgetToRemove:widgetToRemove.setParent(None)
        
        # NOTE 根据设置逐个添加摄像机 item
        for cam in self.cam_list:
            cam.setting = self.camera_setting
            item = ViewportCaptureCameraSettingItem(cam)
            
            count = self.Cam_Item_Scroll.layout().count()
            self.Cam_Item_Scroll.layout().insertWidget(count-1,item)
          
        # NOTE 还原当前使用的摄像机视角
        pm.lookThru(active_cam)

    def addCam(self,text,rx=-45,ry=45,fit=0.5,ortho=False,json=True,t_r_list=None):
        
        cam,cam_shape = pm.camera(n=text)
        text = cam.name()

        pm.parent(cam,self.grp)

        # Note 隐藏摄像机
        cam.visibility.set(0)
            
        # Note 设置旋转值用于
        if t_r_list:
            t,r = t_r_list
            cam.t.set(t)
            cam.r.set(r)
        else:
            cam.rx.set(rx)
            cam.ry.set(ry)
            pm.lookThru(cam)
            pm.viewFit(f=fit,all=0)

        cam_shape.orthographic.set(ortho)

        if json:
            self.camera_setting[text] = {}
            self.camera_setting[text]["translate"] = cam.t.get().tolist()
            self.camera_setting[text]["rotate"] = cam.r.get().tolist()
            self.camera_setting[text]["orthographic"] = ortho
        
        return cam
    

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
        self.layout().addWidget(self.main)
    
    def managerSignal(self):
        for widget in self.widget_list:
            widget.managerSignal(self)
            widget.manager = self
        
        # NOTE 添加删除摄像机组的事件
        def deleteTempData():
            if pm.objExists("temp_capture_grp"):
                pm.delete("temp_capture_grp")
        self.window().destroyed.connect(deleteTempData)
        self.window().adjustSize()

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