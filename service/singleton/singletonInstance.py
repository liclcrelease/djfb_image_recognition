from queue import Queue

g_serverData = {}
g_matchData = {}

objShareMgr = None
result_queue = None
task_queue = None
share_dict = None

g_postQueue = Queue()

g_scanFileThread = {}