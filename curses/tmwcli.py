#!/usr/bin/python2

import os
import sys
import logging
import asyncore
import curses
import threading
from time import gmtime, strftime

# add ../net to PYTHONPATH
parent, _ = os.path.split(os.getcwd())
sys.path.append(os.path.join(parent, "net"))
del parent

import loginsrv
from common import netlog
# from utils import Schedule
import cui
import handlers
import commands

# def print_time():
#     now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
#     cui.chatlog_append(now)

    # s = Schedule(5, 7, print_time)
    # s.cancel()
    # sys.exit()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.ERROR,
    #                     format='%(asctime)s %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(logging.NullHandler())

    netlog.setLevel(logging.ERROR)

    handlers.register_all()

    cui.init()

    loginsrv.connect('server.themanaworld.org', 6902, 'john_doe', '123456')
    loginsrv.cmsg_server_version_request()

    t = threading.Thread(target=asyncore.loop)
    t.setDaemon(True)
    t.start()

    cui.input_loop(commands.process_line)
    cui.finalize()

    import mapserv
    mapserv.cleanup()
