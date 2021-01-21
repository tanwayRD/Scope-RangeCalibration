import os
import numpy as np
import matplotlib
import re
from scipy.interpolate import interp1d
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import math


leftbound = np.zeros(64).tolist()    #通过config手动更改可改变盲区
path = 'E:\Test'

save_path = path + '/output_1'
if os.path.exists(save_path):
    print('目录已存在')
else:
    #os.makedirs(save_path)
    os.mkdir(save_path)

blind = 0.3
cos = np.arange(-12.5,12.5,25/64)
count2dis = 0.004574468994
leftbound_man = np.zeros(64).tolist()
rightbound = np.zeros(64).tolist()
txt_list=[]

for file in os.listdir(path):
    if file.endswith(".txt"):
        txt_list.append(file)
txt_list = sorted(txt_list, key=lambda x: float(x[:-4]))

raw_distance = []
raw_pulsewidth = []
filter_distance = []
filter_pulsewidth = []

for i in range(len(txt_list)):
    raw_distance.append([])
    raw_pulsewidth.append([])
    filter_distance.append([])
    filter_pulsewidth.append([])
    for j in range(64):
        raw_distance[i].append([])
        raw_pulsewidth[i].append([])
        filter_distance[i].append([])
        filter_pulsewidth[i].append([])
true_distance = []

filter_distance_mean = []
filter_pulsewidth_mean = []
residual_dis = []
for i in range(64):
    filter_distance_mean.append([])
    filter_pulsewidth_mean.append([])
    residual_dis.append([])
for i in range(len(txt_list)):
    rawdata_textname = txt_list[i]
    dis = float(rawdata_textname[0:5])
    true_distance.append(dis)
    rawdata_textname = path + '/' + rawdata_textname
    file = open(rawdata_textname)
    for line in file:
        oneline = re.split(' ',line)
        channel = int(oneline[1])
        angle = float(oneline[3])
        distance = float(oneline[5])
        pulse = float(oneline[7])
        if 0 < distance < 10 and 0 < pulse < 8:
            raw_distance[i][channel-1].append(distance)
            raw_pulsewidth[i][channel-1].append(pulse)
for i in range(len(txt_list)):
    for j in range(64):
        dis_mean = np.mean(raw_distance[i][j],axis = 0)
        dis_std = np.std(raw_distance[i][j],axis = 0 , ddof = 1)
        pul_mean = np.mean(raw_pulsewidth[i][j],axis = 0)
        pul_std = np.std(raw_pulsewidth[i][j], axis=0, ddof = 1)
        if  dis_std * 3 < 0.014:
            Outer_d = 0.014
        else:
            Outer_d = dis_std * 3
        if  pul_std * 3 < 0.014:
            Outer_p = 0.014
        else:
            Outer_p = pul_std * 3
        for k in range(len(raw_distance[i][j])):
            if abs(raw_distance[i][j][k] - dis_mean) < Outer_d and abs(raw_pulsewidth[i][j][k] - pul_mean) < Outer_p:   #脉宽标准差如何定？
                filter_distance[i][j].append(raw_distance[i][j][k])
                filter_pulsewidth[i][j].append(raw_pulsewidth[i][j][k])
for i in range(len(txt_list)):
    for j in range(64):
        filter_distance_mean[j].append(np.mean(filter_distance[i][j]))
        filter_pulsewidth_mean[j].append(np.mean(filter_pulsewidth[i][j]))

for i in range(64):
    for j in range(0, len(true_distance)):
        residual_dis[i].append(filter_distance_mean[i][j] - true_distance[j]/math.cos(cos[i]/180*math.pi))
        #print(residual_dis[i])
for i in range(len(true_distance)):
    if true_distance[i] > blind:
        blind_position = i
        break
for i in range(64):
    if leftbound[i] == 0:
        for j in range(blind_position,len(true_distance)):
            if filter_distance_mean[i][j] > 0:
                leftbound[i] = int(np.ceil(filter_distance_mean[i][j]/count2dis))
                break
    else:
        for j in range(len(true_distance)):
            if true_distance[j] > leftbound[i]:
                leftbound[i] = int(np.ceil(filter_distance_mean[i][j] / count2dis))
                break
peak = []   #找极值
for i in range(64):
    peak.append(0)

for i in range(64):
    for j in range(1, len(true_distance)-1):
        if filter_distance_mean[i][j] > filter_distance_mean[i][j-1] and filter_distance_mean[i][j] > filter_distance_mean[i][j+1]:
            peak[i] = j
            break
for i in range(64):
    if peak[i] != 0:
        for j in range(peak[i], len(true_distance)-1):
            if filter_distance_mean[i][j] < filter_distance_mean[i][peak[i]] and filter_distance_mean[i][j+1] > filter_distance_mean[i][peak[i]]:
                leftbound_man[i] = math.ceil(filter_distance_mean[i][j+2]/count2dis)
    kt_0 = plt.figure(0, figsize=(20, 10))
    if i <16 :
        guit = kt_0.add_subplot(4, 4, i + 1)
        guit.plot(true_distance,filter_distance_mean[i], 'r-o', markersize=3, linewidth=1)
        plt.xlim((0, 8))
        guit.grid(True)
        guit.set_xlabel('True Distance/m', fontsize = 12)
        guit.set_ylabel('Scope/m', fontsize = 12)
        title = 'Scope vs Laser Channel ' + str(i+1)
        plt.title(title, fontsize = 12)
        plt.subplots_adjust(left = 0.04, bottom = 0.04, right = 0.96, top = 0.96, wspace = 0.3, hspace = 0.5)
        if i == 15:
            pic_save_file =  save_path + '/#-SCP vs LD linear estimate1.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            plt.savefig(pic_save_file,  dpi=300)
            plt.show()
            plt.close()
            continue

    kt_1 = plt.figure(1, figsize=(20, 10))
    if i >15 and i < 32:
        guit = kt_1.add_subplot(4, 4, i - 15)
        guit.plot(true_distance,filter_distance_mean[i], 'r-o', markersize=3, linewidth=1)
        plt.xlim((0, 8))
        guit.grid(True)
        guit.set_xlabel('True Distance/m', fontsize = 12)
        guit.set_ylabel('Scope/m', fontsize = 12)
        title = 'Scope vs Laser Channel ' + str(i+1)
        plt.title(title, fontsize = 12)
        plt.subplots_adjust(left = 0.04, bottom = 0.04, right = 0.96, top = 0.96, wspace = 0.3, hspace = 0.5)
        if i == 31:
            pic_save_file =  save_path + '/#-SCP vs LD linear estimate2.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            plt.savefig(pic_save_file,  dpi=300)
            plt.show()
            plt.close()
            continue

    kt_2 = plt.figure(2, figsize=(20, 10))
    if i > 31 and i < 48:
        guit = kt_2.add_subplot(4, 4, i - 31)
        guit.plot(true_distance,filter_distance_mean[i], 'r-o', markersize=3, linewidth=1)
        plt.xlim((0, 8))
        guit.grid(True)
        guit.set_xlabel('True Distance/m', fontsize = 12)
        guit.set_ylabel('Scope/m', fontsize = 12)
        title = 'Scope vs Laser Channel ' + str(i+1)
        plt.title(title, fontsize = 12)
        plt.subplots_adjust(left = 0.04, bottom = 0.04, right = 0.96, top = 0.96, wspace = 0.3, hspace = 0.5)
        if i == 47:
            pic_save_file =  save_path + '/#-SCP vs LD linear estimate3.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            plt.savefig(pic_save_file,  dpi=300)
            plt.show()
            plt.close()
            continue

    kt_3 = plt.figure(3, figsize=(20, 10))
    if i > 47:
        guit = kt_3.add_subplot(4, 4, i - 47)
        guit.plot(true_distance,filter_distance_mean[i], 'r-o', markersize=3, linewidth=1)
        plt.xlim((0, 8))
        guit.grid(True)
        guit.set_xlabel('True Distance/m', fontsize = 12)
        guit.set_ylabel('Scope/m', fontsize = 12)
        title = 'Scope vs Laser Channel ' + str(i+1)
        plt.title(title, fontsize = 12)
        plt.subplots_adjust(left = 0.04, bottom = 0.04, right = 0.96, top = 0.96, wspace = 0.3, hspace = 0.5)
        if i == 63:
            pic_save_file =  save_path + '/#-SCP vs LD linear estimate4.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            plt.savefig(pic_save_file,  dpi=300)
            plt.show()
            plt.close()
            continue

fit_total = []
index_start_modified = []
index_end_modified = []
values = np.array(residual_dis)
samples = np.array(filter_distance_mean)
for i in range(64):
    sub_sample = samples[i][~np.isnan(values[i])]/count2dis
    sub_value = values[i][~np.isnan(values[i])]/count2dis
    index_start = int(math.ceil(np.min(sub_sample)))
    index_end = int(math.floor(np.max(sub_sample)))

    index_start = max([leftbound[i],index_start])
    if leftbound_man[i] > index_start:
        index_start = leftbound_man[i]
    if rightbound[i] != 0:
        index_end = rightbound[i]
    index_start_modified.append(index_start)
    index_end_modified.append(index_end)
    queries = range(index_start, index_end + 1)
    slinear_func = interp1d(sub_sample, sub_value, kind='slinear')
    fit_y = slinear_func(queries)
    fit_y_int = np.rint(fit_y)
    fit_total.append(fit_y_int)
    if i < 16:
        kt_4 = plt.figure(4, figsize=(20, 10))
        guit = kt_4.add_subplot(4, 4, i + 1)
        guit.scatter(sub_sample*count2dis, sub_value*count2dis, alpha=1, s=100, c='r', marker='*')
        guit.plot(np.array(queries)*count2dis, fit_y_int*count2dis, linewidth=0.05, color='b', marker='.')
        guit.set_xlabel('Scope Distance Output/m', fontsize=12)
        guit.set_ylabel('Compensation Values/m', fontsize=12)
        title = 'Residual Count   Channel ' + str(i + 1)
        plt.title(title, fontsize=12)
        if i == 15:
            kt_4.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96, wspace=0.3, hspace=0.5)
            pic_save_file = save_path + '/' +  '#-slinear interpolation1.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            kt_4.savefig(pic_save_file)
            plt.show()
            plt.close()
            continue
    elif i >15 and i <32:
        kt_5 = plt.figure(5, figsize=(20, 10))
        guit = kt_5.add_subplot(4, 4, i - 15)
        guit.scatter(sub_sample*count2dis, sub_value*count2dis, alpha=1, s=100, c='r', marker='*')
        guit.plot(np.array(queries)*count2dis, fit_y_int*count2dis, linewidth=0.05, color='b', marker='.')
        guit.set_xlabel('Scope Distance Output/m', fontsize=12)
        guit.set_ylabel('Compensation Values/m', fontsize=12)
        title = 'Residual Count   Channel ' + str(i + 1)
        plt.title(title, fontsize=12)
        if i == 31:
            kt_5.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96, wspace=0.3, hspace=0.5)
            pic_save_file = save_path + '/' +  '#-slinear interpolation2.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            kt_5.savefig(pic_save_file)
            plt.show()
            plt.close()
            continue
    elif i >31 and i <48:
        kt_6 = plt.figure(6, figsize=(20, 10))
        guit = kt_6.add_subplot(4, 4, i - 31)
        guit.scatter(sub_sample*count2dis, sub_value*count2dis, alpha=1, s=100, c='r', marker='*')
        guit.plot(np.array(queries)*count2dis, fit_y_int*count2dis, linewidth=0.05, color='b', marker='.')
        guit.set_xlabel('Scope Distance Output/m', fontsize=12)
        guit.set_ylabel('Compensation Values/m', fontsize=12)
        title = 'Residual Count   Channel ' + str(i + 1)
        plt.title(title, fontsize=12)
        if i == 47:
            kt_6.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96, wspace=0.3, hspace=0.5)
            pic_save_file = save_path + '/' +  '#-slinear interpolation3.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            kt_6.savefig(pic_save_file)
            plt.show()
            plt.close()
            continue
    elif i >47:
        kt_7 = plt.figure(7, figsize=(20, 10))
        guit = kt_7.add_subplot(4, 4, i - 47)
        guit.scatter(sub_sample*count2dis, sub_value*count2dis, alpha=1, s=100, c='r', marker='*')
        guit.plot(np.array(queries)*count2dis, fit_y_int*count2dis, linewidth=0.05, color='b', marker='.')
        guit.set_xlabel('Scope Distance Output/m', fontsize=12)
        guit.set_ylabel('Compensation Values/m', fontsize=12)
        title = 'Residual Count   Channel ' + str(i + 1)
        plt.title(title, fontsize=12)
        if i == 63:
            kt_7.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96, wspace=0.3, hspace=0.5)
            pic_save_file = save_path + '/' +  '#-slinear interpolation4.png'
            if os.path.exists(pic_save_file):
                os.remove(pic_save_file)
            kt_7.savefig(pic_save_file)
            plt.show()
            plt.close()
            break



# generate sum txt


output = []
for i in range(64):
    output.append([])

for i in range(0, 64):
    # 2-12bit transform to 3-8bit for hardware storage: fitting region
    low_hex = "{:#05X}".format(index_start_modified[i])
    high_hex = "{:#05X}".format(index_end_modified[i])
    together_hex = low_hex[2:5] + high_hex[2:5]
    index_array = bytearray.fromhex(together_hex)
    index3 = list(index_array)

    # 强制上下限取0，使非单调区间调节不起作用
    up_index = 0
    low_index = 0

    reverse_low_hex = "{:#05X}".format(up_index)
    reverse_high_hex = "{:#05X}".format(low_index)
    reverse_together_hex = reverse_low_hex[2:5] + reverse_high_hex[2:5]
    reverse_index_array = bytearray.fromhex(reverse_together_hex)
    reverse_index3 = list(reverse_index_array)


    output[i].append(hex(index3[0]).replace('0x', '').zfill(2))
    output[i].append(hex(index3[1]).replace('0x', '').zfill(2))
    output[i].append(hex(index3[2]).replace('0x', '').zfill(2))
    output[i].append(hex(reverse_index3[0]).replace('0x', '').zfill(2))
    output[i].append(hex(reverse_index3[1]).replace('0x', '').zfill(2))
    output[i].append(hex(reverse_index3[2]).replace('0x', '').zfill(2))
    for k in range(0, index_end_modified[i] - index_start_modified[i] + 1):
        if int(fit_total[i][k]) < 0:
            output[i].append(hex(0).replace('0x', '').zfill(2))
        elif int(fit_total[i][k]) > 254:
            output[i].append(hex(254).replace('0x', '').zfill(2))
        else:
            output[i].append(hex(fit_total[i][k]).replace('0x', '').zfill(2))
    for k in range(0, 2042 + index_start_modified[i] - index_end_modified[i] - 1):
        output[i].append(hex(0).replace('0x', '').zfill(2))

sum_txt = save_path + '/sum_' + 'Scope' + '.txt'
if os.path.exists(sum_txt):
    os.remove(sum_txt)
sum_txt = open(sum_txt, 'w')

sumoutput = []
for i in range(16):
    sumoutput.append(list(zip(output[0+4*i],output[1+4*i],output[2+4*i],output[3+4*i])))
    for j in range(2048):
        sumstr = ''.join(sumoutput[i][j])
        sum_txt.writelines(sumstr +'\n')
        #print(sumstr)
sum_txt.close()

print('Finish')
