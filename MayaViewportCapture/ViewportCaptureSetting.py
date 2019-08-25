# coding:utf-8

import os
import json
from functools import partial

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from Qt.QtCompat import loadUi
from Qt.QtCompat import QFileDialog

from ViewportCaptureGeneral import ViewportCaptureGeneral

DIR = os.path.dirname(__file__)
SETTING_PATH = os.path.join(DIR,"json","setting.json")

class ViewportCaptureSetting(ViewportCaptureGeneral):
    """
    ViewportCaptureSetting 设置界面
    """
    def __init__(self):
        super(ViewportCaptureSetting,self).__init__()
        # NOTE 加载UI文件
        ui_file = os.path.join(DIR,"ui","setting.ui")
        loadUi(ui_file,self)
        

        self.menu = QtWidgets.QMenuBar(self)
        self.edit_menu = self.menu.addMenu(u'编辑')

        self.import_json_action = QtWidgets.QAction(u'导入设置', self)    
        self.export_json_action = QtWidgets.QAction(u'导出设置', self)  
        self.reset_json_action  = QtWidgets.QAction(u'重置设置', self)    

        self.back_action        = QtWidgets.QAction(u'主界面', self)    
        self.cam_setting_action = QtWidgets.QAction(u'摄像机设置', self)    
        self.close_action       = QtWidgets.QAction(u'关闭', self)    


        self.edit_menu.addAction(self.import_json_action)
        self.edit_menu.addAction(self.export_json_action)
        self.edit_menu.addAction(self.reset_json_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.back_action)
        self.edit_menu.addAction(self.cam_setting_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.close_action)

        self.addHelpMenu(self,self.menu)

        # NOTE 添加下拉菜单的功能触发
        self.import_json_action.triggered.connect(self.importJsonSetting)
        self.export_json_action.triggered.connect(self.exportJsonSetting)
        self.reset_json_action.triggered.connect(self.resetJsonSetting)

        # NOTE 当设置界面的UI改变时，将数据存储到默认的json路径中
        self.Crop_CB.stateChanged.connect(self.enableCrop)
        self.Horizontal_RB.clicked.connect(partial(self.exportJsonSetting,SETTING_PATH))
        self.Vertical_RB.clicked.connect(partial(self.exportJsonSetting,SETTING_PATH))
        self.Qt_RB.clicked.connect(partial(self.exportJsonSetting,SETTING_PATH))
        self.Maya_RB.clicked.connect(partial(self.exportJsonSetting,SETTING_PATH))
        self.Limit_CB.stateChanged.connect(partial(self.exportJsonSetting,SETTING_PATH))
        self.Width_SP.valueChanged.connect(partial(self.exportJsonSetting,SETTING_PATH))
        self.Height_SP.valueChanged.connect(partial(self.exportJsonSetting,SETTING_PATH))
        self.Fit_SP.valueChanged.connect(partial(self.exportJsonSetting,SETTING_PATH))

        self.setting_data = {}
        if os.path.exists(SETTING_PATH):
            self.importJsonSetting(SETTING_PATH)

    def importJsonSetting(self,path=None):
        """
        importJsonSetting 导入Json
        
        Keyword Arguments:
            path {str} -- 导入路径 为空则弹出选择窗口获取 (default: {None})
        """
        if not path:
            path,_ = QFileDialog.getOpenFileName(self, caption=u"获取设置",filter= u"json (*.json)")
            if not path:return

        # NOTE 如果文件不存在则返回空
        if not os.path.exists(path):return

        with open(path,'r') as f:
            self.setting_data = json.load(f,encoding="utf-8")

        if self.setting_data["Horizontal_RB"]:
            self.Horizontal_RB.setChecked(1)
        else:
            self.Vertical_RB.setChecked(1)

        if self.setting_data["Maya_RB"]:
            self.Maya_RB.setChecked(1)
        else:
            self.Qt_RB.setChecked(1)
        
        self.Crop_CB.setChecked(self.setting_data["Crop_CB"])
        self.Limit_CB.setChecked(self.setting_data["Limit_CB"])
        self.Width_SP.setValue(self.setting_data["Width_SP"])
        self.Height_SP.setValue(self.setting_data["Height_SP"])
        self.Fit_SP.setValue(self.setting_data["Fit_SP"])

    def exportJsonSetting(self,path=None):
        """
        exportJsonSetting 导出Json
        
        Keyword Arguments:
            path {str} -- 导出路径 为空则弹出选择窗口获取 (default: {None})
        """
        if not path:
            path,_ = QFileDialog.getSaveFileName(self, caption=u"输出设置",filter= u"json (*.json)")
            if not path:return
        
        self.setting_data["Horizontal_RB"] = self.Horizontal_RB.isChecked()
        self.setting_data["Maya_RB"]       = self.Maya_RB.isChecked()
        self.setting_data["Crop_CB"]       = self.Crop_CB.isChecked()
        self.setting_data["Limit_CB"]      = self.Limit_CB.isChecked()
        self.setting_data["Width_SP"]      = self.Width_SP.value()
        self.setting_data["Height_SP"]     = self.Height_SP.value()
        self.setting_data["Fit_SP"]        = self.Fit_SP.value()

        try:
            with open(path,'w') as f:
                json.dump(self.setting_data,f,indent=4)
        except:
            QtWidgets.QMessageBox.warning(self, "Warning", "保存失败")

    def resetJsonSetting(self):
        """
        resetJsonSetting 重置设置
        """
        self.Horizontal_RB.setChecked(True)
        self.Maya_RB.setChecked(True)
        self.Crop_CB.setChecked(True)
        self.Limit_CB.setChecked(True)
        self.Width_SP.setValue(500)
        self.Height_SP.setValue(500)
        self.Fit_SP.setValue(0.8)

    def enableCrop(self):
        """
        enableCrop 开启截取并保存设置
        """
        check = self.Crop_CB.isChecked()
        self.Crop_Widget.setEnabled(check)
        self.exportJsonSetting(SETTING_PATH)

    def limitCam(self):
        """
        limitCam 限制只能输出5个摄像机
        """
        check = self.Limit_CB.isChecked()
        cam_panel = self.manager.cam_setting
        count = cam_panel.Cam_Item_Scroll.layout().count()-1
        for i in reversed(range(cam_panel.Cam_Item_Scroll.layout().count())): 
            if i != count and i >= 5:
                item = cam_panel.Cam_Item_Scroll.layout().itemAt(i).widget()
                item.setEnabled(not check)
    
        cam_panel.Add_Cam_BTN.setEnabled(count < 5 or not check)

    def managerSignal(self,manager):
        """
        managerSignal 继承自General类 容器依附到 Maya 窗口后触发事件

        Arguments:
            manager {ViewportCaptureManager} -- 组件管理容器
        """
        func = partial(manager.changeWidgetTo,manager.main)
        self.back_action.triggered.connect(func)
        self.Back_BTN.clicked.connect(func)

        func = partial(manager.changeWidgetTo,manager.cam_setting)
        self.cam_setting_action.triggered.connect(func)

        self.close_action.triggered.connect(manager.window().close)
