import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from optparse import OptionParser
from multiprocessing.managers import BaseManager

intScanFileIndex = 0




class ConsumerManager(BaseManager):
    pass



def scanFile(dirPath: str):
    global intScanFileIndex
    # strScanFile = "{}{}{}.jpg".format(dirPath, fileScanConfig.filePrefixName, intScanFileIndex)


if __name__ == "__main__":

    # global objShareMgr

    if float(str(sys.version_info[0]) + str(sys.version_info[1])) < 3.4:
        print("Found Python interpreter less 3.4 version not support: %s \n" % sys.version)

    else:

        parse = OptionParser(usage="%prog --rf <runFlag>")

        parse.add_option("--rf", "--runFlag", dest="runFlag", help="debug or release")
        parse.add_option("--input", "--i", dest="input", help="input mp4 or frame dir")

        (options, args) = parse.parse_args()

        runFlag = str(options.runFlag)
        input = str(options.input)

        '''
        if runFlag == "debug":
            procVariable.debug = True

        if input == "None" or len(input) <= 0:
            print("input file not valid")
            exit(0)

        if input.find(".mp4") > 0:
            procVariable.fileOrDir = True
            fileMp4 = open(input,"r")
            if fileMp4 is None:
                print("input mp4 not exist")
                exit(0)


        else:
            procVariable.fileOrDir = False
            #check dir is exist
            if not os.path.exists(input):
                print("input dir not exist")
                exit(0)
        '''
        ConsumerManager.register('get_task_queue')
        ConsumerManager.register('get_result_queue')
        ConsumerManager.register('get_cond')

        objShareMgr = ConsumerManager(address=('127.0.0.1', 50000), authkey=b'abc')
        objShareMgr.connect()

        task_queue = objShareMgr.get_task_queue()
        result_queue = objShareMgr.get_result_queue()
        condition = objShareMgr.get_cond()

        print(task_queue)
        print(result_queue)
        print(condition)



