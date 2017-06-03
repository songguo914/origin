# -*- coding: utf-8 -*-
import os
import time
import SocketServer


# Address and Port
HOST = ''
PORT = 1122
ADDR = (HOST, PORT)
BUFSIZ = 1024
SERVERPATH = os.path.join("server_data")
RECEIVEDPATH = os.path.join(SERVERPATH, "received_data")


# build RequestHandler
class MyRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        #self.request.settimeout(20)
        print(u'接受连接，客户端地址:%s'%str(self.client_address))
        fname = os.path.split(self.request.recv(BUFSIZ))[1]
        if not fname:
            self.request.close()
            return
        time_stamp = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        filename = os.path.join(RECEIVEDPATH, "%s-%s"%(time_stamp, fname))
        print u"正在接收文件..."
        try:
            fn = open(filename, "wb")
            while True:
                rdata = self.request.recv(BUFSIZ)
                if not rdata:
                    break
                fn.write(rdata)
        except IOError, err:
            print err
        finally:
            if fn:
                fn.close()
        
        #try:
        mess = u"文件接收完毕，正在处理"
        mess = mess.encode('utf-8')
        self.request.send(mess)
        print u"接收文件完毕"

        self.request.send("yes")

        self.request.close()
        print(u'等待接入，侦听端口:%d'%(PORT))


if __name__ == '__main__':
    if not os.path.exists(SERVERPATH):
            os.mkdir(SERVERPATH)
    if not os.path.exists(RECEIVEDPATH):
            os.mkdir(RECEIVEDPATH)

    # build TCPServer
    TCPServ = SocketServer.ThreadingTCPServer(ADDR, MyRequestHandler)
    print(u'等待接入，侦听端口:%d'%(PORT))
    # loop to process
    TCPServ.serve_forever()
