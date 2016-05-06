
import net.mapserv as mapserv
from net.inventory import get_item_index
import monsterdb
import itemdb
from utils import preprocess_argument
from textutils import expand_links
from loggers import debuglog

__all__ = [ 'whisper_msg', 'whisper_to', 'commands',
            'parse_player_name', 'process_line',
            'must_have_arg' ]

whisper_to = ''
whisper_msg = ''


def must_have_arg(func):

    def wrapper(cmd, arg):
        if len(arg) > 0:
            return func(cmd, arg)

    wrapper.__doc__ = func.__doc__
    return wrapper


@preprocess_argument(expand_links)
def general_chat(msg):
    '''Send message to #General chat'''
    mapserv.cmsg_chat_message(msg)


@preprocess_argument(expand_links, 1)
def send_whisper(to_, msg):
    '''Send whisper to player'''
    global whisper_to, whisper_msg
    whisper_to = to_
    whisper_msg = msg
    mapserv.cmsg_chat_whisper(to_, msg)


@must_have_arg
def send_whisper_internal(_, arg):
    '''Send whisper to player
/w "Player Name" Message...
/w NameWithourSpaces Message'''
    nick, message = parse_player_name(arg)
    if len(nick) > 0 and len(message) > 0:
        send_whisper(nick, message)


@preprocess_argument(expand_links)
def send_party_message(msg):
    '''Sent message to party'''
    mapserv.cmsg_party_message(msg)


@must_have_arg
def send_party_message_internal(_, arg):
    '''Sent message to party'''
    send_party_message(arg)


@must_have_arg
def set_direction(_, dir_str):
    '''/turn down|up|left|right'''
    d = {"down": 0, "left": 2, "up": 4, "right": 6}
    dir_num = d.get(dir_str.lower(), 0)
    mapserv.cmsg_player_change_dir(dir_num)


def sit_or_stand(cmd, _):
    '''Use /sit or /stand for corresponding action'''
    a = {"sit": 2, "stand": 3}
    try:
        action = a[cmd]
        mapserv.cmsg_player_change_act(0, action)
    except KeyError:
        pass


@must_have_arg
def set_destination(_, xy):
    '''/goto x y  -- walk to given coordinates'''
    try:
        x, y = map(int, xy.split())
        mapserv.cmsg_player_change_dest(x, y)
    except ValueError:
        pass


@must_have_arg
def show_emote(_, emote):
    '''Smile!
/emote ID'''
    try:
        mapserv.cmsg_player_emote(int(emote))
    except ValueError:
        pass


@must_have_arg
def attack(_, name_or_id):
    '''Attack being (ID or Name)'''
    target_id = -10
    mob_db = monsterdb.monster_db

    try:
        target_id = int(name_or_id)
        if target_id not in mapserv.beings_cache:
            raise ValueError
    except ValueError:
        for b in mapserv.beings_cache:
            if b.name == name_or_id:
                target_id = b.id
                break
            if b.job in mob_db:
                if mob_db[b.job] == name_or_id:
                    target_id = b.id
                    break

    if target_id > 0:
        mapserv.cmsg_player_change_act(target_id, 7)
    else:
        debuglog.warning("Being %s not found", name_or_id)


@must_have_arg
def me_action(_, arg):
    '''You can guess :-)'''
    general_chat("*{}*".format(arg))


@must_have_arg
def item_action(cmd, name_or_id):
    '''/use <item>
/equip <item>
item can be either item name or ID'''
    item_id = -10
    item_db = itemdb.item_names

    try:
        item_id = int(name_or_id)
    except ValueError:
        for id_, name in item_db.iteritems():
            if name == name_or_id:
                item_id = id_

    if item_id < 0:
        debuglog.warning("Unknown item: %s", name_or_id)
        return

    index = get_item_index(item_id)
    if index > 0:
        if cmd == 'use':
            mapserv.cmsg_player_inventory_use(index, item_id)
        elif cmd == 'equip':
            mapserv.cmsg_player_equip(index)
    else:
        debuglog.error("You don't have %s", name_or_id)


def show_inventory(cmd, _):
    '''Show inventory'''
    inv = {}
    for itemId, amount in mapserv.player_inventory.values():
        inv[itemId] = inv.setdefault(itemId, 0) + amount

    s = []
    for itemId, amount in inv.items():
        if amount > 1:
            s.append('{} [{}]'.format(amount, itemdb.item_name(itemId)))
        else:
            s.append('[{}]'.format(itemdb.item_name(itemId)))

    debuglog.info(', '.join(s))


def show_zeny(cmd, _):
    '''Show player money'''
    debuglog.info('You have {} GP'.format(mapserv.player_money))


def print_beings(cmd, btype):
    '''Show nearby beings
/beings -- show all beings
/beings player|npc|portal --show only given being type'''
    for being in mapserv.beings_cache.itervalues():
        if btype and being.type != btype:
            continue
        debuglog.info("id: %d | type: %s | pos: (%d, %d) | name: %s",
                      being.id, being.type, being.x, being.y, being.name)


def player_position(cmd, _):
    '''Show player position'''
    pp = mapserv.player_pos
    debuglog.info("Map: %s, coor: %d, %d", pp['map'], pp['x'], pp['y'])


def print_help(_, hcmd):
    '''Show help
/help -- show all commands
/help CMD  -- show help on CMD'''
    s = ' '.join(commands.keys())
    if hcmd in commands:
        docstring = commands[hcmd].__doc__
        if docstring:
            debuglog.info(docstring)
        else:
            debuglog.info('No help available for command /{}'.format(hcmd))
    else:
        debuglog.info("[help] commands: %s", s)


def command_not_found(cmd):
    debuglog.warning("[warning] command not found: %s. Try /help.", cmd)


def parse_player_name(line):
    line = line.lstrip()
    if len(line) < 2:
        return "", ""
    if line[0] == '"':
        end = line[1:].find('"')
        if end < 0:
            return line[1:], ""
        else:
            return line[1:end + 1], line[end + 3:]
    else:
        end = line.find(" ")
        if end < 0:
            return line, ""
        else:
            return line[:end], line[end + 1:]


commands = {
    "w"               : send_whisper_internal,
    "whisper"         : send_whisper_internal,
    "p"               : send_party_message_internal,
    "party"           : send_party_message_internal,
    "e"               : show_emote,
    "emote"           : show_emote,
    "dir"             : set_direction,
    "direction"       : set_direction,
    "turn"            : set_direction,
    "sit"             : sit_or_stand,
    "stand"           : sit_or_stand,
    "goto"            : set_destination,
    "nav"             : set_destination,
    "dest"            : set_destination,
    "me"              : me_action,
    "use"             : item_action,
    "equip"           : item_action,
    "attack"          : attack,
    "beings"          : print_beings,
    "inv"             : show_inventory,
    "zeny"            : show_zeny,
    "where"           : player_position,
    "help"            : print_help,
}


def process_line(line):
    if line == "":
        return

    elif line[0] == "/":
        end = line.find(" ")
        if end < 0:
            cmd = line[1:]
            arg = ""
        else:
            cmd = line[1:end]
            arg = line[end + 1:]

        if cmd in commands:
            func = commands[cmd]
            func(cmd, arg)
        else:
            command_not_found(cmd)

    else:
        general_chat(line)
