import serial
import socket
import os
import binascii
import time
import re
import numpy as np
import sys
from meas import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSlot

text1 = binascii.a2b_hex('010600110000D9CF')  # 关闭仪器
text2 = binascii.a2b_hex('010600110002580E')  # 启动连续测量
text3 = binascii.a2b_hex('01060010000149CF')  # 一次测量（没有启动作用）
text4 = binascii.a2b_hex('010300150002D5CF')  # 获取距离数据
text5 = binascii.a2b_hex('02050003FF007C09')  # car go
text6 = binascii.a2b_hex('0205000300003DF9')  # car stop
text7 = binascii.a2b_hex('020500000000CDF9')  # forward(default)
text8 = binascii.a2b_hex('02050000FF008C09')  # reverse
text9 = binascii.a2b_hex('0205000100009C39')  # low speed(default)
text10 = binascii.a2b_hex('02050001FF00DDC9')  # middle speed
text11 = binascii.a2b_hex('02050002FF002DC9')  # high speed on
text12 = binascii.a2b_hex('0205000200006C39')  # high speed off
down_limit = 0.12   #前进停止距离
slow_limit = 0.4    #前进减速距离
init_distance = 7.1 #后退停止距离

class Qmymeas(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)   # 调用父类构造函数，创建窗体
        self.ui=Ui_MainWindow()     # 创建UI对象
        self.ui.setupUi(self)      # 构造UI界面

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
      #print("test_hahah")
      self.ui.config_path = QFileDialog.getOpenFileName(self, "getOpenFileName","./","All Files (*);;Text Files (*.txt)")    # 获取文本路径本路径
      self.ui.lineEdit_2.clear()
      self.ui.lineEdit_2.setText(str(self.ui.config_path))

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        print("test_hahah")
        file = open(str(self.ui.config_path[0]))
        for line in file:
            line_mod = line.replace(' ','')
            if 'COM' in line_mod:
                oneline = re.split('=|\n', line_mod)
                ports = 'COM' + oneline[1]
            elif 'save_path' in line:
                oneline = re.split('=|\n', line_mod)
                save_path = oneline[1]  #标定数据文件存储路径/
        bps = 9600
        timex = 0.5
        ser = serial.Serial(ports, bps, timeout=timex)

        ip = '192.168.111.204'
        port = 5600
        iteration = 17000    #收取数据包数目
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建套接字
        udp_socket.bind((ip, port))  # 绑定本地的相关信息

        def measurement():
            ser.readline()
            time.sleep(0.1)
            ser.write(text2)
            time.sleep(0.2)
            ser.readline()
            time.sleep(0.1)
            ser.write(text4)
            time.sleep(0.1)
            tem = ser.read(9).hex()
            time.sleep(0.1)
            print(tem)
            measure1 = tem[-12:-4]
            measure = round(int(measure1,16)/10000, 4)+0.02 #实际激光雷达距墙距离
            print(measure)
            ser.write(text1)
            time.sleep(0.1)
            ser.readline()
            return measure

        def writetxt(iteration, distanceTrue):
            dis = '%.3f' % distanceTrue
            files = save_path + "\\" + dis + '.txt'
            print(files)
            file = open(files, 'w')
            data = []
            for n in range(iteration):
                sock_data, server_addr = udp_socket.recvfrom(15000)  # UDP接收
                data.append(sock_data)
            for n in range(iteration):
                sock = data[n]  # 1个UDP包1120B
                for i in range(8):  # 2个角度，8根16线单元；每跟16线单元140Byte
                    sub_sock = sock[140 * i:140 * i + 140]
                    flag_sock = sub_sock[136]
                    # print(type(flag_sock))
                    hor_angle_tem = sub_sock[128:132]
                    hor_angle = int.from_bytes(hor_angle_tem, byteorder='big', signed=False) / 100000
                    if 91 >= hor_angle >= 89:
                        if flag_sock == 0:
                            # print(flag_sock)
                            for j in range(16):
                                width_tem = sub_sock[2 + j * 8:4 + j * 8]
                                # print(width_tem)
                                distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                                width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                                distance = float(
                                    format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,
                                           '.5f'))
                                file.writelines(
                                    'Channel: ' + str(j + 1) + ' Angle: ' + str(hor_angle) + ' Distance: ' + str(
                                        distance) + ' PulseWidth: ' + str(
                                        width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
                        elif flag_sock == 64:
                            # print(flag_sock)
                            for j in range(16):
                                width_tem = sub_sock[2 + j * 8:4 + j * 8]
                                distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                                width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                                distance = float(
                                    format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,
                                           '.5f'))
                                file.writelines('Channel: ' + str(j + 17) + ' Angle: ' + str(hor_angle) + ' Distance: ' \
                                                + str(distance) + ' PulseWidth: ' + str(
                                    width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
                        elif flag_sock == 128:
                            # print(flag_sock)
                            for j in range(16):
                                width_tem = sub_sock[2 + j * 8:4 + j * 8]
                                distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                                width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                                distance = float(
                                    format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,
                                           '.5f'))
                                file.writelines('Channel: ' + str(j + 33) + ' Angle: ' + str(hor_angle) + ' Distance: ' \
                                                + str(distance) + ' PulseWidth: ' + str(
                                    width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
                        elif flag_sock == 192:
                            # print(flag_sock)
                            for j in range(16):
                                width_tem = sub_sock[2 + j * 8:4 + j * 8]
                                distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                                width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                                distance = float(
                                    format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,
                                           '.5f'))
                                file.writelines('Channel: ' + str(j + 49) + ' Angle: ' + str(hor_angle) + ' Distance: ' \
                                                + str(distance) + ' PulseWidth: ' + str(
                                    width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
            file.close()

        if not os.path.exists(save_path):
            os.makedirs(save_path)
            os.chdir(save_path)
        else:
            print("目录已存在")
            os.chdir(save_path)

        flag = 1    #前进
        distanceTrue = measurement()
        distanceTrue = measurement()
        if distanceTrue < down_limit:
            flag = 0    #后退
        while True:
            if flag == 1:
                if distanceTrue > slow_limit:
                    writetxt(iteration,distanceTrue)
                    ser.write(text5)
                    time.sleep(0.1)
                    ser.readline()
                    time.sleep(0.2)
                    ser.write(text6)
                    time.sleep(1.5)
                    ser.readline()
                    time.sleep(0.1)
                    distanceTrue = measurement()
                    distanceTrue = measurement()
                    if distanceTrue < down_limit:
                        flag = 0
                else:
                    writetxt(iteration,distanceTrue)
                    ser.write(text9)    #降速，存疑
                    time.sleep(0.1)
                    ser.readline()
                    ser.write(text6)
                    time.sleep(1.5)
                    ser.readline()
                    time.sleep(0.1)
                    distanceTrue = measurement()
                    distanceTrue = measurement()
                    if distanceTrue < down_limit:
                        flag = 0
            else:
                writetxt(iteration,distanceTrue)
                break
        udp_socket.close()
        ser.write(text8)  # 反向
        time.sleep(0.1)
        ser.readline()
        ser.write(text5)  # GO
        time.sleep(0.1)
        ser.readline()
        distanceTrue = measurement()
        while distanceTrue < init_distance:
            distanceTrue = measurement()
        ser.write(text6)  # STOP
        time.sleep(1)
        ser.readline()
        ser.write(text7)  # 正向
        time.sleep(0.1)
        ser.readline()
        ser.close()
        print('Finish')

if  __name__ == "__main__":
   app = QApplication(sys.argv)
   form=Qmymeas()
   form.show()
   sys.exit(app.exec_())
   #app.exec_()