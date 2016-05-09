import net.mapserv as mapserv
import commands
from utils import extends
from loggers import debuglog


__all__ = [ 'PLUGIN', 'init', 'follow' ]


PLUGIN = {
    'name': 'autofollow',
    'requires': (),
    'blocks': (),
}

follow = ''


@extends('smsg_player_move')
def player_move(data):
    if follow:
        b = mapserv.beings_cache[data.id]
        if b.name == follow:
            mapserv.cmsg_player_change_dest(data.coor_pair.dst_x,
                                            data.coor_pair.dst_y)


def follow_cmd(_, player):
    '''Follow given player, or disable following (if no arg)'''
    global follow
    follow = player
    if player:
        debuglog.info('Following %s', player)
    else:
        debuglog.info('Not following anyone')


def init(config):
    commands.commands['follow'] = follow_cmd
