import serial
import socket
import os
import binascii
import time
import re
import numpy as np
import sys



ip = '192.168.111.204'
port = 5600
iteration = 10000    #收取数据包数目
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建套接字
udp_socket.bind((ip, port))  # 绑定本地的相关信息        
save_path = 'E:\Test'



def writetxt(iteration,distanceTrue):
    dis = '%.3f' % distanceTrue
    files = save_path + "\\" + dis + '.txt'
    print(files)
    file = open(files, 'w')
    data = []
    for n in range(iteration):
        sock_data, server_addr = udp_socket.recvfrom(1500)  # UDP接收
        data.append(sock_data)
    for n in range(iteration):
        sock = data[n]  # 1个UDP包1120B
        for i in range(8):  # 2个角度，8根16线单元；每跟16线单元140Byte
            sub_sock = sock[140 * i:140 * i + 140]
            flag_sock = sub_sock[136]
            #print(type(flag_sock))
            hor_angle_tem = sub_sock[128:132]
            hor_angle = int.from_bytes(hor_angle_tem, byteorder='big', signed=False) / 100000
            if 91 >= hor_angle >= 89:
                if flag_sock == 0:
                    #print(flag_sock)
                    for j in range(16):
                        width_tem = sub_sock[2 + j * 8:4 + j * 8]
                        #print(width_tem)
                        distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                        width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                        distance = float(format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,'.5f'))
                        file.writelines('Channel: ' + str(j + 1) + ' Angle: ' + str(hor_angle) + ' Distance: ' + str(distance) + ' PulseWidth: ' + str(width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
                elif flag_sock == 64:
                    #print(flag_sock)
                    for j in range(16):
                        width_tem = sub_sock[2 + j * 8:4 + j * 8]
                        distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                        width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                        distance = float(
                            format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,
                                   '.5f'))
                        file.writelines('Channel: ' + str(j + 17) + ' Angle: ' + str(hor_angle) + ' Distance: ' \
                                        + str(distance) + ' PulseWidth: ' + str(width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
                elif flag_sock == 128:
                    #print(flag_sock)
                    for j in range(16):
                        width_tem = sub_sock[2 + j * 8:4 + j * 8]
                        distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                        width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                        distance = float(
                            format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,
                                   '.5f'))
                        file.writelines('Channel: ' + str(j + 33) + ' Angle: ' + str(hor_angle) + ' Distance: ' \
                                        + str(distance) + ' PulseWidth: ' + str(width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
                elif flag_sock == 192:
                    #print(flag_sock)
                    for j in range(16):
                        width_tem = sub_sock[2 + j * 8:4 + j * 8]
                        distance_tem = sub_sock[0 + j * 8:2 + j * 8]
                        width = int.from_bytes(width_tem, byteorder='big', signed=False) * 0.004574468
                        distance = float(
                            format(int.from_bytes(distance_tem, byteorder='big', signed=False) * 0.004574468,
                                   '.5f'))
                        file.writelines('Channel: ' + str(j + 49) + ' Angle: ' + str(hor_angle) + ' Distance: ' \
                                        + str(distance) + ' PulseWidth: ' + str(width) + ' Temp: 0.7 HighV: 92.7 SubV: 384' + '\n')
    file.close()

if not os.path.exists(save_path):
    os.makedirs(save_path)
    os.chdir(save_path)
else:
    print("目录已存在")
    os.chdir(save_path)
distanceTrue = 1
writetxt(iteration,distanceTrue)

        