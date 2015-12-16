
# import cui
import mapserv
from utils import register_extension
import commands
from chatlog import chatlog


def curses_being_chat(data):
    id_, message = data.id, data.message
    nick = mapserv.beings_cache[id_].name
    # cui.chatlog_append("{} : {}".format(nick, message))
    chatlog.info("{} : {}".format(nick, message))


def curses_player_chat(data):
    message = data.message
    chatlog.info(message)


def curses_got_whisper(data):
    nick, message = data.nick, data.message
    chatlog.info("[{} ->] {}".format(nick, message))


def send_whisper_result(data):
    if data.code == 0:
        chatlog.info("[-> {}] {}".format(
            commands.whisper_to, commands.whisper_msg))
    else:
        chatlog.info("[error] {} is offline.".format(commands.whisper_to))


def curses_party_chat(data):
    nick = mapserv.party_members.get(data.id, str(data.id))
    msg = data.message
    chatlog.info("[Party] {} : {}".format(nick, msg))


def register_all():
    register_extension("smsg_being_chat", curses_being_chat)
    register_extension("smsg_player_chat", curses_player_chat)
    register_extension("smsg_whisper", curses_got_whisper)
    register_extension("smsg_whisper_response", send_whisper_result)
    register_extension("smsg_party_chat", curses_party_chat)
