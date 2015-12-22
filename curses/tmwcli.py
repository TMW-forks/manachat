#!/usr/bin/python2

import os
import sys
import logging
import time
import asyncore
import threading

# add .. to PYTHONPATH
parent, _ = os.path.split(os.getcwd())
sys.path.append(parent)
del parent

from net import loginsrv
from ConfigParser import ConfigParser

import cui
import handlers
import commands
from net.onlineusers import OnlineUsers
from loggers import netlog, debuglog


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


class CursesDebugLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        cui.chatlog_append(msg)


if __name__ == "__main__":
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(logging.NullHandler())

    dbgh = CursesDebugLogHandler()
    dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                        datefmt="%H:%M"))
    debuglog.addHandler(dbgh)
    debuglog.setLevel(logging.INFO)

    fh = logging.FileHandler("/tmp/netlog.txt", mode="w")
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S"))
    netlog.addHandler(fh)
    netlog.setLevel(logging.INFO)

    handlers.register_all()

    config = ConfigParser()
    config.read('../manachat.ini')

    cui.init()

    online_users = OnlineUsers(config.get('Other', 'online_txt_url'))
    online_users.start()
    side_bar_updater = SideBarUpdater(cui.players_win, online_users)
    side_bar_updater.start()

    loginsrv.connect(config.get('Server', 'host'),
                     config.getint('Server', 'port'))

    loginsrv.server.username = config.get('Player', 'username')
    loginsrv.server.password = config.get('Player', 'password')
    loginsrv.server.char_name = config.get('Player', 'charname')

    loginsrv.cmsg_server_version_request()

    t = threading.Thread(target=asyncore.loop)
    t.setDaemon(True)
    t.start()

    cui.input_loop(commands.process_line)

    side_bar_updater.stop()
    online_users.stop()
    cui.finalize()

    from net import mapserv
    mapserv.cleanup()
