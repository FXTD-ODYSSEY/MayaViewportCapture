# coding:utf-8
from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from Qt.QtCompat import loadUi
from Qt.QtCompat import wrapInstance
from Qt.QtCompat import QFileDialog
import webbrowser
import os

DIR = os.path.dirname(__file__)
INSTRUNCTION_PATH = "file:///%s" % os.path.join(DIR,"instruction","README.html")

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