import net.mapserv as mapserv
import net.charserv as charserv
from net.common import distance
from utils import extends, Schedule
# from loggers import debuglog


__all__ = [ 'PLUGIN', 'init', 'target_id' ]


PLUGIN = {
    'name': 'battlebot',
    'requires': (),
    'blocks': (),
}

target_id = 0


@extends('smsg_being_action')
def being_action(data):
    global target_id
    if data.type in (0, 10):
        if target_id == 0 and data.dst_id == charserv.server.account:
            target_id = data.src_id
            mapserv.cmsg_player_change_act(target_id, 7)


@extends('smsg_being_remove')
def being_remove(data):
    global target_id
    if target_id == data.id:
        target_id = 0


@extends('smsg_being_move')
def being_move(data):
    global target_id
    if target_id == data.id:
        target_id = 0


@extends('smsg_item_dropped')
@extends('smsg_item_visible')
def flooritem_appears(data):
    p_x = mapserv.player_pos['x']
    p_y = mapserv.player_pos['y']
    dist = distance(p_x, p_y, data.x, data.y)
    # debuglog.info('p.x=%d p.y=%d i.x=%d i.y=%d dist=%d',
    #               p_x, p_y, data.x, data.y, dist)
    if dist < 2:
        mapserv.cmsg_item_pickup(data.id)
    else:
        mapserv.cmsg_player_change_dest(data.x, data.y)
        # NOTE: will this object be garbage collected?
        Schedule(dist * 0.4, 0, mapserv.cmsg_item_pickup, data.id)


def init(config):
    pass
