import requests
import time
import json
import math
import os

list = ['mm','fs','ipc','lib','block','init','net','kernel','crypto','sound','drivers','arch','include','security','certs']
url_api = 'http://192.168.3.100:7001/api/v1/graphs'
url_svg = 'http://192.168.3.100:7001/public/svg/'
data = {
    'version': '4-15-18',
    'platform': 'x86_64',
    'source': '/mm',
    'target': '/'
}
file = open('get_svg.log','a')
file2 = open('get_json.log','a')

def get_svg(path1,path2,url,file):
    # 获取svg图的get函数
    start_date = time.time()
    response_size = 0
    fname = 'test-' + path1
    p = path1
    if path2 != '':
        fname += '-' + path2
        p += '-' + path2
    fname += '.svg' 
    res = requests.get(url=url+fname)
    response_size = len(res.text)
    end_date = time.time()

    s = p + ' ' + str(math.floor((end_date - start_date)*1000)) + ' ' + str(response_size) + '\n'
    # 路径 传输时间 大小
    file.write(s)
    return

def get_json(path1,path2,url,data,file):
    # 测试api的get函数

    start_date = time.time()
    response_size = 0
    data['source'] = '/' + path1
    data['target'] = '/' + path2
    p = path1
    if path2 != '':
        p += '-' + path2
    
    res = requests.get(url=url,params = data)
    response_size = len(res.text)
    end_date = time.time()
    res_data =  json.loads(res.text)
    print(len(res_data['nodes']),len(res_data['edges']))
    s = p + ' ' + str(res_data['time_cost']) + ' ' +str(math.floor((end_date - start_date)*1000)) + ' ' + str(response_size) + ' ' + str(len(res_data['nodes'])) + ' ' + str(len(res_data['edges'])) + '\n'
    # 路径 处理时间 传输到达时间 大小 nodes edges 
    file.write(s)
    return

n = 2

for i in range(0, n):
    # 跑n次get全部路径的记录
    for i in range(0, 15):
        # get_svg(list[i],'',url_svg,file)
        get_json(list[i],'',url_api,data,file2)
        # get 单路径 mm
        for j in range( i+1 , 15):
            # get_svg(list[i],list[j],url_svg,file)
            get_json(list[i],list[j],url_api,data,file2)
            # get 双路径 mm-fs

file.close()
file2.close()
