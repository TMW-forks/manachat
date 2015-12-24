#!/usr/bin/python2

import asyncore
import logging
from ConfigParser import ConfigParser

import net.loginsrv as loginsrv
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

    loginsrv.connect(config.get('Server', 'host'),
                     config.getint('Server', 'port'))

    loginsrv.server.username = config.get('Player', 'username')
    loginsrv.server.password = config.get('Player', 'password')
    loginsrv.server.char_name = config.get('Player', 'charname')

    loginsrv.cmsg_server_version_request()

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        mapserv.cleanup()
