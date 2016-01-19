import time
import net.mapserv as mapserv
import net.charserv as charserv
import net.stats as stats
from net.common import distance
from net.inventory import get_item_index
from utils import extends, Schedule
# from loggers import debuglog


__all__ = [ 'PLUGIN', 'init', 'target_id',
            'hp_healing_ids', 'hp_heal_at', 'mp_healing_ids', 'mp_heal_at',
            'auto_attack', 'auto_pickup', 'auto_heal' ]


PLUGIN = {
    'name': 'battlebot',
    'requires': (),
    'blocks': (),
}

target_id = 0
hp_healing_ids = [ 535, 541 ]
hp_heal_at = 0.3
hp_last_healed = 0
mp_healing_ids = []
mp_heal_at = 0.5
mp_last_healed = 0
auto_pickup = True
auto_attack = True
auto_heal = True


@extends('smsg_being_action')
def being_action(data):
    if not auto_attack:
        return

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
    if not auto_pickup:
        return

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


@extends('smsg_player_stat_update_x')
def player_stat_update(data):
    global hp_last_healed, mp_last_healed

    if not auto_heal:
        return

    if data.type == stats.HP:
        max_hp = mapserv.player_stats.get(stats.MAX_HP, 0)
        if data.stat_value < max_hp * hp_heal_at:
            now = time.time()
            if now > hp_last_healed + 2:
                for item_id in hp_healing_ids:
                    index = get_item_index(item_id)
                    if index > 0:
                        mapserv.cmsg_player_inventory_use(index, item_id)
                        hp_last_healed = now
                        break

    elif data.type == stats.MP:
        max_mp = mapserv.player_stats.get(stats.MAX_MP, 0)
        if data.stat_value < max_mp * mp_heal_at:
            now = time.time()
            if now > mp_last_healed + 2:
                for item_id in mp_healing_ids:
                    index = get_item_index(item_id)
                    if index > 0:
                        mapserv.cmsg_player_inventory_use(index, item_id)
                        mp_last_healed = now
                        break


def init(config):
    pass
