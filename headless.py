#!/usr/bin/python2

import asyncore
import logging
from ConfigParser import ConfigParser

import net
import net.mapserv as mapserv
from utils import register_extension


def player_warp(data):
    mapserv.cmsg_map_loaded()


if __name__ == '__main__':
    logging.basicConfig(format="[%(asctime)s] %(message)s",
                        level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S")
    config = ConfigParser()
    config.read('manachat.ini')

    register_extension('smsg_player_warp', player_warp)

    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        mapserv.cleanup()
