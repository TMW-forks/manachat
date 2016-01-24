
"""
Copyright 2015-2016, Joseph Botosh <rumly111@gmail.com>

This file is part of tradey, a trading bot in The Mana World
see www.themanaworld.org

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

Additionally to the GPL, you are *strongly* encouraged to share any
modifications you do on these sources.
"""

import urllib2
import string
import threading
import time

from common import netlog


class OnlineUsers(threading.Thread):

    def __init__(self, online_url='http://server.themanaworld.org/online.txt',
                 update_interval=60, refresh_hook=None):
        self._active = True
        self._timer = 0
        self._url = online_url
        self._update_interval = update_interval
        self.__lock = threading.Lock()
        self.__online_users = []
        self.refresh_hook = refresh_hook
        threading.Thread.__init__(self)

    @property
    def online_users(self):
        self.__lock.acquire(True)
        users = self.__online_users[:]
        self.__lock.release()
        return users

    @staticmethod
    def dl_online_list(url):
        """
        Download online.txt, parse it, and return a list of online user nicks.
        If error occurs, return empty list
        """
        try:
            data = urllib2.urlopen(url).read()
        except urllib2.URLError, e:
            netlog.error("urllib error: %s", e.message)
            return []
        start = string.find(data, '------------------------------\n') + 31
        end = string.rfind(data, '\n\n')
        s = data[start:end]
        return map(lambda n: n[:-5].strip() if n.endswith('(GM) ')
                   else n.strip(), s.split('\n'))

    def run(self):
        while self._active:
            if (time.time() - self._timer) > self._update_interval:
                users = self.dl_online_list(self._url)

                if self.refresh_hook:
                    self.refresh_hook(set(users), set(self.__online_users))

                self.__lock.acquire(True)
                self.__online_users = users
                self.__lock.release()
                self._timer = time.time()
            else:
                time.sleep(1.0)

    def stop(self):
        self._active = False
