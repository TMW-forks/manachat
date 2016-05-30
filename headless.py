#!/usr/bin/python2

import os
import sys
import asyncore
import logging
from ConfigParser import ConfigParser

try:
    import construct
    del construct
except ImportError:
    sys.path.insert(0, os.path.join(os.getcwd(), "external"))

import net
import net.mapserv as mapserv
import plugins
from utils import extends
from itemdb import load_itemdb
from logicmanager import logic_manager


@extends('smsg_player_warp')
def player_warp(data):
    mapserv.cmsg_map_loaded()


@extends('smsg_map_login_success')
def map_login_success(data):
    mapserv.cmsg_map_loaded()


if __name__ == '__main__':
    logging.basicConfig(format="[%(asctime)s] %(message)s",
                        level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S")

    config_ini = 'manachat.ini'
    if len(sys.argv) > 1:
        if sys.argv[1].endswith('.ini') and os.path.isfile(sys.argv[1]):
            config_ini = sys.argv[1]
    config = ConfigParser()
    config.read(config_ini)

    load_itemdb('itemdb.txt')

    plugins.load_plugins(config)

    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

    while True:
        asyncore.loop(timeout=0.2, count=5)
        logic_manager.tick()
