#!/usr/bin/python2

import os
import sys
import logging
import time
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
from onlineusers import OnlineUsers


class SideBarUpdater(threading.Thread):

    def __init__(self, window, online_users_obj, update_interval=20):
        self._active = True
        self._timer = 0
        # self._thread = threading.Thread(target=self._threadfunc, args=())
        self._update_interval = update_interval
        self._online_users_obj = online_users_obj
        self._window = window
        threading.Thread.__init__(self)

    def run(self):
        while self._active:
            if (time.time() - self._timer) > self._update_interval:
                self._window.clear()
                for user in self._online_users_obj.online_users:
                    print user
                    self._window.addstr(user + '\n')
                self._window.refresh()
                self._timer = time.time()
            else:
                time.sleep(1.0)

    def stop(self):
        self._active = False


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

    online_users = OnlineUsers(config.online_txt_url)
    online_users.start()
    side_bar_updater = SideBarUpdater(cui.players_win, online_users)
    side_bar_updater.start()

    loginsrv.connect(config.server, config.port)
    loginsrv.cmsg_server_version_request()

    t = threading.Thread(target=asyncore.loop)
    t.setDaemon(True)
    t.start()

    cui.input_loop(commands.process_line)

    side_bar_updater.stop()
    online_users.stop()
    cui.finalize()

    import mapserv
    mapserv.cleanup()
