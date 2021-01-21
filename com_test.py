# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 11:47:20 2020

@author: miaok
"""
import serial
import serial.tools.list_ports
import binascii
import time
from ld import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog,QMainWindow)
from PyQt5.QtCore import Qt, pyqtSlot
import sys


class Qmyld(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)   # 调用父类构造函数，创建窗体
        self.ui=Ui_MainWindow()     # 创建UI对象
        self.ui.setupUi(self)      # 构造UI界面

    @pyqtSlot()
    def on_pushButton_3_clicked(self):  # 查询COM口
      #print("test_hahah")
      self.ui.plist = list(serial.tools.list_ports.comports())
      for i in range(len(self.ui.plist)):
        print(self.ui.plist[i])
      # self.ui.config_path = QFileDialog.getOpenFileName(self, "getOpenFileName","./","All Files (*);;Text Files (*.txt)")    # 获取文本路径本路径
      self.ui.lineEdit_2.clear()
      self.ui.lineEdit_2.setText(str(self.ui.plist[0])[0:4])
      self.ui.com = str(self.ui.plist[0])[0:4]

    @pyqtSlot()
    def on_pushButton_2_clicked(self):  # 获得测距值
        #print('hehe')
        portx = self.ui.com
        bps=9600
        timex=0.5
        ser=serial.Serial(portx,bps,timeout=timex)
        text1=binascii.a2b_hex('010600110000D9CF')#关闭仪器
        text2=binascii.a2b_hex('010600110002580E')#连续测量
        text3=binascii.a2b_hex('01060010000149CF')#启动一次测量
        text4=binascii.a2b_hex('010300150002D5CF')#获取距离数据
        ser.write(text2)
        time.sleep(0.2)
        y=ser.readline()
        time.sleep(0.2)
        ser.write(text4)
        time.sleep(0.2)
        x=ser.read(9).hex()
        y=ser.readline()
        ser.write(text4)
        time.sleep(0.2)
        x = ser.read(9).hex()
        y = ser.readline()
        ser.write(text1)
        ser.close()
        distance = x[-12:-4]
        distance = int(distance,16)/10000
        #print(distance)
        self.ui.lineEdit_5.clear()
        self.ui.lineEdit_5.setText(str(distance))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Qmyld()
    form.show()
    sys.exit(app.exec_())
    #app.exec_()