#-*- coding: utf-8 -*-
import os
from socket import *

class TcpClient:
    #测试，连接本机
    HOST='192.168.0.102'
    #设置侦听端口
    PORT=1122 
    BUFSIZ=1024
    ADDR=(HOST, PORT)
    def __init__(self):
        self.client=socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.ADDR)

        while True:
            print u'请输入文件路径：'
            fname=raw_input()
            print fname[0], fname[-1]
            if "quit" == fname.lower():
                break
            if 0 ==  len(fname) or not os.path.isfile(fname):
                print u"输入的文件不存在"
                continue
            self.client.send(fname)
            print u"正在发送..."
            fn = open(fname, "rb")
            while True:
                data = fn.read(self.BUFSIZ)
                if not data:
                    break
                self.client.send(data)
            fn.close()
            self.client.shutdown(1)
            print u"发送完成，正在等待返回结果..."
            recv_data=self.client.recv(self.BUFSIZ)
            if not recv_data:
                break
            print recv_data.decode('utf-8')
            recv_data=self.client.recv(self.BUFSIZ)
            if not recv_data:
                break
            print(u'从%s收到信息：%s' %(self.HOST, recv_data.decode('utf-8')))
#     def __init__(self):
#         self.client=socket(AF_INET, SOCK_STREAM)
#         self.client.connect(self.ADDR)
# 
#         while True:
#             data=raw_input('>')
#             if not data:
#                 break
#             #python3传递的是bytes，所以要编码
#             self.client.send(data.encode('utf8'))
#             print(u'发送信息到%s：%s' %(self.HOST,data))
#             if data.upper()=="QUIT":
#                 break            
#             data=self.client.recv(self.BUFSIZ)
#             if not data:
#                 break
#             print(u'从%s收到信息：%s' %(self.HOST,data.decode('utf8')))
            
            
if __name__ == '__main__':
    client=TcpClient()
