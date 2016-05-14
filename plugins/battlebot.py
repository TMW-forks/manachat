import time
import net.mapserv as mapserv
import net.charserv as charserv
import net.stats as stats
import walkto
import logicmanager
import commands
from net.common import distance
from net.inventory import get_item_index
from utils import extends
from loggers import debuglog
from actor import find_nearest_being


__all__ = [ 'PLUGIN', 'init',
            'hp_healing_ids', 'hp_heal_at', 'mp_healing_ids', 'mp_heal_at',
            'auto_attack', 'auto_pickup', 'auto_heal_self',
            'auto_heal_others' ]


PLUGIN = {
    'name': 'battlebot',
    'requires': (),
    'blocks': (),
}

target = None
# last_time_attacked = 0
aa_next_time = 0

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

aa_monster_types = []

auto_pickup = True
auto_attack = False
auto_heal_self = False
auto_heal_others = False


@extends('smsg_being_action')
def being_action(data):
    # global last_time_attacked
    global aa_next_time

    if data.type in (0, 10):

        if data.src_id == charserv.server.account:
            # last_time_attacked = time.time()
            aa_next_time = time.time() + 5.0

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


@extends('smsg_item_dropped')
@extends('smsg_item_visible')
def flooritem_appears(data):
    if not auto_pickup:
        return

    item = mapserv.floor_items[data.id]
    px = mapserv.player_pos['x']
    py = mapserv.player_pos['y']

    if distance(px, py, item.x, item.y) > 3:
        return

    walkto.walkto_and_action(item, 'pickup')


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


@extends('smsg_being_remove')
def being_remove(data):
    global target
    if target is not None and target.id == data.id:
        target = None
        aa_next_time = time.time() + 5.0


def battlebot_logic(ts):

    if not auto_attack:
        return

    global target
    # global last_time_attacked
    global aa_next_time

    if ts < aa_next_time:
        return

    if target is None:
        if walkto.state:
            return

        target = find_nearest_being(type='monster',
                                    ignored_ids=walkto.unreachable_ids,
                                    allowed_jobs=aa_monster_types)
        if target is not None:
            # last_time_attacked = time.time()
            aa_next_time = time.time() + 5.0
            walkto.walkto_and_action(target, 'attack')

    elif ts > aa_next_time:
        walkto.walkto_and_action(target, 'attack')


def startbot(_, arg):
    '''Start autoattacking and autolooting'''
    global auto_attack
    global auto_pickup
    global aa_monster_types
    auto_attack = True
    auto_pickup = True
    try:
        aa_monster_types = map(int, arg.split())
    except ValueError:
        aa_monster_types = []


def stopbot(cmd, _):
    '''Stop battlebot'''
    global auto_attack
    global auto_pickup
    global auto_heal_self
    global auto_heal_others
    global target
    auto_attack = False
    auto_pickup = False
    auto_heal_self = False
    auto_heal_others = False
    if target is not None:
        mapserv.cmsg_player_stop_attack()
        target = None


def debugbot(cmd, _):
    px = mapserv.player_pos['x']
    py = mapserv.player_pos['y']
    target_info = '<no_target>'
    if target is not None:
        target_info = '{} at ({},{})'.format(target.name, target.x, target.y)
    debuglog.info('target = %s | player at (%d, %d)', target_info, px, py)


bot_commands = {
    'startbot' : startbot,
    'stopbot'  : stopbot,
    'debugbot' : debugbot,
}


def init(config):
    logicmanager.logic_manager.add_logic(battlebot_logic)
    commands.commands.update(bot_commands)
