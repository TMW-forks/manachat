
import net.mapserv as mapserv
from utils import extends
import cui
import textutils
from loggers import debuglog


__all__ = []


@extends('smsg_whisper_response')
def send_whisper_result(data):
    if data.code == 0:
        last_nick = mapserv.last_whisper['to']
        cui.input_win.clear()
        cui.input_win.addstr('/w "{}" '.format(last_nick))
        cui.input_win.refresh()


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
