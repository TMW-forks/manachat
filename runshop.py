#!/usr/bin/python2

import asyncore
import logging
import sys
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
from logicmanager import logic_manager


@extends('smsg_player_warp')
def player_warp(data):
    mapserv.cmsg_map_loaded()


@extends('smsg_map_login_success')
def map_login_success(data):
    mapserv.cmsg_map_loaded()


@extends('smsg_being_chat')
def being_chat(data):
    debuglog.info(data.message)


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


if __name__ == '__main__':
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(logging.NullHandler())

    dbgh = logging.StreamHandler(sys.stdout)
    dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                        datefmt="%Y-%m-%d %H:%M:%S"))
    debuglog.addHandler(dbgh)
    debuglog.setLevel(logging.INFO)

    shoplog = logging.getLogger('ManaChat.Shop')
    shoplog.addHandler(dbgh)

    config = ConfigParser()
    config.read('manachat.ini')

    load_itemdb('itemdb.txt')

    plugins.load_plugins(config)

    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

    try:
        while True:
            asyncore.loop(timeout=0.2, count=5)
            logic_manager.tick()
    except Exception:
        mapserv.cleanup()
