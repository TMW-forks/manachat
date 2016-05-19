import time
import net.mapserv as mapserv
import net.charserv as charserv
import commands
import walkto
import logicmanager
import status
import plugins
from collections import deque
from net.inventory import get_item_index, get_storage_index
from utils import extends
from actor import find_nearest_being
from chat import send_whisper as whisper


__all__ = [ 'PLUGIN', 'init' ]


PLUGIN = {
    'name': 'manaboy',
    'requires': ('chatbot', 'npc', 'autofollow'),
    'blocks': (),
}

npcdialog = {
    'start_time': -1,
    'program': [],
}

_times = {
    'follow': 0,
    'where' : 0,
    'status' : 0,
    'inventory' : 0,
    'say' : 0,
    'zeny' : 0,
    'storage' : 0,
}

admins = ['Trav', 'Travolta', 'Komornyik']
allowed_drops = [535, 719, 513, 727, 729, 869]

npc_owner = ''
history = deque(maxlen=10)
storage_is_open = False


def set_npc_owner(nick):
    global npc_owner
    if plugins.npc.npc_id < 0:
        npc_owner = nick


@extends('smsg_being_remove')
def bot_dies(data):
    if data.id == charserv.server.account:
        mapserv.cmsg_player_respawn()


@extends('smsg_npc_message')
@extends('smsg_npc_choice')
@extends('smsg_npc_close')
@extends('smsg_npc_next')
@extends('smsg_npc_int_input')
@extends('smsg_npc_str_input')
def npc_activity(data):
    npcdialog['start_time'] = time.time()


@extends('smsg_npc_message')
def npc_message(data):
    if not npc_owner:
        return

    npc = mapserv.beings_cache.findName(data.id)
    m = '[npc] {} : {}'.format(npc, data.message)
    whisper(npc_owner, m)


@extends('smsg_npc_choice')
def npc_choice(data):
    if not npc_owner:
        return

    choices = filter(lambda s: len(s.strip()) > 0,
        data.select.split(':'))

    whisper(npc_owner, '[npc][select] (use !input <number> to select)')
    for i, s in enumerate(choices):
        whisper(npc_owner, '    {}) {}'.format(i + 1, s))


@extends('smsg_npc_int_input')
@extends('smsg_npc_str_input')
def npc_input(data):
    if not npc_owner:
        return

    t = 'number'
    if plugins.npc.input_type == 'str':
        t = 'string'

    whisper(npc_owner, '[npc][input] (use !input <{}>)'.format(t))


@extends('smsg_storage_status')
def storage_status(data):
    print 'storage_status'
    global storage_is_open
    storage_is_open = True
    _times['storage'] = time.time()
    if npc_owner:
        whisper(npc_owner, '[storage]')


@extends('smsg_storage_items')
@extends('smsg_storage_equip')
def storage_items(data):
    if not npc_owner:
        return

    ls = status.invlists2(max_length=255, source='storage')

    for l in ls:
        whisper(npc_owner, l)


@extends('smsg_storage_close')
def storage_close(data):
    print 'smsg_storage_close'
    global storage_is_open
    storage_is_open = False
    _times['storage'] = 0


def cmd_where(nick, message, is_whisper, match):
    if not is_whisper:
        return

    msg = status.player_position()
    whisper(nick, msg)


def cmd_goto(nick, message, is_whisper, match):
    if not is_whisper:
        return

    try:
        x = int(match.group(1))
        y = int(match.group(2))
    except ValueError:
        return

    set_npc_owner(nick)
    plugins.autofollow.follow = ''
    mapserv.cmsg_player_change_dest(x, y)


def cmd_goclose(nick, message, is_whisper, match):
    if not is_whisper:
        return

    x = mapserv.player_pos['x']
    y = mapserv.player_pos['y']

    if message.startswith('!left'):
        x -= 1
    elif message.startswith('!right'):
        x += 1
    elif message.startswith('!up'):
        y -= 1
    elif message.startswith('!down'):
        y += 1

    set_npc_owner(nick)
    plugins.autofollow.follow = ''
    mapserv.cmsg_player_change_dest(x, y)


def cmd_pickup(nick, message, is_whisper, match):
    if not is_whisper:
        return

    commands.pickup()


def cmd_drop(nick, message, is_whisper, match):
    if not is_whisper:
        return

    try:
        amount = int(match.group(1))
        item_id = int(match.group(2))
    except ValueError:
        return

    if nick not in admins:
        if item_id not in allowed_drops:
            return

    index = get_item_index(item_id)
    if index > 0:
        mapserv.cmsg_player_inventory_drop(index, amount)


def cmd_item_action(nick, message, is_whisper, match):
    if not is_whisper:
        return

    try:
        itemId = int(match.group(1))
    except ValueError:
        return

    index = get_item_index(itemId)
    if index <= 0:
        return

    if message.startswith('!equip'):
        mapserv.cmsg_player_equip(index)
    elif message.startswith('!unequip'):
        mapserv.cmsg_player_unequip(index)
    elif message.startswith('!use'):
        mapserv.cmsg_player_inventory_use(index, itemId)


def cmd_emote(nick, message, is_whisper, match):
    if not is_whisper:
        return

    try:
        emote = int(match.group(1))
    except ValueError:
        return

    mapserv.cmsg_player_emote(emote)


def cmd_attack(nick, message, is_whisper, match):
    if not is_whisper:
        return

    target_s = match.group(1)

    try:
        target = mapserv.beings_cache[int(target_s)]
    except (ValueError, KeyError):
        target = find_nearest_being(name=target_s,
                                    ignored_ids=walkto.unreachable_ids)

    if target is not None:
        set_npc_owner(nick)
        plugins.autofollow.follow = ''
        walkto.walkto_and_action(target, 'attack')


def cmd_say(nick, message, is_whisper, match):
    if not is_whisper:
        return

    msg = match.group(1)
    whisper(nick, msg)


def cmd_sit(nick, message, is_whisper, match):
    if not is_whisper:
        return

    plugins.autofollow.follow = ''
    mapserv.cmsg_player_change_act(0, 2)


def cmd_turn(nick, message, is_whisper, match):
    if not is_whisper:
        return

    commands.set_direction('', message[6:])


def cmd_follow(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if plugins.autofollow.follow == nick:
        plugins.autofollow.follow = ''
    else:
        set_npc_owner(nick)
        plugins.autofollow.follow = nick


def cmd_lvlup(nick, message, is_whisper, match):
    if not is_whisper:
        return

    stat = match.group(1).lower()
    stats = {'str': 13, 'agi': 14, 'vit': 15,
             'int': 16, 'dex': 17, 'luk': 18}

    skills = {'mallard': 45, 'brawling': 350, 'speed': 352,
              'astral': 354, 'raging': 355, 'resist': 353}

    if stat in stats:
        mapserv.cmsg_stat_update_request(stats[stat], 1)
    elif stat in skills:
        mapserv.cmsg_skill_levelup_request(skills[stat])


def cmd_invlist(nick, message, is_whisper, match):
    if not is_whisper:
        return

    ls = status.invlists(50)
    for l in ls:
        whisper(nick, l)


def cmd_inventory(nick, message, is_whisper, match):
    if not is_whisper:
        return

    ls = status.invlists2(255)
    for l in ls:
        whisper(nick, l)


def cmd_status(nick, message, is_whisper, match):
    if not is_whisper:
        return

    all_stats = ('stats', 'hpmp', 'weight', 'points',
                 'zeny', 'attack', 'skills')

    sr = status.stats_repr(*all_stats)
    whisper(nick, ' | '.join(sr.values()))


def cmd_zeny(nick, message, is_whisper, match):
    if not is_whisper:
        return

    whisper(nick, 'I have {} GP'.format(mapserv.player_money))


def cmd_talk2npc(nick, message, is_whisper, match):
    if not is_whisper:
        return

    npc_s = match.group(1)
    jobs = []
    name = ''
    try:
        jobs = [int(npc_s)]
    except ValueError:
        name = npc_s

    b = find_nearest_being(name=name, type='npc', allowed_jobs=jobs)
    if b is None:
        return

    set_npc_owner(nick)
    plugins.autofollow.follow = ''
    plugins.npc.npc_id = b.id
    mapserv.cmsg_npc_talk(b.id)


def cmd_input(nick, message, is_whisper, match):
    if not is_whisper:
        return

    plugins.npc.cmd_npcinput('', match.group(1))


def cmd_close(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if storage_is_open:
        reset_storage()
    else:
        plugins.npc.cmd_npcclose()


def cmd_history(nick, message, is_whisper, match):
    if not is_whisper:
        return

    for user, cmd in history:
        whisper(nick, '{} : {}'.format(user, cmd))


def cmd_store(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if not storage_is_open:
        return

    try:
        amount = int(match.group(1))
        item_id = int(match.group(2))
    except ValueError:
        return

    index = get_item_index(item_id)
    if index > 0:
        mapserv.cmsg_move_to_storage(index, amount)


def cmd_retrieve(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if not storage_is_open:
        return

    try:
        amount = int(match.group(1))
        item_id = int(match.group(2))
    except ValueError:
        return

    index = get_storage_index(item_id)
    if index > 0:
        mapserv.cmsg_move_from_storage(index, amount)


def cmd_help(nick, message, is_whisper, match):
    if not is_whisper:
        return

    m = ('[@@https://forums.themanaworld.org/viewtopic.php?f=12&t=19673|Forum@@]'
         '[@@https://bitbucket.org/rumly111/manachat|Sources@@] '
         'Try !commands for list of commands')
    whisper(nick, m)


def cmd_commands(nick, message, is_whisper, match):
    if not is_whisper:
        return

    c = []
    for cmd in manaboy_commands:
        if cmd.startswith('!('):
            br = cmd.index(')')
            c.extend(cmd[2:br].split('|'))
        elif cmd.startswith('!'):
            c.append(cmd[1:].split()[0])

    c.sort()
    whisper(nick, ', '.join(c))


def reset_storage():
    mapserv.cmsg_storage_close()
    mapserv.cmsg_npc_list_choice(plugins.npc.npc_id, 6)


# =========================================================================
def manaboy_logic(ts):

    def reset():
        global npc_owner
        npc_owner = ''
        npcdialog['start_time'] = -1
        plugins.npc.cmd_npcinput('', '6')
        # plugins.npc.cmd_npcclose()

    if storage_is_open and ts > _times['storage'] + 150:
        reset_storage()

    if npcdialog['start_time'] <= 0:
        return

    if not storage_is_open and ts > npcdialog['start_time'] + 30.0:
        reset()


# =========================================================================
manaboy_commands = {
    '!where' : cmd_where,
    '!goto (\d+) (\d+)' : cmd_goto,
    '!(left|right|up|down)' : cmd_goclose,
    '!pickup' : cmd_pickup,
    '!drop (\d+) (\d+)' : cmd_drop,
    '!equip (\d+)' : cmd_item_action,
    '!unequip (\d+)' : cmd_item_action,
    '!use (\d+)' : cmd_item_action,
    '!emote (\d+)' : cmd_emote,
    '!attack (.+)' : cmd_attack,
    '!say ((@|#).+)' : cmd_say,
    '!sit' : cmd_sit,
    '!turn' : cmd_turn,
    '!follow' : cmd_follow,
    '!lvlup (\w+)' : cmd_lvlup,
    '!inventory' : cmd_inventory,
    '!invlist' : cmd_invlist,
    '!status' : cmd_status,
    '!zeny' : cmd_zeny,
    '!talk2npc (\w+)' : cmd_talk2npc,
    '!input (.+)' : cmd_input,
    '!close' : cmd_close,
    '!store (\d+) (\d+)' : cmd_store,
    '!retrieve (\d+) (\d+)' : cmd_retrieve,
    '!(help|info)' : cmd_help,
    '!commands' : cmd_commands,
    '!history' : cmd_history,
}


def chatbot_answer_mod(func):
    '''modifies chatbot.answer to remember last 10 commands'''

    def mb_answer(nick, message, is_whisper):
        if is_whisper:
            history.append((nick, message))
        return func(nick, message, is_whisper)

    return mb_answer


def init(config):
    for cmd, action in manaboy_commands.items():
        plugins.chatbot.add_command(cmd, action)

    plugins.chatbot.answer = chatbot_answer_mod(plugins.chatbot.answer)

    logicmanager.logic_manager.add_logic(manaboy_logic)
