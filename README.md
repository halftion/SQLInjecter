# SQL-Injecter

#### 项目介绍 :  
  
基于Python3.8的SQL盲注利用脚本 , 实现很简陋
  
---
#### 使用说明 :  
```
python sqlhacker.py http://www.xxx.com/index.php?id=1
```
只需要一个参数 , 程序会自动判断是否存在注入点  
如果存在会显示出Payload并自动脱裤  
会自动忽略系统库 , 例如` information_schema/mysql `等  

---

#### TODO :  
1. 目前只可以利用Bool盲注 , 时间盲注为扩展功能
2. 目前只支持GET方式
3. 有时候会出现可以找到注入点 , 但是注入的时候出错的情况 , 这个还是因为是通过长度判断的
4. 检测URL是否存在时间盲注漏洞