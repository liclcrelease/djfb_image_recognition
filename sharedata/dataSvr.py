import os,sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from multiprocessing.managers import BaseManager,ValueProxy,ListProxy,DictProxy
from multiprocessing import Condition
from multiprocessing.managers import Value
from optparse import OptionParser
from sharedata.proc import procVariable
import sys
import queue

objShareMgr = None
#这个size 很重要,和逻辑处理有关系
#搜索 queueSizeEndModify
task_q = queue.Queue(20)
result_q = queue.Queue(100)
kill_frame = Value('i',0)
tower_frame = Value('i',0)
dragon_frame = Value('i',0)

ten_kill_frame = Value('i',0)
first_dragon_att_frame = Value('i',0)
lol_check_list = list()


shareDict = dict()



if __name__ == "__main__":
    #global objShareMgr
    if float(str(sys.version_info[0]) + str(sys.version_info[1])) < 3.4:
        print("Found Python interpreter less 3.4 version not support: %s \n" % sys.version)

    else:

        parse = OptionParser(usage="%prog --rf <runFlag>")

        parse.add_option("--rf", "--runFlag", dest="runFlag", help="debug or release")
        parse.add_option("--p", "--port", dest="port", help="listen port")

        (options, args) = parse.parse_args()

        runFlag = str(options.runFlag)
        procVariable.port = int(options.port)

        if runFlag == "debug":
            procVariable.debug = True


    try:
        BaseManager.register('get_task_queue',callable=lambda: task_q)
        BaseManager.register('get_result_queue',callable=lambda : result_q)
        #用代理value 不用注册condition

        '''
        #wzry
        BaseManager.register('get_kill_frame', callable=lambda: kill_frame,proxytype=ValueProxy)
        BaseManager.register('get_tower_kill_frame', callable=lambda: tower_frame, proxytype=ValueProxy)
        BaseManager.register('get_dragon_kill_frame', callable=lambda: dragon_frame, proxytype=ValueProxy)

        #lol
        BaseManager.register('get_ten_kill', callable=lambda: ten_kill_frame, proxytype=ValueProxy)
        BaseManager.register('first_dragon_att', callable=lambda: first_dragon_att_frame, proxytype=ValueProxy)
        BaseManager.register('get_checking_list', callable=lambda: lol_check_list, proxytype=ListProxy)
        '''
        BaseManager.register('get_share_dict', callable=lambda: shareDict, proxytype=DictProxy)


        objShareMgr = BaseManager(address=('0.0.0.0', procVariable.port), authkey=b'abc')
        server = objShareMgr.get_server()
        server.serve_forever()
    except KeyboardInterrupt:
        objShareMgr.shutdown()
    except Exception as e:
        print(repr(e))
        pass