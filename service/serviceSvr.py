import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
import asyncio
import threading
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



class MyHttpRequestHandler(SimpleHTTPRequestHandler):


    def do_GET(self):
        listParam = self.path[1:].split("?")
        if len(listParam) <= 1:
            return self.ret_get_body('{"ret":0,"des":"invalid param"}')

        strMethod = listParam[0]
        print(self.path)
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

    def run_forever(self):
        self.base_http_server_obj.serve_forever(poll_interval=0.5)

    def handle_request(self):
        self.base_http_server_obj.handle_request()

class ConsumerManager(BaseManager):
        pass


#全局变量
g_obj_loop = asyncio.get_event_loop()
g_obj_httpd = Http_Servre()

@asyncio.coroutine
def __http_request():
    g_obj_httpd.handle_request()
    print("handle the request")
    g_obj_loop.call_later(0.2, lambda: asyncio.async(__http_request()))


@asyncio.coroutine
def __async_init():
    try:
        #__init_logger()
        #以后这里改成多进程结构的
        g_obj_httpd.listen('0.0.0.0',procVariable.port)

        #初始化处理结果集
        #ConsumerManager.register('get_result_queue')
        ConsumerManager.register('get_task_queue')
        ConsumerManager.register('get_result_queue')
        ConsumerManager.register('get_share_dict', dict, DictProxy)
        singletonInstance.objShareMgr = ConsumerManager(address=('127.0.0.1', procVariable.sharePort), authkey=b'abc')
        singletonInstance.objShareMgr.connect()

        singletonInstance.result_queue = singletonInstance.objShareMgr.get_result_queue()
        singletonInstance.task_queue = singletonInstance.objShareMgr.get_task_queue()
        singletonInstance.share_dict = singletonInstance.objShareMgr.get_share_dict()

        #开一个线程去处理
        resultThread = threading.Thread(name="result", target=check.checkResult, args=())
        resultThread.start()

        #开一个线程去处理
        postThread = threading.Thread(name="post", target=post.postResult)
        postThread.start()


        # TODO 优化
        g_obj_loop.call_later(0.2, lambda: asyncio.async(__http_request()))

        sys.stdout.write("-----> All modules start up successfully! <-----")
        sys.stdout.flush()

    except Exception as e:
        print(repr(e))
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

    asyncio.async(__async_init())
    try:
        g_obj_loop.run_forever()
    except KeyboardInterrupt as e:
        print(asyncio.Task.all_tasks())
        print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
        g_obj_loop.stop()
        g_obj_loop.run_forever()
    finally:
        g_obj_loop.close()
