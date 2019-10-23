#!/usr/bin/python2

# ManaChat simple frontend. Works only on *nix

import asyncore
import logging
import os
import sys
import readline
import thread
import struct
import fcntl
import termios
from collections import deque
from ConfigParser import ConfigParser

try:
    import construct
    del construct
except ImportError:
    import os
    sys.path.insert(0, os.path.join(os.getcwd(), "external"))

import net
import net.mapserv as mapserv
import plugins
from utils import extends
from itemdb import load_itemdb
from monsterdb import read_monster_db
from loggers import debuglog
import commands
from logicmanager import logic_manager


PROMPT = '] '
input_buffer = deque()


def input_thread():
    while True:
        s = raw_input(PROMPT)
        input_buffer.append(s)


class DebugLogHandler(logging.Handler):

    def clear_curr_input(self):
        # http://stackoverflow.com/questions/2082387/reading-input-from-raw-input-without-having-the-prompt-overwritten-by-other-th?rq=1
        _, cols = struct.unpack('hh',
            fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))
        tl = len(readline.get_line_buffer()) + len(PROMPT)
        # ANSI escape sequences (All VT100 except ESC[0G)
        sys.stdout.write('\x1b[2K')                       # Clear current line
        sys.stdout.write('\x1b[1A\x1b[2K' * (tl / cols))  # cur up & clr line
        sys.stdout.write('\x1b[0G')                       # to start of line

    def emit(self, record):
        self.clear_curr_input()
        print self.format(record)
        sys.stdout.write(PROMPT + readline.get_line_buffer())
        sys.stdout.flush()


@extends('smsg_player_warp')
def player_warp(data):
    mapserv.cmsg_map_loaded()
    m = "[warp] {} ({},{})".format(data.map, data.x, data.y)
    debuglog.info(m)


@extends('smsg_map_login_success')
def map_login_success(data):
    mapserv.server.raw = True
    mapserv.cmsg_map_loaded()


@extends('smsg_whisper_response')
def send_whisper_result(data):
    if data.code == 0:
        if len(readline.get_line_buffer()) == 0:
            last_nick = mapserv.last_whisper['to']
            readline.insert_text('/w "{}" '.format(last_nick))
            readline.redisplay()


if __name__ == '__main__':
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(logging.NullHandler())

    dbgh = DebugLogHandler()
    dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                        datefmt="%Y-%m-%d %H:%M:%S"))
    debuglog.addHandler(dbgh)
    debuglog.setLevel(logging.INFO)

    config_ini = 'manachat.ini'
    if len(sys.argv) > 1:
        if sys.argv[1].endswith('.ini') and os.path.isfile(sys.argv[1]):
            config_ini = sys.argv[1]
    config = ConfigParser()
    config.read(config_ini)

    if config.getboolean('Other', 'log_network_packets'):
        from loggers import netlog
        netlog.setLevel(logging.INFO)
        fh = logging.FileHandler('/tmp/netlog.txt', mode="w")
        fmt = logging.Formatter("[%(asctime)s] %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fmt)
        netlog.addHandler(fh)

    load_itemdb('itemdb.txt')
    read_monster_db('monsterdb.txt')

    plugins.load_plugins(config)

    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

    thread.start_new_thread(input_thread, ())

    while True:
        if len(input_buffer) > 0:
            for l in input_buffer:
                commands.process_line(l)
            input_buffer.clear()

        asyncore.loop(timeout=0.2, count=5)
        logic_manager.tick()
