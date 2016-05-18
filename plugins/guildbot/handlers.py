from chat import send_whisper
from utils import extends
from commands import parse_player_name


online_users = None
db = None
max_msg_len = 200
pending_invitations = {}


def ignore():
    pass


def listonline(nick, _):
    curr_msg = ''
    online = online_users.online_users

    for prow in db.all_players_same_guild(nick):
        p = prow[0]
        if p in online:
            if len(curr_msg + ', ' + p) > max_msg_len:
                send_whisper(nick, curr_msg)
                curr_msg = p
            else:
                curr_msg = curr_msg + ', ' + p

    send_whisper(nick, curr_msg)


def leave(nick, _):
    info = db.player_info(nick)
    broadcast(nick, '"{}" left the guild'.format(nick), True)
    db.guild_remove_player(nick)
    send_whisper(nick, 'You left guild {}'.format(info[1]))


def showinfo(nick, _):
    db.player_set_showinfo(nick, True)
    send_whisper(nick, "Information messages are visible")


def hideinfo(nick, _):
    db.player_set_showinfo(nick, False)
    send_whisper(nick, "Information messages are hidden")


def status(nick, _):
    _, guild, access = db.player_info(nick)
    send_whisper(nick, 'Player:{}, Guild:{}, Access:{}'.format(
        nick, guild, access))


# FIXME: not finished
def invite(nick, player):
    if not player:
        send_whisper(nick, "Usage: !invite Player")
        return

    pinfo = db.player_info(player)
    if pinfo and pinfo[0]:
        send_whisper(nick, '"{}" is already a member of guild "{}"'.format(
            player, pinfo[1]))
        return

    online = online_users.online_users
    if player not in online:
        send_whisper(nick, '"{}" is not online'.format(player))
        return

    _, guild, _ = db.player_info(nick)
    invite_msg = ('You have been invited to the "{}" guild chat. '
                  'If you would like to accept this invitation '
                  'please reply "yes" and if not then "no"').format(guild)
    send_whisper(player, invite_msg)
    # FIXME: what if player is offline? online_list can be outdated
    pending_invitations[player] = guild


def remove(nick, player):
    if not player:
        send_whisper(nick, "Usage: !remove Player")
        return

    pinfo = db.player_info(player)
    if not pinfo:
        send_whisper(nick, '{} is not in any guild'.format(player))
        return

    gid, _, _ = db.player_info(nick)
    if gid != pinfo[0]:
        send_whisper(nick, '{} is not in your guild'.format(player))
        return

    broadcast(player, '{} was removed from your guild'.format(player), True)
    db.guild_remove_player(player)
    send_whisper(nick, 'You were removed from "{}" guild'.format(pinfo[1]))


def setmotd(nick, motd):
    guild = db.player_info(nick)[1]
    db.setmotd(guild, motd)
    broadcast(nick, 'MOTD: ' + motd)


def removemotd(nick, _):
    guild = db.player_info(nick)[1]
    db.setmotd(guild, '')
    broadcast(nick, 'MOTD removed')


def setaccess(nick, params):
    try:
        si = params.index(" ")
        lvl = int(params[:si])
        player = params[si + 1:]
        if len(player) < 4:
            raise ValueError
    except ValueError:
        send_whisper(nick, "Usage: !setaccess Level Player")
        return

    gid, guild_name, access = db.player_info(nick)
    gidp, _, accessp = db.player_info(player)

    if gid != gidp:
        send_whisper(nick, '{} is not in your guild "{}"'.format(
            player, guild_name))
        return

    if access <= accessp:
        send_whisper(nick, "You cannot set access level for {}".format(
            player))
        return

    db.player_set_access(player, lvl)
    send_whisper(nick, "Player: {}, access level: {}".format(
        player, lvl))


def disband(nick, _):
    _, guild, _ = db.player_info(nick)
    if db.guild_delete(guild):
        send_whisper(nick, 'Deleted guild "{}"'.format(guild))
    else:
        send_whisper(nick, 'Error deleting guild "{}"'.format(guild))


def addguild(nick, params):
    usage = 'Usage: !addguild Leader Guild (note: Leader can be quoted)'
    if not params:
        send_whisper(nick, usage)
        return

    leader, guild = parse_player_name(params)

    if len(leader) < 4 or len(guild) < 4:
        send_whisper(nick, usage)
        return

    if db.guild_create(guild):
        send_whisper(nick, 'Created guild "{}", leader is "{}"'.format(
            guild, leader))
    else:
        send_whisper(nick, "Error creating guild")


def removeguild(nick, guild_name):
    if not guild_name:
        send_whisper(nick, "Usage: !removeguild Guild")
        return

    if db.guild_delete(guild_name):
        send_whisper(nick, 'Deleted guild "{}"'.format(guild_name))
    else:
        send_whisper(nick, 'Guild not found: "{}"'.format(guild_name))


def globalmsg(nick, msg):
    if not msg:
        send_whisper(nick, "Usage: !global Message")
        return

    online = online_users.online_users
    for prow in db.all_players_any_guild():
        pname = prow[0]
        if pname in online:
            send_whisper(pname, msg)


def joinguild(nick, guild):
    if not guild:
        send_whisper(nick, "Usage: !joinguild Guild")
        return

    if db.player_join_guild(nick, guild, 20):
        send_whisper(nick, 'You joined guild "{}"'.format(guild))
    else:
        send_whisper(nick, 'Guild "{}" does not exist'.format(guild))


def showhelp(nick, _):
    access = db.player_get_access(nick)
    curr_line = ''

    for cmd, (lvl, _, hlp) in commands.iteritems():
        if access < lvl:
            continue

        if hlp[0] == '+':
            help_s = '!' + cmd + ' ' + hlp[1:]
        else:
            help_s = '!' + cmd + ' -- ' + hlp

        if len(curr_line + '; ' + help_s) > max_msg_len:
            send_whisper(nick, curr_line)
            curr_line = help_s
        else:
            curr_line = curr_line + '; ' + help_s

    if curr_line:
        send_whisper(nick, curr_line)


commands = {
    "help":        (-10, showhelp,    "show help"),
    "info":        (0,   status,      "display guild information"),
    "listonline":  (0,   listonline,  "list online players"),
    "leave":       (0,   leave,       "leave your guild"),
    "showinfo":    (0,   showinfo,    "verbose notifications"),
    "hideinfo":    (0,   hideinfo,    "quiet notifications"),
    "invite":      (5,   invite,      "+Player -- invite player to guild"),
    "remove":      (5,   remove,      "+Player -- remove player from guild"),
    "setmotd":     (5,   setmotd,     "+MOTD -- set MOTD"),
    "removemotd":  (5,   removemotd,  "remove MOTD"),
    "setaccess":   (10,  setaccess,   "+Level Player -- set access level"),
    "disband":     (10,  disband,     "disband your guild"),
    "addguild":    (20,  addguild,    "+Leader GuildName -- add guild"),
    "removeguild": (20,  removeguild, "+GuildName -- remove guild"),
    "global":      (20,  globalmsg,   "+Message -- global message"),
    "joinguild":   (20,  joinguild,   "+GuildName -- join a guild"),
}


def exec_command(nick, cmdline):
    end = cmdline.find(" ")
    if end < 0:
        cmd = cmdline[1:]
        arg = ""
    else:
        cmd = cmdline[1:end]
        arg = cmdline[end + 1:]

    if cmd in commands:
        lvl, func, _ = commands[cmd]
        access = db.player_get_access(nick)

        if access < lvl:
            send_whisper(nick, 'That command is fobidden for you!')
        else:
            func(nick, arg)

    else:
        send_whisper(nick, 'Command !{} not found. Try !help'.format(cmd))


def player_joining(player, guild):
    db.player_join_guild(player, guild)
    broadcast(player, '{} joined your guild'.format(player), True)


def broadcast(nick, msg, exclude_nick=False):
    """
    Broadcast message for all players that belong the same guild as nick.
    """
    n = 0
    for prec in db.all_players_same_guild(nick):
        if exclude_nick and prec[0] == nick:
            continue
        n += 1
        send_whisper(prec[0], '{} : {}'.format(nick, msg))

    if n == 0:
        send_whisper(nick, "You don't belong to any guild")


def online_list_update(curr, prev):
    for p in curr - prev:
        ginfo = db.player_info(p)
        if ginfo is not None:
            if ginfo[0] is not None:
                allp = set(db.all_players_same_guild(p))
                n = len(allp.intersection(curr))
                send_whisper(p,
                    'Welcome to {}! ({} Members are online)'.format(
                        ginfo[1], n))
                broadcast(p, '{} is now Online'.format(p), True)

    for p in prev - curr:
        broadcast(p, '{} is now Offline'.format(p), True)


@extends('smsg_whisper')
def got_whisper(data):
    nick, message = data.nick, data.message

    if len(message) < 1:
        return

    if message[0] == '!':
        exec_command(nick, message)
    else:
        if nick in pending_invitations:
            # TODO: inform message
            if message.lower() == 'yes':
                player_joining(nick, pending_invitations[nick])
            del pending_invitations[nick]

        else:
            broadcast(nick, message)


@extends('smsg_whisper_response')
def send_whisper_result(data):
    pass
