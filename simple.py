#!/usr/bin/python2

# ManaChat simple frontend. Works only on *nix

import asyncore
import logging
import sys
import readline
import thread
import struct
import fcntl
import termios
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
from loggers import debuglog
import commands


PROMPT = '] '


def input_thread():
    while True:
        s = raw_input(PROMPT)
        commands.process_line(s)


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


@extends('smsg_map_login_success')
def map_login_success(data):
    mapserv.cmsg_map_loaded()


@extends('smsg_being_chat')
def being_chat(data):
    id_, message = data.id, data.message
    nick = mapserv.beings_cache[id_].name
    m = "{} : {}".format(nick, message)
    debuglog.info(m)


@extends('smsg_player_chat')
def player_chat(data):
    debuglog.info(data.message)


@extends('smsg_whisper')
def got_whisper(data):
    nick, message = data.nick, data.message
    m = "[{} ->] {}".format(nick, message)
    debuglog.info(m)


@extends('smsg_gm_chat')
def gm_chat(data):
    m = "[GM] {}".format(data.message)
    debuglog.info(m)


@extends('smsg_whisper_response')
def send_whisper_result(data):
    if data.code == 0:
        m = "[-> {}] {}".format(commands.whisper_to, commands.whisper_msg)
        debuglog.info(m)
        readline.insert_text('/w "{}" '.format(commands.whisper_to))
        readline.redisplay()
    else:
        debuglog.warning("[error] {} is offline.".format(
            commands.whisper_to))


if __name__ == '__main__':
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(logging.NullHandler())

    dbgh = DebugLogHandler()
    dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                        datefmt="%Y-%m-%d %H:%M:%S"))
    debuglog.addHandler(dbgh)
    debuglog.setLevel(logging.INFO)

    config = ConfigParser()
    config.read('manachat.ini')

    load_itemdb('itemdb.txt')
    plugin_list = config.get('Core', 'plugins').split()
    plugins.load_plugins(config, *plugin_list)

    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

    thread.start_new_thread(input_thread, ())

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        mapserv.cleanup()
