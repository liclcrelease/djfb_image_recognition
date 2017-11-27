from datetime import datetime
import time


def getNow()->int:
    tc = datetime.now().timetuple()
    return int(time.mktime(tc))
