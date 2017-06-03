#-*- coding: utf-8 -*-
import os
import re
import json
import urllib
import httplib


class MyHttpClient(object):
    def __register(self, conn):
        print u"请输入手机号、密码，用,分隔"
        input_str = raw_input()
        input_l   = re.split(r",\s+|,", input_str)
        if 2 != len(input_l) or 11 != len(input_l[0]):
            print input_l
            print len(input_l[0])
            print u"输入错误"
            return
        user_name, user_passwd = input_l[0], input_l[1]
        
#         headers = {"Content-type": "application/x-www-form-urlencoded",
#                    "Accept": "text/plain"}#Accept： 浏览器可接受的MIME类型 
#                    #Content-Type 表示后面的文档属于什么MIME类型
#         data = urllib.urlencode({"userId":user_name, "passwd":user_passwd})
        headers = {"Content-type": "application/json",
                   "Accept": "text/plain"}
        data = json.dumps({"userId":user_name, "passwd":user_passwd})
        conn.request('POST', '/user/register', body=data, headers=headers)
        httpres = conn.getresponse()
        print httpres.status  
        print httpres.reason  
        rst = json.loads(httpres.read())
        print rst["status"]
        if 0 == rst["status"]:
            print u"注册成功"
        else:
            print rst["errMsg"]#.decode("utf-8")
    
    def __login(self, conn):
        print u"请输入手机号、密码，用,分隔"
        input_str = raw_input()
        input_l   = re.split(r",\s+|,", input_str)
        if 2 != len(input_l) or 11 != len(input_l[0]):
            print input_l
            print len(input_l[0])
            print u"输入错误"
            return
        user_name, user_passwd = input_l[0], input_l[1]
        
        headers = {"Content-type": "application/json",
                   "Accept": "text/plain"}
        data = json.dumps({"userId":user_name, "passwd":user_passwd})
        conn.request('POST', '/user/login', body=data, headers=headers)
        httpres = conn.getresponse()
        print httpres.status
        print httpres.reason  
        rst = json.loads(httpres.read())
        print rst["status"]
        if 0 == rst["status"]:
            print u"登录成功"
        else:
            print rst["errMsg"]#.decode("utf-8")

    def __collect(self, conn):
        print u"请输入手机号、设备型号、文件路径，用,分隔"
        input_str = raw_input()
        input_l   = re.split(r",\s+|,", input_str)
        if 3 != len(input_l) or 11 != len(input_l[0]):
            print input_l
            print len(input_l[0])
            print u"输入错误"
            return
        user_name = input_l[0]
        dev_type  = input_l[1]
        filename  = input_l[2]
        print filename
        if not os.path.isfile(filename):
            print u"输入的文件不存在..."
            return
        
        headers = {"Content-type": "application/json",
                   "Accept": "text/plain"}
        fn = open(filename, "r")
        fname = os.path.split(filename)[1]
        #fname = fname.decode(sys.stdin.encoding or locale.getpreferredencoding(True))
        data = json.dumps({"userId":user_name, "devType":dev_type,\
                "fName":fname, "fContent":fn.read()})
        conn.request('POST', '/data/collect', body=data, headers=headers)
        fn.close()
        print u"文件已发送，正在等待服务器处理"
        httpres = conn.getresponse()
        print httpres.status  
        print httpres.reason
        rst = json.loads(httpres.read())
        print rst["status"]
        if 0 == rst["status"]:
            print u"采集数据上传成功"
        else:
            print rst["errMsg"]#.decode("utf-8")

    def run(self):
        conn = httplib.HTTPConnection('192.168.0.102:8886')
        while True:
            print u"\n退出请按0"
            print u"注册请按1"
            print u"登录请按2"
            print u"采集请按3"
            sel_num = raw_input()
            if "0" == sel_num:
                break
            elif "1" == sel_num:
                self.__register(conn)
            elif "2" == sel_num:
                self.__login(conn)
            elif "3" == sel_num:
                self.__collect(conn)
            else:
                continue
        conn.close()
    
if __name__ == '__main__':
    va = MyHttpClient()
    va.run()
