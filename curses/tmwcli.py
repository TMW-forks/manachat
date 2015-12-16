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
sys.path.append(parent)
sys.path.append(os.path.join(parent, "net"))
del parent

import loginsrv
from common import netlog
# from utils import Schedule
import cui
import handlers
import commands
import config


if __name__ == "__main__":
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(logging.NullHandler())

    netlog.setLevel(logging.DEBUG)
    fh = logging.FileHandler("/tmp/netlog.txt", mode="w")
    fmt = logging.Formatter("[%(asctime)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt)
    netlog.addHandler(fh)

    handlers.register_all()

    cui.init()

    loginsrv.connect(config.server, config.port)
    loginsrv.cmsg_server_version_request()

    t = threading.Thread(target=asyncore.loop)
    t.setDaemon(True)
    t.start()

    cui.input_loop(commands.process_line)
    cui.finalize()

    import mapserv
    mapserv.cleanup()
