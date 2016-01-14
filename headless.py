#!/usr/bin/python2

import asyncore
import logging
from ConfigParser import ConfigParser

try:
    import construct
    del construct
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.getcwd(), "external"))

import net
import net.mapserv as mapserv
import plugins
from utils import extends
from itemdb import load_itemdb


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

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        mapserv.cleanup()
