
import net.mapserv as mapserv
from loggers import debuglog
from gui.tmxmap import BeingWidget
import commands
import monsterdb
from utils import extends


__all__ = ['app']


map_name = ""
app = None


@extends('smsg_being_chat')
def being_chat(data):
    id_, message = data.id, data.message
    nick = mapserv.beings_cache[id_].name
    m = "{} : {}".format(nick, message)
    debuglog.info(m)


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
    if data.code == 0:
        m = "[-> {}] {}".format(commands.whisper_to, commands.whisper_msg)
        debuglog.info(m)
        app.root.chat_input.text = '/w "{}" '.format(commands.whisper_to)
        app.root.chat_input.focus = True

    else:
        debuglog.warning("[error] {} is offline.".format(
            commands.whisper_to))


@extends('smsg_party_chat')
def party_chat(data):
    nick = mapserv.party_members.get(data.id, str(data.id))
    msg = data.message
    m = "[Party] {} : {}".format(nick, msg)
    debuglog.info(m)


@extends('smsg_player_warp')
def player_warp(data):
    mw = app.root.map_w

    for b in mw.beings:
        mw.remove_widget(mw.beings[b])
    mw.beings.clear()

    mw.load_map(data.map)
    app.root.player.anim.stop(app.root.player)
    app.root.player.pos = mw.from_game_coords((data.x, data.y))

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
    app.root.map_w.load_map(map_name)
    app.root.player.pos = app.root.map_w.from_game_coords((data.coor.x,
                                                           data.coor.y))
    app.root.player.name = mapserv.server.char_name
    mapserv.cmsg_map_loaded()


@extends('smsg_connection_problem')
def connection_problem(data):
    error_codes = {
        2 : "Account already in use"
    }
    msg = error_codes.get(data.code, str(data.code))
    debuglog.error('Connection problem: %s', msg)


@extends('smsg_being_visible')
def being_visible(data):
    if mapserv.beings_cache[data.id].type not in ("monster", "player"):
        return

    mw = app.root.map_w
    if data.id in mw.beings:
        return

    npos = mw.from_game_coords((data.coor.x, data.coor.y))
    name = monsterdb.monster_db.get(data.job, str(data.job))
    mw.beings[data.id] = BeingWidget(size_hint=(None, None),
                                     size=(16, 20),
                                     name=name,
                                     pos=npos)
    mw.add_widget(mw.beings[data.id])


@extends('smsg_being_move')
def being_move(data):
    mw = app.root.map_w

    if data.id not in mw.beings:
        npos = mw.from_game_coords((data.coor_pair.src_x,
                                    data.coor_pair.src_y))
        name = monsterdb.monster_db.get(data.job, str(data.job))
        mw.beings[data.id] = BeingWidget(size_hint=(None, None),
                                         size=(16, 20),
                                         name=name,
                                         pos=npos)
        mw.add_widget(mw.beings[data.id])

    try:
        speed = data.speed
    except AttributeError:
        speed = mapserv.beings_cache[data.id].speed

    mw.move_being(mw.beings[data.id], data.coor_pair.dst_x,
                  data.coor_pair.dst_y, speed)


@extends('smsg_player_update')
def player_update(data):
    mw = app.root.map_w
    npos = mw.from_game_coords((data.coor.x, data.coor.y))
    name = mapserv.beings_cache[data.id].name
    mw.beings[data.id] = BeingWidget(size_hint=(None, None),
                                     size=(16, 20),
                                     name=name,
                                     pos=npos)
    mw.add_widget(mw.beings[data.id])


@extends('smsg_player_move')
def player_move(data):
    mw = app.root.map_w

    if data.id not in mw.beings:
        npos = mw.from_game_coords((data.coor_pair.src_x,
                                    data.coor_pair.src_y))
        mw.beings[data.id] = BeingWidget(size_hint=(None, None),
                                         size=(16, 20),
                                         name=str(data.id),
                                         pos=npos)
        mw.add_widget(mw.beings[data.id])

    try:
        speed = data.speed
    except AttributeError:
        speed = mapserv.beings_cache[data.id].speed

    mw.move_being(mw.beings[data.id], data.coor_pair.dst_x,
                  data.coor_pair.dst_y, speed)


@extends('smsg_being_remove')
def being_remove(data):
    mw = app.root.map_w

    if data.id in mw.beings:
        mw.remove_widget(mw.beings[data.id])
        del mw.beings[data.id]


@extends('smsg_being_name_response')
def being_name_response(data):
    mw = app.root.map_w

    if data.id in mw.beings:
        mw.beings[data.id].name = data.name


@extends('smsg_walk_response')
def player_walk_response(data):
    mw = app.root.map_w
    mw.move_being(mw.player, data.coor_pair.dst_x,
                  data.coor_pair.dst_y)


@extends('smsg_being_action')
def being_action(data):
    if data.type in (0, 10):
        app.root.map_w.current_attacks[data.src_id, data.dst_id] = data.damage
