# TMWA <> IRC bridge

import sys
import irc.bot
import thread
import logging
import cPickle as pickle
import time
import re
from logicmanager import logic_manager
from utils import extends
from collections import deque
from textutils import (preprocess, simplify_links, manaplus_to_mIRC, remove_formatting, replace_emotes)
import net
from net.onlineusers import OnlineUsers
import net.mapserv as mapserv
import net.charserv as charserv

__all__ = [ 'PLUGIN', 'init' ]


PLUGIN = {
    'name': 'irclink',
    'requires': (),
    'blocks': ('chatbot', 'manaboy', 'autofollow'),
}

irc_bridge = None # irc interface
whisper_players = set() # players to send whispers to
database = {"game": {}, "irc": {}} # database specific to the irc bridge (ignores, ...)
send_queue = deque() # whispers waiting to be sent
is_sending = 0 # is the queue being processed right now?
tmwa_is_ready = False # is the tmwa interface connected and ready to use?
config = ''
irclog = logging.getLogger('ManaChat.IRC')
ircbot_commands = {}
is_quiet = False # if True, don't send notifications
follow_player = '' # should the bot follow player X ?
suicide = False # did the bot commit seppuku?
online_users = '' # online list thread

class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, realname, server, port, password, areachannel):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, realname)
        self.channel = channel
        self.areachannel = areachannel
        self.is_dead = 0
        self.tmwa_last_died = 0

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        global whisper_players, database, is_quiet
        self.connection.buffer_class.encoding = 'utf-8'
        self.connection.buffer_class.errors = 'replace'
        c.join(self.channel)
        if self.is_dead == 1 and is_quiet is not True:
            self.connection.privmsg(self.channel, "** The IRC link is back.".decode('utf-8', 'replace'))
            for player in whisper_players:
                send_queue.append((player, "=> IRC link is back."))
        if (len(self.areachannel) > 1):
            c.join(self.areachannel)
            if self.is_dead == 1 and is_quiet is not True:
                self.connection.privmsg(self.areachannel, "** The IRC link is back.".decode('utf-8', 'replace'))
        self.is_dead = 0
        database["irc_last_connected"] = int(time.time())

    def on_disconnect(self, *_):
        global send_queue, whisper_players, suicide
        if suicide is True:
            return
        self.is_dead = 1
        for player in whisper_players:
            send_queue.append((player, "=> IRC link died. Trying to reconnect..."))
        self.connection.reconnect()

    def whisper_to_irc(self, nick, msg):
        if self.connection.connected == 0:
            return
        self.connection.privmsg(self.channel, "[ {} ] {}".format(nick, msg).decode('utf-8', 'replace'))

    def area_to_irc(self, nick, msg):
        if self.connection.connected == 0:
            return
        if (len(self.areachannel) < 1):
            return
        self.connection.privmsg(self.areachannel, "[ {} ] {}".format(nick, msg).decode('utf-8', 'replace'))

    def on_pubmsg(self, c, e, action=False):
        global database, whisper_players
        msg = e.arguments[0].encode('utf-8', 'replace')
        if action is True:
            msg = "*{}*".format(msg)
        nick = e.source.nick
        if nick in database["irc"]:
            if 2 in database["irc"][nick]:
                return # player is ignored
        if e.target == self.channel:
            for player in whisper_players:
                send_queue.append((player, "[IRC] {}: {}".format(nick, msg)))
            send_next(0) # don't wait
        elif e.target == self.areachannel:
            mapserv.cmsg_chat_message("{}: {}".format(nick, msg))

    def on_action(self, c, e):
        self.on_pubmsg(c, e, True)

    def on_privmsg(self, c, e):
        c.notice(e.source.nick, "I do not have IRC commands support yet. Please use in-game commands.")

def send_next(ts, force=False):
    global is_sending, send_queue, tmwa_is_ready, irclog
    if len(send_queue) < 1 or tmwa_is_ready != 1:
        return
    if is_sending != 0 and (int(time.time()) - is_sending) < 8 and force != True:
        return
    is_sending = int(time.time())
    player, msg = send_queue.popleft()
    if (len(player) < 1) or (len(msg) < 1):
        if (len(send_queue) < 1):
            is_sending = 0 # queue is empty, so unblock
        else:
            send_next(0, True)
    else:
        mapserv.cmsg_chat_whisper(player, msg)

@extends('smsg_whisper_response')
def send_whisper_result(data):
    global is_sending, send_queue, whisper_players
    if is_sending == 0:
        return
    last_nick = mapserv.last_whisper['to']
    if data.code != 0:
        whisper_players.discard(last_nick)

    if (len(send_queue) < 1):
        is_sending = 0 # queue is empty, so unblock
    else:
        send_next(0, True) # process next whisper in queue

@extends('smsg_map_login_success')
def map_login_success(data):
    global tmwa_is_ready, whisper_players, is_sending, database, irc_bridge, is_quiet
    if tmwa_is_ready == 2:
        is_sending = 0
        if is_quiet is not True:
            if irc_bridge.connection.connected:
                irc_bridge.connection.notice(irc_bridge.channel, "** TMWA link is back.".decode('utf-8', 'replace'))
                if len(irc_bridge.areachannel) > 1:
                    irc_bridge.connection.notice(irc_bridge.areachannel, "** TMWA link is back.".decode('utf-8', 'replace'))
            for player in whisper_players:
                send_queue.append((player, "=> TMWA link is back."))
    tmwa_is_ready = 1
    database["game_last_connected"] = int(time.time())

def seppuku():
    global suicide, irc_bridge, online_users, irclog
    irclog.warning("Committing seppuku...")
    suicide = True
    irc_bridge.die()
    online_users.stop()
    mapserv.cleanup()
    sys.exit(0)

@extends('on_close')
def on_close():
    global tmwa_is_ready, irc_bridge, config, is_quiet, suicide
    if suicide is True:
        irclog.warning("I'm dead already")
        return
    if tmwa_is_ready == 2:
        if irc_bridge.connection.connected:
            irc_bridge.connection.notice(irc_bridge.channel, "** TMWA server unreachable. Committing seppuku...".decode('utf-8', 'replace'))
            if len(irc_bridge.areachannel) > 1:
                irc_bridge.connection.notice(irc_bridge.areachannel, "** TMWA server unreachable. Committing seppuku...".decode('utf-8', 'replace'))
        seppuku()
        return

    tmwa_is_ready = 2
    if irc_bridge.connection.connected and int(time.time()) - irc_bridge.tmwa_last_died > 30 and int(time.time()) - database["last_started"] > 30:
        irc_bridge.tmwa_last_died = int(time.time())
        if is_quiet is not True:
            irc_bridge.connection.notice(irc_bridge.channel, "** TMWA link died. Trying to reconnect in 5s...".decode('utf-8', 'replace'))
            if len(irc_bridge.areachannel) > 1:
                irc_bridge.connection.notice(irc_bridge.areachannel, "** TMWA link died. Trying to reconnect in 5s...".decode('utf-8', 'replace'))
    time.sleep(5)
    net.login(host=config.get('Server', 'host'),
              port=config.getint('Server', 'port'),
              username=config.get('Player', 'username'),
              password=config.get('Player', 'password'),
              charname=config.get('Player', 'charname'))

@extends('smsg_being_chat')
def being_chat(data):
    global irc_bridge, config
    s = data.message.split(" : ", 1)
    nick, message = s[0].strip(), preprocess(s[1].strip(' \t\n\r'))
    if (nick == config.get('Player', 'charname') and ": " in message) or (nick == "Server"):
        return

    if message.startswith('\302\202'):
        # manaplus special commands # FIXME: handle talkpet https://git.io/vrGyL
        return
    if len(message) < 1:
        return
    irc_bridge.area_to_irc(nick, message)

@extends('smsg_player_chat')
def player_chat(data):
    being_chat(data)

@extends('smsg_whisper')
def got_whisper(data):
    global database, send_queue, whisper_players, irc_bridge, ircbot_commands
    nick, message = data.nick, data.message.strip(' \t\n\r')

    if message.startswith('\302\202'):
        # manaplus special commands # FIXME: handle talkpet https://git.io/vrGyL
        # actually, are these ever sent via whisper?
        return
    if len(message) < 1:
        return

    if (message.startswith("*AFK*")):
        return

    if (message.startswith("!")):
        for regex, action in ircbot_commands.iteritems():
            match = re.match(regex, message)
            if match:
                if action[1] is True:
                    if nick not in database["game"]:
                        send_queue.append((nick, "=> I do not recognize you as an admin."))
                        return
                    if 1 not in database["game"][nick]:
                        send_queue.append((nick, "=> I do not recognize you as an admin."))
                        return
                action[0](nick, message, match)
                return
        send_queue.append((nick, "=> Command not found. Type !list to see available commands."))
        return

    message = preprocess(message) # only pre-process if not a command

    if nick not in whisper_players:
        whisper_players.add(nick)
        if nick in database["game"]:
            if 0 in database["game"][nick]:
                send_queue.append((nick, "=> Welcome back. You have been automatically added to the send queue. Type !help for info."))
        else:
            send_queue.append((nick, "=> You have been added to the send queue for this session only. You might want to !register. Type !help for info."))

    if nick in database["game"]:
        if 2 in database["game"][nick]:
            send_queue.append((nick, "=> Your message could not be sent. You are in the ignore list."))
            return

    for player in whisper_players:
        if nick != player:
            send_queue.append((player, "{}: {}".format(nick, data.message)))

    send_next(0) # don't wait

    irc_bridge.whisper_to_irc(nick, message)

def online_list_hook(users, u2):
    global database, send_queue, config, is_quiet
    for pg in database["game"].keys():
        if len(database["game"][pg]) < 1:
            del database["game"][pg]
    for pi in database["irc"].keys():
        if len(database["irc"][pi]) < 1:
            del database["irc"][pi]

    database["last_save"] = int(time.time())

    pickle_link = open(config.get('IRC', 'database'), "wb")
    pickle.dump(database, pickle_link, -1) # dump db to file
    pickle_link.close()

    for player in users:
        if player in database["game"]:
            if player not in whisper_players and 0 in database["game"][player]:
                whisper_players.add(player)
                #if is_quiet is not True:
                #    send_queue.append((player, "=> Welcome back. You have been automatically added to the send queue. Type !help for info."))

    #if len(users) > 0:
    #    for player in whisper_players:
    #        if player not in users:
    #            # send notice on irc (player offline)
    #            # send whisper to all (player offline)

@extends('smsg_gm_chat')
def gm_chat(data):
    global irc_bridge, is_quiet
    if is_quiet is True:
        return
    irc_bridge.area_to_irc("GM", preprocess("##1{}".format(data.message), (simplify_links,
                                                                            manaplus_to_mIRC,
                                                                            remove_formatting,
                                                                            replace_emotes)))

@extends('smsg_player_move')
def player_move(data):
    global follow_player
    if follow_player:
        b = mapserv.beings_cache[data.id]
        if b.name == follow_player:
            mapserv.cmsg_player_change_dest(data.coor_pair.dst_x,
                                            data.coor_pair.dst_y)

@extends('smsg_being_remove')
def bot_dies(data):
    if data.id == charserv.server.account:
        mapserv.cmsg_player_emote(7) # angel
        #mapserv.cmsg_player_respawn()

def cmd_help(nick, message, match):
    global send_queue, irc_bridge
    send_queue.append((nick, "=> This is an IRC bot. If you register, you will be able to send and receive messages to/from the {} channel on IRC.".format(irc_bridge.channel)))
    if (len(irc_bridge.areachannel) > 1):
        send_queue.append((nick, "=> You can also join the {} channel on IRC to interact with players near the bot.".format(irc_bridge.areachannel)))
    send_queue.append((nick, "=>"))
    send_queue.append((nick, "=> -- Quick Commands --"))
    send_queue.append((nick, "=> !register  =>  adds you to the send queue, and remembers it"))
    send_queue.append((nick, "=> !remove  =>  removes you from the send queue"))
    send_queue.append((nick, "=> !commands  =>  lists all commands"))

def cmd_register(nick, message, match):
    global whisper_players, send_queue, database
    whisper_players.add(nick)
    if nick in database["game"]:
        if 0 in database["game"][nick]:
            send_queue.append((nick, "=> You are already registered."))
            return
        else:
            database["game"][nick].append(0)
    else:
        database["game"][nick] = [0]
    send_queue.append((nick, "=> You are now registered. Type !remove to unregister."))

def cmd_remove(nick, message, match):
    global whisper_players, send_queue, database
    whisper_players.discard(nick)
    if nick in database["game"]:
        if 0 in database["game"][nick]:
            database["game"][nick].remove(0)
            send_queue.append((nick, "=> You are now unregistered. You must explicitly send !register if you wish to re-register in the future."))
    send_queue.append((nick, "=> You are now removed from the send queue. You may be temporarily added again if you talk through the bot while unregistered."))

def cmd_list(nick, message, match):
    global ircbot_commands, send_queue, database
    c = []
    for cmd in ircbot_commands:
        if ircbot_commands[cmd][1] is True:
            if nick not in database["game"]:
                continue
            if 1 not in database["game"][nick]:
                continue
        if cmd.startswith('!('):
            c.append(cmd[2:cmd.index('|')])
        elif cmd.startswith('!'):
            c.append(cmd[1:cmd.index('(')])
    c.sort()
    send_queue.append((nick, "=> Commands: {}".format(', '.join(c))))

def cmd_talk(nick, message, match):
    global send_queue
    msg = match.group("msg")
    if msg is not None:
        mapserv.cmsg_chat_message(msg)
        send_queue.append((nick, "=> Done."))
    else:
        send_queue.append((nick, "=> Can't send an empty message."))

def cmd_whisper(nick, message, match):
    global send_queue
    n, msg = match.group("player"), match.group("msg")
    if n is not None and msg is not None:
        send_queue.append((n, msg))
        send_queue.append((nick, "=> Message sent to `{}`".format(n)))
    else:
        send_queue.append((nick, "=> Invalid syntax."))

def cmd_goto(nick, message, match):
    global follow_player, send_queue
    try:
        x = int(match.group("x"))
        y = int(match.group("y"))
    except ValueError:
        send_queue.append((nick, "=> Invalid location."))
        return
    follow_player = ''
    mapserv.cmsg_player_change_dest(x, y)
    send_queue.append((nick, "=> Walking to {},{}...".format(x,y)))

def cmd_turn(nick, message, match):
    global send_queue
    if match.group("dir") is not None:
        d = {"down": 1, "left": 2, "up": 4, "right": 8}
        dir_num = d.get(match.group("dir").lower(), -1)
        if dir_num > 0:
            mapserv.cmsg_player_change_dir(dir_num)
        send_queue.append((nick, "=> Done."))
    else:
        send_queue.append((nick, "=> Invalid direction."))

def cmd_sit(nick, message, match):
    global follow_player, send_queue
    follow_player = ''
    mapserv.cmsg_player_change_act(0, 2)
    send_queue.append((nick, "=> Done."))

def cmd_stand(nick, message, match):
    global follow_player, send_queue
    follow_player = ''
    mapserv.cmsg_player_change_act(0, 3)
    send_queue.append((nick, "=> Done."))

def cmd_follow(nick, message, match):
    global follow_player, send_queue
    n = nick
    if match.group("player") is not None:
        n = match.group("player")
    if follow_player == n or n.lower() == "unfollow":
        follow_player = ''
        send_queue.append((nick, "=> I am no longer following anyone."))
    else:
        follow_player = n
        send_queue.append((nick, "=> I am now following {}.".format(n)))

def cmd_seppuku(nick, message, match):
    global irclog, send_queue
    if match.group("mode") is None:
        irclog.warning("Suicide signal sent via whisper by {}".format(nick))
        send_queue.append((nick, "*dies*"))
        send_next(0)
    seppuku()

def cmd_ping(nick, message, match):
    global send_queue
    send_queue.append((nick, "=> Pong: {}".format(int(time.time()))))
    send_next(0) # don't wait when it's ping

ircbot_commands = {
    '!(help|info)(?: .*)?$' : [cmd_help, False],
    '!(list|commands)(?: .*)?$' : [cmd_list, False],
    '!(ping|time)(?: .*)?$' : [cmd_ping, False],
    '!(register|add)(?: .*)?$' : [cmd_register, False],
    '!(remove|unregister)(?: .*)?$' : [cmd_remove, False],
    '!(say|talk)(?: (?P<msg>.+)?)?$' : [cmd_talk, True],
    '!(whisper|w)(?: "(?P<player>[^"]+)"(?: (?P<msg>.+)?)?| .*)?$' : [cmd_whisper, True],
    '!(goto|walk)(?: (?P<x>\d+)[ ,](?P<y>\d+)| .*)?$' : [cmd_goto, True],
    '!turn(?: (?P<dir>(?i)up|down|left|right)| .*)?$' : [cmd_turn, True],
    '!sit(?: .*)?$' : [cmd_sit, True],
    '!stand(?: .*)?$' : [cmd_stand, True],
    '!follow(?: (?P<player>.+)| .*)?$' : [cmd_follow, True],
    '!(die|suicide)(?: (?P<mode>(?i)force)| .*)?$' : [cmd_seppuku, True],
}

def init(conf):
    global irc_bridge, database, config, irclog, online_users
    config = conf

    irc_bridge = IRCBot(config.get('IRC', 'channel'),
                        config.get('IRC', 'username'),
                        config.get('IRC', 'realname'),
                        config.get('IRC', 'host'),
                        config.getint('IRC', 'port'),
                        config.get('IRC', 'password'),
                        config.get('IRC', 'areachannel'))

    pickle_link = open(config.get('IRC', 'database'), "rb")
    database = pickle.load(pickle_link)
    pickle_link.close()

    # initialize new db (db version 2)
    if "v" not in database:
        database = {"game": {}, "irc": {}, "created": int(time.time()), "v": 2}

    # update the db timestamp
    database["last_started"] = int(time.time())

    # start the irc bridge in a new thread
    thread.start_new_thread(irc_bridge.start, ())

    # add our hooks to logic manager
    logic_manager.add_logic(send_next)

    # start the online list thread, and add a hook
    online_users = OnlineUsers(config.get('Other', 'online_txt_url'), 10, online_list_hook)
    online_users.start()
