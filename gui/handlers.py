
from kivy.app import App
import net.mapserv as mapserv
import commands
from utils import register_extension


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


def register_all():
    register_extension("smsg_being_chat", being_chat)
    register_extension("smsg_player_chat", player_chat)
    register_extension("smsg_whisper", got_whisper)
    register_extension("smsg_whisper_response", send_whisper_result)
    register_extension("smsg_party_chat", party_chat)
    register_extension("smsg_player_warp", player_warp)
