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
    m3u8_title = re.findall('title: "[\S]*"', re_data)
    m3u8_begin = re.findall('begin:"[0-9]*"', re_data)
    m3u8_end = re.findall('end:"[0-9]*"', re_data)
    title =  m3u8_title[0][8:-1]
    begin = int(m3u8_begin[0][7:-1])
    end = int(m3u8_end[0][5:-1])
    print( '直播网页解析成功：\n',
           'm3u8路径：',m3u8_url[0],'\n',
           '录像标题：',title,'\n',
           '录像时长：',end - begin,' s'
         )
    m3u8_file = requests.get(m3u8_url[0]).content
    savepath_filename = os.getcwd() + '\\' + os.path.basename(url)
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
            total_time += float(re.findall('[0-9]*\.?[0-9]+',line)[0])
        if line_info != []:
            m3u8_info[1].append(line_info[0])
    f.close()
    return m3u8_info

def downloader(url, savepath_filename):
    re_data = requests.get(url).content
    output = open(savepath_filename, 'wb')
    output.write(re_data)
    output.close()

##############################################################################################################
class ProgressBar:
    def __init__(self,count = 0,total = 0,width = 90):
        self.count = count
        self.total = total
        self.width = width
    def move(self):
        self.count += 1
    def log(self):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:4}/{1:4}:'.format(self.count,self.total))
        sys.stdout.write('#'* progress +'-'*(self.width - progress)+'\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()
##############################################################################################################
if __name__ == '__main__':
    url = ''
    title = ''
    start_flag = 0
    end_flag = 0
    if len(sys.argv) == 2 and sys.argv[1] == '-help':
        print ('Use: main.py [url]\n',
               'Use: main.py [url] [start] [end]\n',
               'NOTICE:[start] and [end] by seconds')
        exit() 
    if len(sys.argv) >= 4 :
        url = sys.argv[1]    
        start_flag = float(sys.argv[2])
        end_flag = float(sys.argv[3])
        if start_flag > end_flag: #防止智障
            temp = end_flag
            end_flag = start_flag
            start_flag = temp  
    else:
        url = sys.argv[1]
    print('欢迎使用YY录像下载工具，正在下载的url为：'+url)
    path = os.getcwd()
    print('当前的工作路径为：'+path)
    tmp_path = path + '\\ts\\'
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
        print('创建临时文件夹成功')
    print('---------------------------------------------------------------------------------------')
    
    (m3u8_filename,title) = get_m3u8_file(url)
    m3u8_info = get_m3u8_info(m3u8_filename)
    m3u8_num = len(m3u8_info[1])

    start = 0
    end = m3u8_num - 1
    if end_flag!=0:
        i = 0
        while m3u8_info[0][i] <= start_flag:
            if i >= m3u8_num:#防止智障
                break
            i+=1
        start = i
        
        while m3u8_info[0][i] <= end_flag:
            if i >= m3u8_num:
                break
            i+=1
        end = i
    
    #下载分片文件
    pro = ProgressBar(total = end+1-start) 
    starttime = datetime.datetime.now()
    for i in range(start,end+1):
        savepath_filename = path + '\\ts\\' + '%06d'%i + '.ts'
        downloader(m3u8_info[1][i] , savepath_filename)
        untilnowtime = datetime.datetime.now()
        interval = (untilnowtime - starttime).seconds
        pro.move()
        pro.log()
    
    #下面开始合并文件
    fromdir = path + '\\ts\\'
    tofile = path + '\\' + title + '[' + str(start_flag) + '-' + str(end_flag) + ']' + '.ts'
    join(fromdir, tofile)
    print ('合并文件成功！')
    
    shutil.rmtree(fromdir)
    os.mkdir(fromdir)
    print ('清理临时文件成功!')

    endtime = datetime.datetime.now()
    interval = (endtime - starttime).seconds
    print ('共计用时 ' + str(interval/60) + ' min (' + str(interval) + ' s )')