# coding:utf-8
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets
import os
import ctypes

class ImageUtil(object):
    
    def __init__(self):
        pass
    
    def getActiveM3dViewImage(self):
        '''
        getActiveM3dViewImage 获取当前 Viewport 视窗截图
        
        Returns:
            [MImage] -- 当前视窗截图
        '''

        # NOTE 通过 API 获取 viewport
        viewport = OpenMayaUI.M3dView.active3dView()
        viewport.refresh()

        # NOTE 获取 viewport 中缓存的渲染图
        img = OpenMaya.MImage()
        viewport.readColorBuffer(img, True)
        return img

    def getImagePixel(self,image,number=True):
        u'''
        getImagePixel 获取MImage像素

        Arguments:
            image {MImage} -- Maya API的图片对象

        Returns:
            [list] -- 像素序列
        '''
        width, height = image.getSize()

        # NOTE https://gist.github.com/hmasato/b72a95fbadf1c63b56ec
        pxiel = image.pixels().__long__()
        ptr = ctypes.cast(pxiel, ctypes.POINTER(ctypes.c_char))
        size = width * height * 4
        # NOTE ord将字符转换为 0 - 255 ASCII码区间
        if number:
            return [ord(char) for char in ctypes.string_at(ptr, size)]
        else:
            return ctypes.string_at(ptr, size)

class MayaImageUtil(ImageUtil):
    
    def __init__(self):
        pass
    
    def cropImage(self,image, x=0, y=0, width=100, height=100):
        u'''
        cropImage 图片裁剪

        Arguments:
            image {MImage} --  Maya API的图片对象

        Keyword Arguments:
            x {int} -- 裁剪起始像素 (default: {0})
            y {int} -- 裁剪结束像素 (default: {0})
            width {int} -- 宽度 (default: {200})
            height {int} -- 高度 (default: {200})

        Returns:
            [MImage] -- 裁剪的图像
            * None -- 报错返回空值
        '''

        img_width, img_height = image.getSize()

        # NOTE 如果数值不合法则返回 None
        if width <= 0 or height <= 0 or x < 0 or y < 0:
            print u"输入值不合法"
            return

        # NOTE 如果裁剪区域超过原图范围则限制到原图的边界上
        if x+width > img_width:
            width = img_width - x
        if y+height > img_height:
            height = img_height - y

        origin_pixels = self.getImagePixel(image)

        # NOTE https://groups.google.com/forum/#!topic/python_inside_maya/Q9NuAd6Av20
        pixels = bytearray(width*height*4)
        for _i, i in enumerate(range(x, x+width)):
            for _j, j in enumerate(range(y, y+height)):
                # NOTE 分别获取当前像素的坐标
                _pos = (_i+_j*width)*4
                pos = (i+j*img_width)*4
                # NOTE 这里加数字代表当前像素下 RGBA 四个通道的值
                pixels[_pos+0] = origin_pixels[pos+0]
                pixels[_pos+1] = origin_pixels[pos+1]
                pixels[_pos+2] = origin_pixels[pos+2]
                pixels[_pos+3] = origin_pixels[pos+3]

        # NOTE 返回裁剪的 Image
        img = OpenMaya.MImage()
        img.setPixels(pixels, width, height)
        return img

    def centerCropImage(self,image,width=500,height=500):
        '''
        centerCropImage 居中裁切图片 改变图片的长宽比
        
        Arguments:
            image {MImage} --  Maya API的图片对象
        
        Keyword Arguments:
            width {int} -- 宽度 (default: {200})
            height {int} -- 高度 (default: {200})
        
        Returns:
            [MImage] -- 裁剪的图像
            * None -- 报错返回空值
        '''

        img_width, img_height = image.getSize()
        x = img_width/2 - width/2
        y = img_height/2 - height/2
        return self.cropImage(image,x,y,width,height)


    def mergeImage(self,image_list,horizontal=True):
        '''
        mergeImage 图片合成
        
        Arguments:
            image_list {list} -- Maya API的图片对象组成的数组
        
        Keyword Arguments:
            horizontal {bool} -- True为横向排列 False为纵向排列  (default: {True})
        
        Returns:
            [MImage] -- 合成的图像
        '''

        # NOTE 获取图片数组的长宽及像素数据
        img_width_list = []
        img_height_list = []
        img_pixels_list = []
        for image in image_list:
            img_width, img_height = image.getSize()
            img_pixels = self.getImagePixel(image)
            img_width_list.append(img_width)
            img_height_list.append(img_height)
            img_pixels_list.append(img_pixels)

        # NOTE 获取图片数组的长宽及像素数据
        total_width = sum(img_width_list) if horizontal else max(img_width_list)
        total_height = max(img_height_list) if horizontal else sum(img_height_list)
        
        # NOTE 初始化变量
        pixels = bytearray(total_width*total_height*4)
        width = 0
        height = 0
        width_list = []
        height_list = []
        for _width,_height,_pixels in zip(img_width_list,img_height_list,img_pixels_list):
            # NOTE 纵向和横向不同的循环模式
            if horizontal:
                width_list = range(width,width+_width)
                height_list = range(_height)
                width += _width
            else:
                height_list = range(height,height+_height)
                width_list = range(_width)
                height += _height

            # NOTE 循环获取像素
            for _i,i in enumerate(width_list):
                for _j,j in enumerate(height_list):
                    _pos = (_i+_j*_width)*4
                    pos = (i+j*total_width)*4
                    pixels[pos+0] = _pixels[_pos+0]
                    pixels[pos+1] = _pixels[_pos+1]
                    pixels[pos+2] = _pixels[_pos+2]
                    pixels[pos+3] = _pixels[_pos+3]

        # NOTE 返回合成的图像
        img = OpenMaya.MImage()
        img.setPixels(pixels, total_width, total_height)
        return img
    
class QtImageUtil(ImageUtil):

    def __init__(self):
        pass
    
    def getActiveM3dViewImage(self):
        image = super(QtImageUtil,self).getActiveM3dViewImage()
        return self.getQIamge(image)

    def getQIamge(self,image):
        """getQIamge 将 MImage 的数据 转换为 QImage
        
        Arguments:
            image {MImage} --  Maya API的图片对象
        
        Returns:
            [QImage] -- Qt的图片对象
        """     

        # NOTE https://forums.autodesk.com/t5/maya-programming/maya-2016-grabbing-m3dview-with-python/td-p/5979432

        width, height = image.getSize()
        # NOTE 获取 MImage 的像素数据
        ptr = self.getImagePixel(image,False)
        img = QtGui.QImage(ptr, width, height, QtGui.QImage.Format_ARGB32)
        img = img.mirrored(horizontal=False, vertical=True)
        return img
    
    def cropImage(self,image, x=0, y=0, width=100, height=100):
        u'''
        cropImage 图片裁剪

        Arguments:
            image {QImage} --  Qt 的图片对象

        Keyword Arguments:
            x {int} -- 裁剪起始像素 (default: {0})
            y {int} -- 裁剪结束像素 (default: {0})
            width {int} -- 宽度 (default: {200})
            height {int} -- 高度 (default: {200})

        Returns:
            [QImage] -- 裁剪的图像
        '''

        rect = QtCore.QRect(x, y, width, height)
        return image.copy(rect)

    def centerCropImage(self,image,width=500,height=500):
        u'''
        centerCropImage 居中裁切图片 改变图片的长宽比
        
        Arguments:
            image {QImage} --  Qt 的图片对象
        
        Keyword Arguments:
            width {int} -- 宽度 (default: {200})
            height {int} -- 高度 (default: {200})
        
        Returns:
            [QImage] -- 裁剪的图像
        '''

        img_width, img_height = image.width(),image.height()
        x = img_width/2 - width/2
        y = img_height/2 - height/2
        return self.cropImage(image,x,y,width,height)

    def mergeImage(self,image_list,horizontal=True):
        '''
        mergeImage 图片合成
        
        Arguments:
            image_list {list} -- QImage的图片对象组成的数组
        
        Keyword Arguments:
            horizontal {bool} -- True为横向排列 False为纵向排列  (default: {True})
        
        Returns:
            [QImage] -- 合成的图像
        '''

        # NOTE 获取图片数组的长宽及像素数据
        img_width_list = []
        img_height_list = []
        for image in image_list:
            img_width_list.append(image.width())
            img_height_list.append(image.height())

        # NOTE 获取图片数组的长宽及像素数据
        total_width = sum(img_width_list) if horizontal else max(img_width_list)
        total_height = max(img_height_list) if horizontal else sum(img_height_list)
        

        painter = QtGui.QPainter()
        _image = QtGui.QImage(total_width, total_height, QtGui.QImage.Format_ARGB32)
        # TODO 采样第一张图片的第一个像素颜色作为背景颜色 如果背景为渐变蓝色无法输出正确的颜色 
        # TODO 数据丢失问题 https://stackoverflow.com/questions/22023296/avoid-color-quantization-when-painting-translucent-colors-in-qt?noredirect=1&lq=1
        _image.fill(QtGui.QColor(image_list[0].pixel(0,0)))
        painter.begin(_image)

        width = 0 
        height = 0
        for _width,_height in zip(img_width_list,img_height_list):
            
            # NOTE 根据给定的左上角坐标 将图片覆盖到 _image 上
            painter.drawImage(width,height,image)

            # NOTE 纵向和横向 数值叠加
            if horizontal:
                width += _width
                height = 0
            else:
                width = 0
                height += _height

        painter.end()

        return _image

DIR = os.path.dirname(__file__)

def maya_test():
    
    util = MayaImageUtil()
    img = util.getActiveM3dViewImage()
    img = util.centerCropImage(img)
    if img:
        output = os.path.join(DIR, "viewport.jpg")
        img.writeToFile(output, 'jpg')

def qt_test():
    
    util = QtImageUtil()
    img = util.getActiveM3dViewImage()
    img = util.centerCropImage(img)

    output = os.path.join(DIR, "viewport2.jpg")

    img.save(output,format = 'jpg')
