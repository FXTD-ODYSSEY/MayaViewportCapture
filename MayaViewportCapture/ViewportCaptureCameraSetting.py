# coding:utf-8

import os
from functools import partial
from collections import OrderedDict
import pymel.core as pm
import json

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from Qt.QtCompat import loadUi
from Qt.QtCompat import QFileDialog

# import ViewportCaptureGeneral
# reload(ViewportCaptureGeneral)
import ViewportCaptureCameraSettingItem
reload(ViewportCaptureCameraSettingItem)

from ViewportCaptureGeneral import ViewportCaptureGeneral
from ViewportCaptureCameraSettingItem import ViewportCaptureCameraSettingItem



DIR = os.path.dirname(__file__)

class ViewportCaptureCameraSetting(ViewportCaptureGeneral):
    """
    ViewportCaptureCameraSetting 摄像机设置界面
    """
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
        self.main_action        = QtWidgets.QAction(u'主界面', self)    
        self.setting_action     = QtWidgets.QAction(u'插件设置', self)    
        self.close_action       = QtWidgets.QAction(u'关闭', self)    

        self.edit_menu.addAction(self.import_json_action)
        self.edit_menu.addAction(self.export_json_action)
        self.edit_menu.addAction(self.reset_json_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.main_action)
        self.edit_menu.addAction(self.setting_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.close_action)

        # NOTE 添加下拉菜单的功能触发
        self.import_json_action.triggered.connect(self.importJsonSetting)
        self.export_json_action.triggered.connect(self.exportJsonSetting)
        self.reset_json_action.triggered.connect(self.resetJsonSetting)
        
        self.Save_BTN.clicked.connect(self.batchLoadCamData)
        self.Add_Cam_BTN.clicked.connect(self.addCamItem)
        self.addHelpMenu(self,self.menu)
    
    def addCamItem(self):
        """
        addCamItem 添加摄像机Item
        """
        text,ok = QtWidgets.QInputDialog.getText(self, self.tr("新建摄像机角度"),self.tr("输入摄像机角度名称"))
        if ok and text:
            cam = self.addCam(text,0,0)
            self.cam_list.append(cam)
        
        self.showProcess()

    def batchLoadCamData(self):
        """
        batchLoadCamData 批量保存摄像机属性
        """
        # NOTE 遍历所有的item
        count = self.Cam_Item_Scroll.layout().count()-1
        for i in reversed(range(self.Cam_Item_Scroll.layout().count())): 
            if i != count:
                item = self.Cam_Item_Scroll.layout().itemAt(i).widget()
                item.loadCamData()

    def importJsonSetting(self):
        """
        importJsonSetting 导入 Json 设置
        """
        path,_ = QFileDialog.getOpenFileName(self, caption=u"获取摄像机设置",filter= u"json (*.json)")
        if not path:return

        # NOTE 如果文件不存在则返回空
        if not os.path.exists(path):return

        with open(path,'r') as f:
            self.camera_setting = json.load(f,encoding="utf-8",object_pairs_hook=OrderedDict)
        
        # NOTE 更新面板内容
        self.showProcess()

    def exportJsonSetting(self):
        """
        exportJsonSetting 导出 Json 设置
        """
        path,_ = QFileDialog.getSaveFileName(self, caption=u"输出摄像机设置",filter= u"json (*.json)")
        if not path:return
                
        try:
            with open(path,'w') as f:
                json.dump(self.camera_setting,f,indent=4)
        except:
            QtWidgets.QMessageBox.warning(self, "Warning", "保存失败")

    def resetJsonSetting(self):
        """
        resetJsonSetting 重置默认设置
        """
        self.initialzie_cam = True
        # NOTE 更新面板内容
        self.showProcess()

    def managerSignal(self,manager):
        """
        managerSignal 继承自General类 容器依附到 Maya 窗口后触发事件

        Arguments:
            manager {ViewportCaptureManager} -- 组件管理容器
        """
        func = partial(self.clearTempGrp,manager)
        self.main_action.triggered.connect(func)
        self.Back_BTN.clicked.connect(func)

        func = partial(manager.changeWidgetTo,manager.setting)
        self.setting_action.triggered.connect(func)

        self.close_action.triggered.connect(manager.window().close)

    def clearTempGrp(self,manager):
        """
        clearTempGrp 返回主界面 删除临时的组
        
        Arguments:
            manager {ViewportCaptureManager} -- 组件管理容器
        """
        manager.changeWidgetTo(manager.main)
        pm.delete(self.grp)

    def showProcess(self):
        """
        showProcess 继承自 General 类 切换界面的时候触发
        """
        self.sel_list = pm.ls(sl=1)
        if not self.sel_list:
            self.sel_list = [mesh.getParent() for mesh in pm.ls(type="mesh")]

        # NOTE 获取当前使用的摄像机视角
        for panel in pm.getPanel(type="modelPanel"):
            if pm.modelEditor(panel,q=1,av=1):
                self.active_cam = pm.modelEditor(panel,q=1,camera=1)
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
            item = ViewportCaptureCameraSettingItem(cam,self)
            
            count = self.Cam_Item_Scroll.layout().count()
            self.Cam_Item_Scroll.layout().insertWidget(count-1,item)
          
        # NOTE 还原当前使用的摄像机视角
        pm.lookThru(self.active_cam)

        # NOTE 是否禁用添加按钮
        self.manager.setting.limitCam()

    def addCam(self,text,rx=-45,ry=45,ortho=False,json=True,t_r_list=None):
        """addCam 添加摄像机
        
        Arguments:
            text {str} -- 摄像机名称
        
        Keyword Arguments:
            rx {int} -- x轴旋转角度 (default: {-45})
            ry {int} -- y轴旋转角度 (default: {45})
            ortho {bool} -- 正交属性 (default: {False})
            json {bool} -- 是否存储当前设置的属性 (default: {True})
            t_r_list {tuple} -- 位移和旋转的组合元组 (default: {None})
        
        Returns:
            [camera] -- Maya 的 Camera 对象
        """
        fit = self.manager.setting.Fit_SP.value()

        cam,cam_shape = pm.camera(n=text)
        text = cam.name()

        pm.parent(cam,self.grp)

        # Note 隐藏摄像机
        cam.visibility.set(0)
            
        # Note 如果传入这个变量说明是读取数据 安装数据设置摄像机
        pm.select(self.sel_list)
        if t_r_list:
            t,r = t_r_list
            cam.t.set(t)
            cam.r.set(r)
        else:
            cam.rx.set(rx)
            cam.ry.set(ry)
            pm.lookThru(cam)
            pm.viewFit(f=fit,all=0)

        if ortho:
            cam_shape.orthographic.set(ortho)
            pm.lookThru(cam)
            pm.viewFit(f=fit/2,all=0)

        # NOTE 是否将数组输出到到字典上
        if json:
            self.camera_setting[text] = {}
            self.camera_setting[text]["translate"] = cam.t.get().tolist()
            self.camera_setting[text]["rotate"] = cam.r.get().tolist()
            self.camera_setting[text]["orthographic"] = ortho
        
        return cam
    
