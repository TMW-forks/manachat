#!/usr/bin/python2

import os
import sys
import logging
import asyncore
import curses

# add ../net to PYTHONPATH
parent, _ = os.path.split(os.getcwd())
sys.path.append(os.path.join(parent, "net"))
del parent

import loginsrv
from common import netlog
import cui


if __name__ == "__main__":
    cui.init()
    cui.input_loop(cui.chatlog_append)
    cui.finalize()
    sys.exit()
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    netlog.setLevel(logging.ERROR)

    loginsrv.connect('server.themanaworld.org', 6902, 'john_doe', '123456')
    loginsrv.cmsg_server_version_request()
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        import mapserv
        mapserv.cleanup()
