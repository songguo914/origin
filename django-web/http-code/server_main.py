# -*- coding: utf-8 -*-
import os
import re
import cgi
import json
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


# Address and Port
HOST = ''
PORT = 8886#8080
ADDR = (HOST, PORT)

SERVERPATH     = os.path.join("server_data")
RAWCOLLECTPATH = os.path.join(SERVERPATH, "raw_collect")
LOGINPATH      = os.path.join(SERVERPATH, "login")


# 请求处理
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __writeheaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self.__writeheaders()

    def do_POST(self):
        print "headers:", self.headers
        form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                'CONTENT_TYPE':self.headers['Content-Type'],})
                #要想接收json数据，Content-Type的值必须为"application/json"
        post_value = json.loads(form.value)

        print "path", self.path
        if re.match(r"^/user/register$", self.path):
            rst_status, rst_err_msg = self.__register(post_value)#注册
            rst_data = ""
        elif re.match(r"^/user/login$", self.path):
            rst_status, rst_err_msg = self.__login(post_value)#登录
            rst_data = ""
        elif re.match(r"^/data/collect$", self.path):
            rst_status, rst_err_msg = self.__collect(post_value)#一次性采集数据
            rst_data = ""
        else:
            rst_status  = 1
            rst_err_msg = (u"你访问的地址不存在：%s"%self.path).encode("utf-8")
            rst_data = ""
            #self.send_error(404, (u"你访问的地址不存在：%s"%self.path).encode("utf-8"))
        
        self.__writeheaders()
        self.wfile.write(json.dumps({"status":rst_status, "data":rst_data,\
                "errMsg":rst_err_msg}))
        print(u'等待接入，侦听端口:%d'%(PORT))
        return

    def __register(self, post_value):
        rst_status  = 0
        rst_err_msg = ""
        
        if "userId" not in post_value or "passwd" not in post_value:
            rst_status  = 1
            rst_err_msg = u"获取注册信息失败".encode('utf-8')
            #self.send_error(400, u"获取登录信息失败".encode('utf-8'))
            return (rst_status, rst_err_msg)
                
        user_name, user_passwd = post_value["userId"], post_value["passwd"]
        if 11 != len(user_name) or 0 == len(user_passwd):
            rst_status  = 1
            rst_err_msg = u"注册信息填写错误".encode('utf-8')
            #self.send_error(400, u"注册信息填写错误".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
        login_info = self.__load_login_info()
        if not isinstance(login_info, dict):
            rst_status  = 1
            rst_err_msg = u"服务器读信息失败".encode('utf-8')
            #self.send_error(500, u"服务器遇到未知错误".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
        if user_name in login_info:
            rst_status  = 1
            rst_err_msg = u"注册的用户已存在".encode('utf-8')
            #self.send_error(406, u"该用户已存在".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
        rst = True
        try:
            fn = open(LOGINPATH, "ab")
            fn.write("%s:%s\n"%(user_name, user_passwd))
        except Exception, err:
            print err
            rst = False
        finally:
            if fn:
                fn.close()
        if not rst:
            rst_status  = 1
            rst_err_msg = u"服务器写信息出错".encode('utf-8')
            #self.send_error(500, u"服务器遇到未知错误".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write("yes")
        return (rst_status, rst_err_msg)

    def __login(self, post_value):
        rst_status  = 0
        rst_err_msg = ""
        if "userId" not in post_value or "passwd" not in post_value:
            rst_status  = 1
            rst_err_msg = u"获取登录信息失败".encode('utf-8')
            #self.send_error(400, u"获取登录信息失败".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
        user_name, user_passwd = post_value["userId"], post_value["passwd"]
        if 11 != len(user_name) or 0 == len(user_passwd):
            rst_status  = 1
            rst_err_msg = u"登录信息错误".encode('utf-8')
            #self.send_error(400, u"登录信息错误".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
        login_info = self.__load_login_info()
        if not isinstance(login_info, dict):
            rst_status  = 1
            rst_err_msg = u"服务器读信息出错".encode('utf-8')
            #self.send_error(500, u"服务器遇到未知错误".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
        if user_name not in login_info:
            rst_status  = 1
            rst_err_msg = u"用户不存在，请先注册".encode('utf-8')
            #self.send_error(403, u"用户不存在，请先注册".encode('utf-8'))
            return (rst_status, rst_err_msg)
        elif user_passwd != login_info[user_name]:
            rst_status  = 1
            rst_err_msg = u"密码错误".encode('utf-8')
            #self.send_error(403, u"密码错误".encode('utf-8'))
            return (rst_status, rst_err_msg)
        else:
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write("yes")
            return (rst_status, rst_err_msg)

    def __load_login_info(self):
        login_info = {}
        rst = True
        try:
            fn = open(LOGINPATH, "rb")
            for line_str in fn.xreadlines():
                line_l = re.split(r":\s+|:", line_str)
                if 2 != len(line_l):
                    continue
                if line_l[0] not in login_info:
                    login_info[line_l[0]] = (line_l[1]).strip()
        except Exception, err:
            print err
            rst = False
        finally:
            if fn:
                fn.close()
        if not rst:
            return
        return login_info

    def __check_received_data(self, post_value):
        if "userId" not in post_value or 11 != len(post_value["userId"]):
            rst_status  = 1
            rst_err_msg = u"用户信息出错".encode('utf-8')
        elif "devType" not in post_value:
            rst_status  = 1
            rst_err_msg = u"设备信息出错".encode('utf-8')
        elif "fName" not in post_value or "fContent" not in post_value:
            rst_status  = 1
            rst_err_msg = u"文件信息出错".encode('utf-8')
        else:
            rst_status  = 0
            rst_err_msg = ""
        return (rst_status, rst_err_msg)

    def __collect(self, post_value):
        rst_status, rst_err_msg = self.__check_received_data(post_value)
        if 0 != rst_status:
            return (rst_status, rst_err_msg)
        
        dev_type_path = os.path.join(RAWCOLLECTPATH,\
                (post_value["devType"]).encode("utf-8"))
        if not os.path.isdir(dev_type_path):
            os.mkdir(dev_type_path)
        user_path = os.path.join(dev_type_path, (post_value["userId"]).encode("utf-8"))
        if not os.path.isdir(user_path):
            os.mkdir(user_path)
        fname = post_value["fName"]
        filename = os.path.join(user_path, fname.encode("utf-8"))
        
        print u"正在接收文件..."
        rst = True
        try:
            fn = open(filename, "wb")
            fn.write(post_value["fContent"])
        except IOError, err:
            print err
            rst = False
        finally:
            if fn:
                fn.close()
        if not rst:
            rst_status  = 1
            rst_err_msg = u"接收文件失败，遇到未知错误".encode('utf-8')
            #self.send_error(500, u"接收文件失败，遇到未知错误".encode('utf-8'))
            return (rst_status, rst_err_msg)
        
        print u"接收文件完毕"
        rst_status  = 0
        rst_err_msg = ""
        return (rst_status, rst_err_msg)

class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass


def init_env():
    if not os.path.isdir(SERVERPATH):
        os.mkdir(SERVERPATH)
    if not os.path.isdir(RAWCOLLECTPATH):
        os.mkdir(RAWCOLLECTPATH)

    if not os.path.isfile(LOGINPATH):
        try:
            fn = open(LOGINPATH, "wb")
        except Exception, err:
            print err
        finally:
            if fn:
                fn.close()


if __name__ == '__main__':
    init_env()

    srvr = ThreadingServer(ADDR, SimpleHTTPRequestHandler)
    print(u'等待接入，侦听端口:%d'%(PORT))
    srvr.serve_forever()

