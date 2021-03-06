# coding:utf-8

import os
from functools import partial
import pymel.core as pm

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from Qt.QtCompat import loadUi

DIR = os.path.dirname(__file__)

class ViewportCaptureCameraSettingItem(QtWidgets.QWidget):
    """
    ViewportCaptureCameraSettingItem 摄像机设置界面的摄像机Item
    """
    def __init__(self,cam,widget):
        super(ViewportCaptureCameraSettingItem,self).__init__()
        ui_file = os.path.join(DIR,"ui","item.ui")
        loadUi(ui_file,self)

        self.widget = widget
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
        """
        loadCamData 根据当前摄像机属性修改UI数值
        """
        self.Cam_BTN.setText(self.cam.name())
        self.TX_SP.setValue(self.cam.tx.get())
        self.TY_SP.setValue(self.cam.ty.get())
        self.TZ_SP.setValue(self.cam.tz.get())
        self.RX_SP.setValue(self.cam.rx.get())
        self.RY_SP.setValue(self.cam.ry.get())
        self.RZ_SP.setValue(self.cam.rz.get())
        self.Orthographic_CB.setChecked(self.cam.orthographic.get())
        
    def deleteLater(self):
        """
        deleteLater 删除自身并将 数据也清空
        """
        super(ViewportCaptureCameraSettingItem,self).deleteLater()
        del self.cam.setting[self.cam.name()]
        # NOTE 刷新页面
        self.widget.showProcess()


    def orthographicState(self,check):
        """
        orthographicState 当正交复选框发生修改
        
        Arguments:
            check {int} -- 复选框勾选为2不勾选为0
        """
        check = False if check == 0 else True
        self.cam.orthographic.set(check)

    def txValueChange(self,value):
        """txValueChange 位移x修改
        
        Arguments:
            value {int} -- spinbox数值
        """
        self.setting["translate"][0] = value
        self.cam.tx.set(value)

    def tyValueChange(self,value):
        """
        tyValueChange 位移y修改
        
        Arguments:
            value {int} -- spinbox数值
        """
        self.setting["translate"][1] = value
        self.cam.ty.set(value)

    def tzValueChange(self,value):
        """
        tzValueChange 位移z修改
        
        Arguments:
            value {int} -- spinbox数值
        """
        self.setting["translate"][2] = value
        self.cam.tz.set(value)

    def rxValueChange(self,value):
        """
        rxValueChange 旋转x修改
        
        Arguments:
            value {int} -- spinbox数值
        """
        self.setting["rotate"][0] = value
        self.cam.rx.set(value)

    def ryValueChange(self,value):
        """
        ryValueChange 旋转y修改
        
        Arguments:
            value {int} -- spinbox数值
        """
        self.setting["rotate"][1] = value
        self.cam.ry.set(value)

    def rzValueChange(self,value):
        """
        rzValueChange 旋转z修改
        
        Arguments:
            value {int} -- spinbox数值
        """
        self.setting["rotate"][2] = value
        self.cam.rz.set(value)

    