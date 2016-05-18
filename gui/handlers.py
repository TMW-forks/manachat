
import net.mapserv as mapserv
from loggers import debuglog
from utils import extends


__all__ = ['app']


map_name = ""
app = None


@extends('smsg_whisper_response')
def send_whisper_result(data):
    if data.code == 0:
        last_nick = mapserv.last_whisper['to']
        app.root.chat_input.text = '/w "{}" '.format(last_nick)
        app.root.chat_input.focus = True


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
