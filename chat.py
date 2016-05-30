import time
from collections import deque
import net.mapserv as mapserv
from loggers import debuglog
from utils import extends
from textutils import preprocess as pp
from textutils import (simplify_links, remove_formatting,
                       replace_emotes)
pp_actions = (simplify_links, remove_formatting, replace_emotes)

sent_whispers = deque()


def send_whisper(nick, message):
    ts = time.time()
    sent_whispers.append((nick, message, ts))
    mapserv.cmsg_chat_whisper(nick, message)


@extends('smsg_whisper_response')
def send_whisper_result(data):
    now = time.time()
    while True:
        try:
            nick, msg, ts = sent_whispers.popleft()
        except IndexError:
            return
        if now - ts < 1.0:
            break

    if data.code == 0:
        m = "[-> {}] {}".format(nick, pp(msg, pp_actions))
        debuglog.info(m)
    else:
        debuglog.warning("[error] {} is offline.".format(nick))


@extends('smsg_being_chat')
def being_chat(data):
    message = pp(data.message, pp_actions)
    debuglog.info(message)


@extends('smsg_player_chat')
def player_chat(data):
    message = pp(data.message, pp_actions)
    debuglog.info(message)


@extends('smsg_whisper')
def got_whisper(data):
    nick, message = data.nick, data.message
    message = pp(message, pp_actions)
    m = "[{} ->] {}".format(nick, message)
    debuglog.info(m)


@extends('smsg_party_chat')
def party_chat(data):
    nick = mapserv.party_members.get(data.id, str(data.id))
    message = pp(data.message, pp_actions)
    m = "[Party] {} : {}".format(nick, message)
    debuglog.info(m)


@extends('smsg_gm_chat')
def gm_chat(data):
    m = "[GM] {}".format(data.message)
    debuglog.info(m)
