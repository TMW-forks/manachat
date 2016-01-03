
from kivy.app import App
import net.mapserv as mapserv
from gui.tmxmap import BeingWidget
import commands
import monsterdb
from utils import register_extension

_map_name = ""
_char_name = ""


def being_chat(data):
    id_, message = data.id, data.message
    nick = mapserv.beings_cache[id_].name
    m = "{} : {}".format(nick, message)
    app = App.get_running_app()
    app.root.messages_log.append_message(m)


def player_chat(data):
    message = data.message
    app = App.get_running_app()
    app.root.messages_log.append_message(message)


def got_whisper(data):
    nick, message = data.nick, data.message
    m = "[{} ->] {}".format(nick, message)
    app = App.get_running_app()
    app.root.messages_log.append_message(m)


def send_whisper_result(data):
    app = App.get_running_app()

    if data.code == 0:
        m = "[-> {}] {}".format(commands.whisper_to, commands.whisper_msg)
        app.root.messages_log.append_message(m)
        app.root.chat_input.text = '/w "{}" '.format(commands.whisper_to)
        app.root.chat_input.focus = True

    else:
        app.root.messages_log.append_message("[error] {} is offline.".format(
            commands.whisper_to))


def party_chat(data):
    nick = mapserv.party_members.get(data.id, str(data.id))
    msg = data.message
    m = "[Party] {} : {}".format(nick, msg)
    app = App.get_running_app()
    app.root.messages_log.append_message(m)


def player_warp(data):
    mapserv.cmsg_map_loaded()
    m = "[warp] {} ({},{})".format(data.map, data.x, data.y)
    app = App.get_running_app()
    app.root.messages_log.append_message(m)


def char_map_info(data):
    global _map_name
    _map_name = data.map_name


def map_login_success(data):
    app = App.get_running_app()
    m = "[map] {} ({},{})".format(_map_name, data.coor.x, data.coor.y)
    app.root.messages_log.append_message(m)
    app.root.map_w.load_map("client-data/maps/{}.tmx".format(_map_name))
    app.root.player.pos = app.root.map_w.from_game_coords((data.coor.x,
                                                           data.coor.y))
    app.root.player.name = mapserv.server.char_name
    # app.root.map_scroller.scroll_x = app.root.player.x / app.root.map_w.width
    # app.root.map_scroller.scroll_y = app.root.player.y / app.root.map_w.height


def being_visible(data):
    if mapserv.beings_cache[data.id].type not in ("monster", "player"):
        return

    app = App.get_running_app()
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


def being_move(data):
    app = App.get_running_app()
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

    mw.move_being(mw.beings[data.id], data.coor_pair.dst_x,
                  data.coor_pair.dst_y)


def player_update(data):
    app = App.get_running_app()
    mw = app.root.map_w
    npos = mw.from_game_coords((data.coor.x, data.coor.y))
    mw.beings[data.id] = BeingWidget(size_hint=(None, None),
                                     size=(16, 20),
                                     name=str(data.id),
                                     pos=npos)
    mw.add_widget(mw.beings[data.id])


def player_move(data):
    app = App.get_running_app()
    mw = app.root.map_w

    if data.id not in mw.beings:
        npos = mw.from_game_coords((data.coor_pair.src_x,
                                    data.coor_pair.src_y))
        mw.beings[data.id] = BeingWidget(size_hint=(None, None),
                                         size=(16, 20),
                                         name=str(data.id),
                                         pos=npos)
        mw.add_widget(mw.beings[data.id])

    mw.move_being(mw.beings[data.id], data.coor_pair.dst_x,
                  data.coor_pair.dst_y)


def being_remove(data):
    app = App.get_running_app()
    mw = app.root.map_w

    if data.id in mw.beings:
        mw.remove_widget(mw.beings[data.id])
        del mw.beings[data.id]


def being_name_response(data):
    app = App.get_running_app()
    mw = app.root.map_w

    if data.id in mw.beings:
        mw.beings[data.id].name = data.name


def register_all():
    register_extension("smsg_being_chat", being_chat)
    register_extension("smsg_player_chat", player_chat)
    register_extension("smsg_whisper", got_whisper)
    register_extension("smsg_whisper_response", send_whisper_result)
    register_extension("smsg_party_chat", party_chat)
    register_extension("smsg_player_warp", player_warp)
    register_extension("smsg_char_map_info", char_map_info)
    register_extension("smsg_map_login_success", map_login_success)
    register_extension("smsg_being_visible", being_visible)
    register_extension("smsg_being_move", being_move)
    register_extension("smsg_player_update", player_update)
    register_extension("smsg_player_move", player_move)
    register_extension("smsg_being_remove", being_remove)
    register_extension("smsg_being_name_response", being_name_response)
