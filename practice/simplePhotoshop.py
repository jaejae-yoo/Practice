from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMainWindow,QApplication,qApp,QFileDialog, QRubberBand, QWidget
from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtGui import *
import sys
import cv2
import glob
import os
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt


class Node:
    def __init__(self, item = None, link=None):
        self.item = item
        self.link = link

class circleLinkedlist:
    def __init__(self):
        self.root = Node()
        self.tail = self.root
        self.current = self.root

    def append(self, item):
        newNode = Node(item)
        if self.root.item == None:
            self.root = newNode
            self.tail = newNode
            newNode.link = self.root
            self.current = self.root
        else:
            tmp = self.tail.link
            self.tail.link = newNode
            newNode.link = tmp
            self.tail = newNode

    def listsize(self):
        listSize = 1
        curNode=self.root
        while curNode.link !=self.root:
            curNode=curNode.link
            listSize+=1
        return listSize

    def setCurrent(self, item):
        curNode = self.root
        for num in range(self.listsize()):
            if curNode.item !=item:
                curNode = curNode.link
            else:
                self.current = curNode
                break


    def moveNext(self):
        self.current = self.current.link
        return self.current.item

    def insert(self, item):
        newNode = Node(item)
        tmp1 = self.current.link
        self.current.link = newNode
        newNode.link = tmp1
        if self.current == self.tail:
            self.tail = newNode


    def delete(self, item):
        curNode = self.root
        if self.root.item == item:
            self.root = self.root.link
            self.tail.link = self.root
        else:
            while curNode.link != self.root:
                preNode = curNode
                curNode = curNode.link
                if curNode.item == item:
                    preNode.link = curNode.link
                    if curNode == self.tail:
                        self.tail = preNode

    def getCurrent(self):
        return self.current.item

form_class=loadUiType("ImageViewer.ui")[0]
form_class2 = loadUiType("dialog.ui")[0]

class AnotherWindow(QWidget, form_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class Viewer(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self,parent)
        self.qPixmapVar = QPixmap()
        self.setupUi(self)
        self.idx = 0
        self.frame = None

        self.actionFile_Select.triggered.connect(self.fileselect)
        self.actionFolder_Select.triggered.connect(self.folderselect)
        self.actionmedian.triggered.connect(self.median)
        self.actiongaussian.triggered.connect(self.gaussian)
        self.actioneast.triggered.connect(self.east)
        self.actionwest.triggered.connect(self.west)
        self.actionsouth.triggered.connect(self.south)
        self.actionnorth.triggered.connect(self.north)
        self.actiontoGray.triggered.connect(self.togray)
        self.actionRotation.triggered.connect(self.rotation)
        self.movenextButton.clicked.connect(self.movenext)
        self.actionCrop.triggered.connect(self.crop)
        self.actionon.triggered.connect(self.camera)
        self.pictureButton.clicked.connect(self.picture)
        self.actionexit.triggered.connect(qApp.exit)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.hh = 600
        self.ww = 600
        self.cropEnable = False
        self.cameraon = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
        if self.cropEnable == True:
            self.selStart = self.origin - self.startPos
            self.selEnd = event.pos() - self.startPos
            print(self.origin)
            print(self.startPos)
            #print(self.selStart, self.selEnd)

            cut_begin_x = int(self.img_width_origin*self.selStart.x()/self.img_width_tran)
            cut_begin_y = int(self.img_height_origin * self.selStart.y() / self.img_height_tran)
            cut_end_x = int(self.img_width_origin*self.selEnd.x()/self.img_width_tran)
            cut_end_y = int(self.img_height_origin * self.selEnd.y() / self.img_height_tran)
            self.img = self.img[cut_begin_y:cut_end_y, cut_begin_x:cut_end_x,:].astype('uint8')
            self.img2label(self.img)
            self.cropEnable=False

    def img2label(self, img):
        self.qPixmapVar = QPixmap(self.img2QImage(img))
        self.qPixmapVar = self.qPixmapVar.scaled(self.hh, self.ww, aspectRatioMode=True)
        self.label.setPixmap(self.qPixmapVar)

    def fileselect(self):
        self.fName = QFileDialog.getOpenFileName(self, 'Open file','C:/Users/wotj1/PycharmProjects/software_project/picture', "Image files (*.jpg)")[0]
        self.img = cv2.imread(self.fName)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.img_height_origin = self.img.shape[0]
        self.img_width_origin = self.img.shape[1]
        print(self.img.shape)
        self.img2label(self.img)

    def east(self):
        _tmp = np.zeros((self.img_height_origin, 100, 3))
        self.img = np.concatenate((_tmp, self.img), axis=1)
        self.img = self.img[:, :self.img_width_origin, :].astype('uint8')
        self.img2label(self.img)

    def west(self):
        _tmp = np.zeros((self.img_height_origin, 100, 3))
        self.img = np.concatenate((self.img, _tmp), axis=1)
        self.img = self.img[:, 100:, :].astype('uint8')
        self.img2label(self.img)

    def south(self):
        _tmp = np.zeros((100, self.img_width_origin, 3))
        self.img = np.concatenate((_tmp, self.img), axis=0)
        self.img = self.img[:self.img_height_origin, :, :].astype('uint8')
        self.img2label(self.img)

    def north(self):
        _tmp = np.zeros((100, self.img_width_origin, 3))
        self.img = np.concatenate((self.img, _tmp), axis=0)
        self.img = self.img[100:, :, :].astype('uint8')
        self.img2label(self.img)

    def crop(self):
        self.cropEnable = True
        self.hw_ratio = self.img_height_origin/self.img_width_origin
        #print(self.img_height_origin, self.img_width_origin)

        if self.hw_ratio > 1:
            self.img_height_tran = self.hh
            self.img_width_tran = int(self.img_height_tran/self.img_height_origin*self.img_width_origin)
        else:
            self.img_width_tran=self.ww
            self.img_height_tran=int(self.img_width_tran/ self.img_width_origin*self.img_height_origin)
            print(self.img_height_tran, self.img_width_tran)

        if self.img_width_tran < self.ww:
            self.startPos = QPoint((self.ww-self.img_width_tran) //2, 0)
            self.endPos = QPoint(self.startPos.x() + self.img_width_tran, self.ww)
        else:
            self.startPos = QPoint(0, (self.hh-self.img_height_tran)//2)
            self.endPos = QPoint(self.hh, self.startPos.y()+self.img_height_tran)
        #print( self.startPos, self.endPos)

    def median(self):
        img = cv2.imread(self.fName)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        dst4 = cv2.medianBlur(img, 9)
        image = QImage(dst4, dst4.shape[1], dst4.shape[0], dst4.shape[1] * 3, QImage.Format_RGB888)
        self.qPixmapVar = QPixmap(image)
        self.qPixmapVar = self.qPixmapVar.scaled(700, 400, aspectRatioMode=True)
        self.label.setPixmap(self.qPixmapVar)

    def gaussian(self):
        img = cv2.imread(self.fName)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        dst2 = cv2.GaussianBlur(img,(5,5),0)
        image = QImage(dst2, dst2.shape[1], dst2.shape[0], dst2.shape[1] * 3, QImage.Format_RGB888)
        self.qPixmapVar = QPixmap(image)
        self.qPixmapVar = self.qPixmapVar.scaled(700, 400, aspectRatioMode=True)
        self.label.setPixmap(self.qPixmapVar)


    def folderselect(self):
        self.Imagelist = circleLinkedlist()
        dirName = QFileDialog.getExistingDirectory(self, 'Open Folder', 'C:/Users/wotj1/PycharmProjects/software_project/picture')
        self.files =[]
        for file in glob.glob(os.path.join(dirName, '*.jpg')):
            self.files.append(file)

        self.fName = self.files[0]
        self.testname = self.files[0]

        for file in glob.glob(os.path.join(dirName, '*.jpg')):
            self.Imagelist.append(file)
            self.qPixmapVar = QPixmap(self.file2Image(self.files[0]))
            self.qPixmapVar = self.qPixmapVar.scaled(700, 400, aspectRatioMode=True)
            self.label.setPixmap(self.qPixmapVar)

    #웹캠에서 사진 촬영 후 폴더에 저장
    def camera(self):
        self.frame = None
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while (True):
            ret, self.frame = cap.read()
            if (ret):
                cv2.imshow('frame_color', self.frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                if self.cameraon == True:
                    break
        cap.release()
        cv2.destroyAllWindows()

    def picture(self):
        cv2.imwrite('picture/mypicture.jpg', self.frame, params=[cv2.IMWRITE_PNG_COMPRESSION, 0])
        self.cameraon = True

    def togray(self):
        img = cv2.imread(self.fName)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        r_img = img[:, :, 0]
        g_img = img[:, :, 1]
        b_img = img[:, :, 2]
        imgGray = 0.21*r_img+0.72*g_img+0.07*b_img
        img[:, :, 0] = imgGray
        img[:, :, 1] = imgGray
        img[:, :, 2] = imgGray
        image = QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)

        self.qPixmapVar = QPixmap(image)
        self.qPixmapVar = self.qPixmapVar.scaled(700, 400, aspectRatioMode=True)
        self.label.setPixmap(self.qPixmapVar)

    def rotation(self):
        pass

    def movenext(self):
        self.idx +=1
        self.testname = self.Imagelist.moveNext()
        self.fName = self.testname

        self.qPixmapVar = QPixmap(self.file2Image(self.testname))
        self.qPixmapVar = self.qPixmapVar.scaled(700, 400, aspectRatioMode=True)

        self.label.setPixmap(self.qPixmapVar)

    def img2QImage(self, img):
        return QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)

    def file2Image(self, fname):
        img = cv2.imread(fname)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)

app=QApplication(sys.argv)
myWindow=Viewer(None)
myWindow.show()
app.exec_()