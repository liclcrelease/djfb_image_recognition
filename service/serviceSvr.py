import sys
import os
import logging
import logging.handlers
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
import asyncio
import threading
import time
import ctypes
from urllib.parse import unquote
from optparse import OptionParser
from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from service.handle.matchBegin import handleMatchBegin
from service.handle.matchEnd import handleMatchEnd

from multiprocessing.managers import BaseManager,DictProxy

from service.singleton import singletonInstance
from service.proc import procVariable
from service.logic import check
from service.logic import post
from service.logic import timer
from service.exit_after import time_out



class MyHttpRequestHandler(SimpleHTTPRequestHandler):


    def do_GET(self):
        listParam = self.path[1:].split("?")
        if len(listParam) <= 1:
            return self.ret_get_body('{"ret":0,"des":"invalid param"}')

        strMethod = listParam[0]
        #print(self.path)
        logging.debug(self.path)
        dictParam = self.query_to_dict(listParam[1])

        try:
            if strMethod == "matchBegin":
                handleMatchBegin(dictParam)
            elif strMethod == "matchEnd":
                handleMatchEnd(dictParam)
            else:
                return self.ret_get_body("method is not found")

            return self.ret_get_body('{"ret":0,"des":""}')

        except Exception as e:
            return self.ret_get_body(repr(e))

    def query_to_dict(self,query:str):

        res = {}
        k_v_pairs = query.split("&")
        for item in k_v_pairs:
            sp_item = item.split("=", 1)
            key = sp_item[0]
            value = unquote(sp_item[1])
            res[key] = value

        return res


    def ret_get_body(self,body):
        self.send_response(200)
        if isinstance(body,str):
            body = body.encode()

        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_timeout(self):
        sys.stdout.write("-----> handle timeout! <-----")
        sys.stdout.flush()



class ThreadingHttpServer(HTTPServer,ThreadingMixIn):
    pass

class Http_Servre():
    def __init__(self):
        self.base_http_server_obj = None


    def __del__(self):
        if self.base_http_server_obj is not None:
            self.base_http_server_obj.server_close()

    def listen(self,ip:str,port:int):
        self.base_http_server_obj = ThreadingHttpServer((ip, port), MyHttpRequestHandler)
        self.base_http_server_obj.socket.settimeout(1)

    def run_forever(self):
        self.base_http_server_obj.serve_forever(poll_interval=0.5)

    def handle_request(self):
        self.base_http_server_obj._handle_request_noblock()
        #self.base_http_server_obj.timeout

class ConsumerManager(BaseManager):
        pass



#g_obj_loop = asyncio.get_event_loop()
g_obj_httpd = Http_Servre()

def logging_stdout():
    """ modify sys.stdout
    """
    import sys
    #origin = sys.stdout
    f = open(os.path.dirname(os.path.realpath(__file__)) +"\std.log", 'w')
    sys.stdout = f
    #sys.stdout = origin
    # ===================================
    #print('Start of program')

    #print('End of program')
    # ===================================

    #f.close()

#@asyncio.coroutine
def __http_request():
    #while True:
        sys.stdout.write("-----> Begin handle request! <-----")
        sys.stdout.flush()
        try:
            #timer_request()
            g_obj_httpd.run_forever()
        except Exception as e:
            logging.debug(repr(e))
            logging.debug("handle the request")
    #g_obj_loop.call_later(0.2, lambda: asyncio.async(__http_request()))

@time_out(2)
def timer_request():
    g_obj_httpd.handle_request()


def __async_init():
    try:
        fileHandler = logging.handlers.TimedRotatingFileHandler(os.path.dirname(os.path.realpath(__file__)) +"\service.log")
        logging.getLogger().addHandler(fileHandler)
        logging.getLogger().setLevel(logging.DEBUG)
        #logging_stdout()
        #__init_logger()
        #以后这里改成多进程结构的
        g_obj_httpd.listen('0.0.0.0',procVariable.port)

        #初始化处理结果集
        #ConsumerManager.register('get_result_queue')
        ConsumerManager.register('get_task_queue')
        ConsumerManager.register('get_result_queue')
        ConsumerManager.register('get_share_dict', dict, DictProxy)
        if procVariable.debug:
            singletonInstance.objShareMgr = ConsumerManager(address=('127.0.0.1', procVariable.sharePort), authkey=b'abc')
        else:
            singletonInstance.objShareMgr = ConsumerManager(address=('172.18.244.216', procVariable.sharePort),
                                                            authkey=b'abc')
        singletonInstance.objShareMgr.connect()

        singletonInstance.result_queue = singletonInstance.objShareMgr.get_result_queue()
        singletonInstance.task_queue = singletonInstance.objShareMgr.get_task_queue()
        singletonInstance.share_dict = singletonInstance.objShareMgr.get_share_dict()

        #开一个线程去处理
        resultThread = threading.Thread(name="result", target=check.checkResult, args=())
        resultThread.setDaemon(True)
        resultThread.start()

        #开一个线程去处理
        postThread = threading.Thread(name="post", target=post.postResult)
        postThread.setDaemon(True)
        postThread.start()

        # 开一个线程去处理
        postThread = threading.Thread(name="status", target=post.postStatus)
        postThread.setDaemon(True)
        postThread.start()

        #开一个线程去处理timer
        timerThread = threading.Thread(name="timer", target=timer.timerCheck)
        timerThread.setDaemon(True)
        timerThread.start()

        # TODO 优化
        #requestThread = threading.Thread(name="request", target=__http_request)
        #requestThread.start()
        #g_obj_loop.call_later(0.2, lambda: asyncio.async(__http_request()))
        #sys.stdout.write("-----> All modules start up successfully! <-----")
        #sys.stdout.flush()
        print("-----> All modules start up successfully! <-----")
        g_obj_httpd.run_forever()

    except Exception as e:
        logging.debug(repr(e))
        exit(0)



if "__main__" == __name__:

    parse = OptionParser(usage="%prog --rf <runFlag>")

    parse.add_option("--rf", "--runFlag", dest="runFlag", help="debug or release")
    parse.add_option("--p", "--port", dest="port", help="listen port")
    parse.add_option("--sp", "--sharePort", dest="sharePort", help="sharePort")

    (options, args) = parse.parse_args()

    runFlag = str(options.runFlag)
    procVariable.port = int(options.port)
    procVariable.sharePort = int(options.sharePort)

    if runFlag == "debug":
        procVariable.debug = True

    win32 = ctypes.windll.kernel32
    hin = win32.GetStdHandle(-10)
    mode = ctypes.c_int(0)
    win32.GetConsoleMode(hin, ctypes.byref(mode))
    old_mode = mode.value
    new_mode = old_mode & (~0x0040)
    win32.SetConsoleMode(hin,new_mode)

    __async_init()
