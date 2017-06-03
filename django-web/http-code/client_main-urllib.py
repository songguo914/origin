#  -*- coding:utf-8 -*-
import re
import json
import urllib
import urllib2


def http_post():
    print u"请输入手机号、密码，用,分隔"
    input_str = raw_input()
    input_l   = re.split(r",\s+|,", input_str)
    if 2 != len(input_l) or 11 != len(input_l[0]):
        print input_l
        print len(input_l[0])
        print u"输入错误"
        return
    user_name, user_passwd = input_l[0], input_l[1]
    
    url='http://192.168.0.102:8886/user/register'
    jdata = json.dumps({"userId":user_name, "passwd":user_passwd})

    headers = {"Content-type": "application/json",
                   "Accept": "text/plain"}
    req = urllib2.Request(url, jdata, headers=headers)       # 生成页面请求的完整数据
    response = urllib2.urlopen(req)       # 发送页面请求
    rst = json.loads(response.read())                    # 获取服务器返回的页面信息
    if 0 == rst["status"]:
        print u"注册成功"
    else:
        print rst["errMsg"]#.decode("utf-8")
    return

while True:
    resp = http_post()
