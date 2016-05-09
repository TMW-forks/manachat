
import net.mapserv as mapserv
from loggers import debuglog
import commands
from utils import extends


__all__ = ['app']


map_name = ""
app = None


@extends('smsg_being_chat')
def being_chat(data):
    debuglog.info(data.message)


@extends('smsg_player_chat')
def player_chat(data):
    debuglog.info(data.message)


@extends('smsg_whisper')
def got_whisper(data):
    nick, message = data.nick, data.message
    m = "[{} ->] {}".format(nick, message)
    debuglog.info(m)


@extends('smsg_whisper_response')
def send_whisper_result(data):
    last_nick = mapserv.last_whisper['to']
    if data.code == 0:
        last_msg = mapserv.last_whisper['msg']
        m = "[-> {}] {}".format(last_nick, last_msg)
        debuglog.info(m)
        app.root.chat_input.text = '/w "{}" '.format(last_nick)
        app.root.chat_input.focus = True

    else:
        debuglog.warning("[error] {} is offline.".format(last_msg))


@extends('smsg_party_chat')
def party_chat(data):
    nick = mapserv.party_members.get(data.id, str(data.id))
    msg = data.message
    m = "[Party] {} : {}".format(nick, msg)
    debuglog.info(m)


@extends('smsg_gm_chat')
def gm_chat(data):
    m = "[GM] {}".format(data.message)
    debuglog.info(m)


@extends('smsg_player_warp')
def player_warp(data):
    mapserv.cmsg_map_loaded()
    m = "[warp] {} ({},{})".format(data.map, data.x, data.y)
    debuglog.info(m)


@extends('smsg_char_map_info')
def char_map_info(data):
    global map_name
    map_name = data.map_name


@extends('smsg_map_login_success')
def map_login_success(data):
    m = "[map] {} ({},{})".format(map_name, data.coor.x, data.coor.y)
    debuglog.info(m)
    mapserv.server.raw = True
    mapserv.cmsg_map_loaded()


@extends('smsg_connection_problem')
def connection_problem(data):
    error_codes = {
        2 : "Account already in use"
    }
    msg = error_codes.get(data.code, str(data.code))
    debuglog.error('Connection problem: %s', msg)
