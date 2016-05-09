
import net.mapserv as mapserv
from utils import extends
import commands
import cui
import textutils
from loggers import debuglog


__all__ = []


@extends('smsg_being_chat')
def being_chat(data):
    message = textutils.preprocess(data.message)
    debuglog.info(message)


@extends('smsg_player_chat')
def player_chat(data):
    message = textutils.preprocess(data.message)
    debuglog.info(message)


@extends('smsg_whisper')
def got_whisper(data):
    nick, message = data.nick, data.message
    message = textutils.preprocess(message)
    m = "[{} ->] {}".format(nick, message)
    debuglog.info(m)


@extends('smsg_whisper_response')
def send_whisper_result(data):
    last_nick = mapserv.last_whisper['to']
    if data.code == 0:
        message = textutils.preprocess(mapserv.last_whisper['msg'])
        m = "[-> {}] {}".format(last_nick, message)
        debuglog.info(m)
        cui.input_win.clear()
        cui.input_win.addstr('/w "{}" '.format(last_nick))
        cui.input_win.refresh()
    else:
        debuglog.info("[error] {} is offline.".format(last_nick))


@extends('smsg_party_chat')
def party_chat(data):
    nick = mapserv.party_members.get(data.id, str(data.id))
    message = textutils.preprocess(data.message)
    m = "[Party] {} : {}".format(nick, message)
    debuglog.info(m)


@extends('smsg_player_warp')
def player_warp(data):
    mapserv.cmsg_map_loaded()
    m = "[warp] {} ({},{})".format(data.map, data.x, data.y)
    debuglog.info(m)


@extends('smsg_map_login_success')
def map_login_success(data):
    mapserv.cmsg_map_loaded()


@extends('smsg_connection_problem')
def connection_problem(data):
    error_codes = {
        2 : "Account already in use"
    }
    msg = error_codes.get(data.code, str(data.code))
    debuglog.error('Connection problem: %s', msg)
