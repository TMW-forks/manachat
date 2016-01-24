import net.mapserv as mapserv
import net.charserv as charserv
import net.stats as stats
from net.common import distance
from net.inventory import get_item_index
from utils import extends, Schedule
from loggers import debuglog


__all__ = [ 'PLUGIN', 'init', 'target_id',
            'hp_healing_ids', 'hp_heal_at', 'mp_healing_ids', 'mp_heal_at',
            'auto_attack', 'auto_pickup', 'auto_heal_self',
            'auto_heal_others' ]


PLUGIN = {
    'name': 'battlebot',
    'requires': (),
    'blocks': (),
}

target_id = 0

hp_healing_ids = [ 535, 541 ]
hp_heal_at = 0.3
hp_is_healing = False
hp_prev_value = 0

mp_healing_ids = [ 826 ]
mp_heal_at = 0.5
mp_is_healing = False
mp_prev_value = 0

players_taken_damage = {}
player_damage_heal = 300

auto_pickup = False
auto_attack = False
auto_heal_self = True
auto_heal_others = True


@extends('smsg_being_action')
def being_action(data):
    if not auto_attack:
        return

    global target_id
    if data.type in (0, 10):

        if (auto_attack and target_id == 0 and
                data.dst_id == charserv.server.account):
            target_id = data.src_id
            mapserv.cmsg_player_change_act(target_id, 7)

        if (auto_heal_others and
                data.dst_id != charserv.server.account and
                data.dst_id in mapserv.beings_cache and
                mapserv.beings_cache[data.dst_id].type == 'player'):

            players_taken_damage[data.dst_id] = players_taken_damage.get(
                data.dst_id, 0) + data.damage

            if players_taken_damage[data.dst_id] >= player_damage_heal:
                mapserv.cmsg_chat_message("#inma {}".format(
                    mapserv.beings_cache[data.dst_id].name))
                players_taken_damage[data.dst_id] = 0


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


@extends('smsg_player_status_change')
def player_status_change(data):
    global hp_is_healing
    if data.id == charserv.server.account:
        if data.effect == 256:
            hp_is_healing = True
        elif data.effect == 0:
            hp_is_healing = False


@extends('smsg_player_stat_update_x')
def player_stat_update(data):
    if not auto_heal_self:
        return

    global hp_prev_value, mp_prev_value

    if data.type == stats.HP:
        max_hp = mapserv.player_stats.get(stats.MAX_HP, 0)
        if data.stat_value < max_hp * hp_heal_at and not hp_is_healing:
            healing_found = False
            for item_id in hp_healing_ids:
                index = get_item_index(item_id)
                if index > 0:
                    healing_found = True
                    debuglog.info("Consuming %d", item_id)
                    mapserv.cmsg_player_inventory_use(index, item_id)
                    break
            if not healing_found:
                debuglog.info("Low health, but no HP healing item found")

        hp_prev_value = data.stat_value

    elif data.type == stats.MP:
        max_mp = mapserv.player_stats.get(stats.MAX_MP, 0)
        if data.stat_value < max_mp * mp_heal_at and not mp_is_healing:
            healing_found = False
            for item_id in mp_healing_ids:
                index = get_item_index(item_id)
                if index > 0:
                    healing_found = True
                    debuglog.info("Consuming %d", item_id)
                    mapserv.cmsg_player_inventory_use(index, item_id)
                    break

            if not healing_found:
                debuglog.info("Low mana, but no MP healing item found")

        mp_prev_value = data.stat_value


def init(config):
    pass
