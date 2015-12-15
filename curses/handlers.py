
import cui
import mapserv
from extend import register_extension

def curses_being_chat(data):
    id_, message = data.id, data.message
    nick = mapserv.beings_cache[id_].name
    cui.chatlog_append("{} : {}".format(nick, message))


def curses_player_chat(data):
    message = data.message
    cui.chatlog_append(message)


def curses_got_whisper(data):
    nick, message = data.nick, data.message
    cui.chatlog_append("[w] {} : {}".format(nick, message))


def register_all():
    register_extension("smsg_being_chat", curses_being_chat)
    register_extension("smsg_player_chat", curses_player_chat)
    register_extension("smsg_whisper", curses_got_whisper)
