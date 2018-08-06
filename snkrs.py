#!/usr/bin/python3
#coding:utf-8
import urllib3
import json
import time
from datetime import datetime
import traceback
from collections import deque
import os
import requests
#import winsound

urllib3.disable_warnings()



#http = urllib3.PoolManager()
#appinitializationUrl = "https://unite.nike.com/appInitialization?appVersion=460&experienceVersion=378&uxid=com.nike.commerce.snkrs.ios&locale=zh_CN&backendEnvironment=identity&browser=Apple%20Computer%2C%20Inc.&os=undefined&mobile=true&native=true&visit=&visitor=&clientId=G64vA0b95ZruUtGk1K0FkAgaO3Ch30sj&status=success&uxId=com.nike.commerce.snkrs.ios&isAndroid=false&isIOS=true&isMobile=true&isNative=true&timeElapsed=203"
#initHeaders = {
#    'host':'unite.nike.com',
#    'Content-Type':'application/json',
#    'Origin':'https://s3.nikecdn.com',
#    'Connection':'keep-alive',
#    'X-NewRelic-ID':'VQYGVF5SCBADUVBRBgAGVg==',
#    'Proxy-Connection':'keep-alive',
#    'Accept':'*/*',
#    'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257',
#    'Accept-Language':'en-us',
#    'Accept-Encoding':'gzip, deflate',
#    'Cookie':'s_vi=[CS]v1|2DB0A344852A167D-60000106C00000CE[CE]'
#}
#
#resp = http.request("GET", appinitializationUrl,headers = initHeaders)
#print(resp.getheaders().get('Set-Cookie'))
#
#print("cookies:",cookies)
#loginUrl = "https://s3.nikecdn.com/login?appVersion=460&experienceVersion=378&uxid=com.nike.commerce.snkrs.ios&locale=zh_CN&backendEnvironment=identity&browser=Apple%20Computer%2C%20Inc.&os=undefined&mobile=true&native=true&visit=1&visitor=53f479c5-6cc7-4ef9-82a8-10fa4b02c95d"
#loginHeaders = {
#    'host':'s3.nikecdn.com',
#    'Content-Type':'application/json',
#    'Origin':'https://s3.nikecdn.com',
#    'Connection':'keep-alive',
#    'Proxy-Connection':'keep-alive',
#    'Accept':'*/*',
#    'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257',
#    'Accept-Language':'en-us',
#    'Accept-Encoding':'gzip, deflate',
#}
#loginPayload={
#    "username":"xxxxxxx",
#    "password":"xxxxx",
#    "client_id":"G64vA0b95ZruUtGk1K0FkAgaO3Ch30sj",       
#    "ux_id":"com.nike.commerce.snkrs.ios",
#    "grant_type":"password"
#}
#
#loginResp = http.request("POST", loginUrl, body=json.dumps(loginPayload))
#cookies=loginResp.cookies.get_dict()
#print("cookies:",cookies)
#print(loginResp.data)
#
#
#
def formatTimeStr(str):
    return str[0:10]+" "+str[11:19]
def getTime(str):
    return time.mktime(time.strptime(formatTimeStr(str),"%Y-%m-%d %H:%M:%S"))
def getLocalTimeStr(str):
    tm = getTime(str)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(tm+28800)))
def addsepline():
    print("-----------------------------------------------------------------------------------------------")

addsepline()
print("做监控是为了方便各位sneakerhead，有问题请反馈，免费分享，请不要倒卖！！！！")
print("下载地址:https://pan.baidu.com/s/1h7sodzyH2-Cx1BWM5DdDbg")
print("作者:Niko(wechat:xvnk23)")
addsepline()

from enum import Enum
class RegionURL(Enum):
    cn = "&country=CN&language=zh-Hans"
    us = "&country=US&language=en"
    jp = "&country=JP&language=ja"
class OrderBy(Enum):
    published = "&orderBy=published"
    updated = "&orderBy=lastUpdated"

url = "https://api.nike.com/snkrs/content/v1/?"

areaCode = input("请选择市场区域(1:美国,2:日本,3:中国):")
if areaCode == "1":
    url += RegionURL.us.value
elif areaCode == "2":
    url += RegionURL.jp.value
else:
    url += RegionURL.cn.value

print("正在抓取最新发布球鞋数据...")

sneakers = [] #球鞋缓存
ludict = {} #
totalCount = 1000000

def printSneaker(data):
    str = data["name"]+" "+data["title"]
    try:
        if data["product"]["colorDescription"]:
            str += ("["+data["product"]["colorDescription"]+"]")
        if data["product"]["merchStatus"]:
            str += ("["+data["product"]["merchStatus"]+"]")
    except:
        pass
    if data["restricted"]:
        str += "[专属]"
    print(str)

def requestSneakers(order,offset):
    global totalCount
    requrl = url+"&offset="+str(offset)+order
    http = urllib3.PoolManager()
    r = http.request("GET", requrl)
    shoes = []
    try:
        json_data = json.loads(r.data)
        if len(sneakers) >= totalCount:
            return []
        totalCount = json_data["totalRecords"]
        for data in json_data["threads"]:
            shoes.append(data["id"])
            ludict[data["id"]] = getTime(data["lastUpdatedDate"])
            if offset == 0:
                printSneaker(data)
        return shoes
    except :
        print("\r访问服务器失败，3秒后重试")
        time.sleep(3)
        return requestSneakers(order,offset)

for num in range(0,10000):
    k = num * 50
    snkrs = requestSneakers(OrderBy.published.value,k)
    if len(snkrs) == 0:
        print("数据请求完毕,一共获取到",str(len(sneakers)),"条数据(只显示前50条)...")
        break
    sneakers.extend(snkrs)

addsepline()
frequency = 3
warningTime = 5
inputfreq = input("请设定接口访问频率(秒)，访问频率过快可能会导致服务器异常，默认是3，最小是1:")
try:
    frequency = int(inputfreq)
except:
    print("输入出错，按照默认频率请求")
if frequency <= 0:
    frequency == 3
warning = input("请设定发现新款过后报警次数，默认是5，最小是1:")
try:
    warningTime = int(warning)
except:
    print("输入出错，按照默认次数报警")
if warningTime <= 0:
    warningTime == 5
print("服务器实时请求接口中("+str(frequency)+"秒每次)...")
addsepline()

def timer(n):
    while True:
        http = urllib3.PoolManager()
        requesturl = url + OrderBy.updated.value + "&offset=0"
        r = http.request("GET", requesturl)
        json_data = json.loads(r.data)
        try:
            datas = json_data["threads"]
        except:
            print("请求失败")
            timer(frequency)
            break
        for data in datas:
            sneakerid = data["id"]
            if sneakerid not in sneakers:
                sneakers.append(sneakerid)
                ludict[data["id"]] = getTime(data["lastUpdatedDate"])
                i=warningTime
                while i>0:
                    os.system('say "发现新款上架"')
#                    winsound.Beep(2600,1000)
                    print(getLocalTimeStr(data["lastUpdatedDate"]),"发现新款上架",end=" ")
                    printSneaker(data)
                    i-=1
            else:
                if getTime(data["lastUpdatedDate"]) > ludict[sneakerid]:
                    ludict[sneakerid] = getTime(data["lastUpdatedDate"])
                    product = data["product"]
                    print(getLocalTimeStr(data["lastUpdatedDate"]),end=" ")
                    str = "售罄"
                    if product["merchStatus"] == "ACTIVE":
                        if product["available"]:
                            str = "库存更新("
                            for sku in product["skus"]:
                                if sku["available"]:
                                    str += (sku["localizedSize"]+",")
                            str = str[:-1]
                            str += ")"
                    print(str,end=" ")
                    printSneaker(data)
        time.sleep(frequency)
timer(3)
# SNKRSMonitor
