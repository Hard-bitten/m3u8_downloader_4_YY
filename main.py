# -*- coding: utf-8 -*-
"""
Created on 20170519

@author: XDLiu 
Thanks for WHUER https://github.com/xuyuanfang/m3u8_downloader_4_yingke
"""

import re
from join import join
import requests
import shutil
import datetime,time
import os,sys

##############################################################################################################
def get_m3u8_file(url):
    re_data = requests.get(url).text
    m3u8_url = re.findall('[a-zA-z]+://[^\s]*.m3u8', re_data)
    m3u8_title = re.findall('title: "[^\x00-\xff]*"', re_data)
    title =  m3u8_title[0][8:-1]
    print(m3u8_title)
    m3u8_file = requests.get(m3u8_url[0]).content
    path = os.getcwd()
    savepath_filename = path + '\\' + os.path.basename(url)
    output = open(savepath_filename, 'wb')
    output.write(m3u8_file)
    output.close()
    return (savepath_filename,title)
    
def get_m3u8_info(m3u8_filename):
    m3u8_info = [[]*2,[]*2]
    f = open(m3u8_filename)
    lines = f.readlines()
    total_time = 0.0
    for line in lines:
        line_info = re.findall('[a-zA-z]+://[^\s]*', line)
        if line.find("#EXTINF:") != -1:
            m3u8_info[0].append(total_time)
            total_time += float(re.findall('[1-9].[0-9]*',line)[0])
        if line_info != []:
            m3u8_info[1].append(line_info[0])
    f.close()
    #print('录像时长：'+time.strtime('%H:%M:%S',time.gmtime(total_time)))
    return m3u8_info

def downloader(url, savepath_filename):
    re_data = requests.get(url).content
    output = open(savepath_filename, 'wb')
    output.write(re_data)
    output.close()

##############################################################################################################
if __name__ == '__main__':
    url = ''
    title = ''
    start_flag = 0
    end_flag = 0
    print(len(sys.argv))
    if len(sys.argv) == 2 and sys.argv[1] == '-help':
        print ('Use: main.py [url]')
        exit() 
    if len(sys.argv) == 4 :
        url = sys.argv[1]    
        start_flag = float(sys.argv[2])
        end_flag = float(sys.argv[3])
    else:
        url = sys.argv[1]
    print('欢迎使用YY录像下载工具，正在下载的url为：'+url)
    path = os.getcwd()
    print('当前的工作路径为：'+path)
    tmp_path = path + '\\ts\\'
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
        print('创建临时文件夹成功')
    
    (m3u8_filename,title) = get_m3u8_file(url)
    print (title)
    m3u8_info = get_m3u8_info(m3u8_filename)

    m3u8_num = len(m3u8_info[1])

    print ('m3u8的分片数为： ' + str(m3u8_num))
    starttime = datetime.datetime.now()
    
    start = 0
    end = m3u8_num-1
    if end_flag!=0:
        i = 0
        while m3u8_info[0][i] <= start_flag:
            i+=1
        start = i
        
        while m3u8_info[0][i] <= end_flag:
            i+=1
        end = i
    
    for i in range(start,end+1):
        print ('正在下载： ' + m3u8_info[1][i] + ' ['+ str(i + 1- start) +'/' + str(end + 1 - start) + ']')
        #ts_url = url_ + id + '/' + m3u8_info[i]
        savepath_filename = path + '\\ts\\' + '%06d'%i + '.ts'
        downloader(m3u8_info[1][i] , savepath_filename)
        untilnowtime = datetime.datetime.now()
        interval = (untilnowtime - starttime).seconds
        print ('已经下载了： ' + str(interval) + 's')
    
    
    fromdir = path + '\\ts\\'
    tofile = path + '\\' + title +str(start_flag) + '-' + str(end_flag)+ '.ts'
    print ('合并文件开始！')
    join(fromdir, tofile)
    print ('合并文件开始成功！')
    
    shutil.rmtree(fromdir)
    os.mkdir(fromdir)
    print ('清理临时文件成功!')

    endtime = datetime.datetime.now()
    interval = (endtime - starttime).seconds
    print ('共计用时 ' + str(interval/60) + ' min (' + str(interval) + ' s )')