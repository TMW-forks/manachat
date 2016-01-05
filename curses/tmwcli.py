#!/usr/bin/python2

import os
import sys
import logging
import time
import asyncore
import threading
from ConfigParser import ConfigParser

# add .. to PYTHONPATH
parent, _ = os.path.split(os.getcwd())
sys.path.insert(0, parent)

try:
    import construct
    del construct
except ImportError:
    sys.path.insert(1, os.path.join(parent, "external"))

del parent

import cui
import handlers
import net
import net.mapserv as mapserv
from commands import process_line
from net.onlineusers import OnlineUsers
from loggers import netlog, debuglog


class SideBarUpdater(threading.Thread):

    def __init__(self, window, online_users_obj, update_interval=20):
        self._active = True
        self._timer = 0
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

    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

    t = threading.Thread(target=asyncore.loop)
    t.setDaemon(True)
    t.start()

    cui.input_loop(process_line)

    side_bar_updater.stop()
    online_users.stop()
    cui.finalize()

    mapserv.cleanup()
