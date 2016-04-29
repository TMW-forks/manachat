import os
import logging

import net.mapserv as mapserv
from loggers import chatlog
from utils import extends


__all__ = [ 'PLUGIN', 'init', 'ChatLogHandler' ]


PLUGIN = {
    'name': 'chatlogfile',
    'requires': (),
    'blocks': (),
}


class ChatLogHandler(logging.Handler):

    def __init__(self, chat_log_dir):
        logging.Handler.__init__(self, 0)
        self.chat_log_dir = chat_log_dir
        self.loggers = {}
        if not os.path.exists(self.chat_log_dir):
            os.makedirs(self.chat_log_dir)

    def emit(self, record):
        try:
            user = record.user
        except AttributeError:
            return

        user = ''.join(map(lambda c: c if c.isalnum() else '_', user))

        if user in self.loggers:
            logger = self.loggers[user]
        else:
            logger = chatlog.getChild(user)
            self.loggers[user] = logger
            # FIXME: it can open too many files, need cleanup
            handler = logging.FileHandler(os.path.join(
                self.chat_log_dir, user + ".txt"))
            logger.addHandler(handler)

        message = self.format(record)
        logger.info(message)


def log(message, user='General'):
    chatlog.info(message, extra={'user': user})


@extends('smsg_being_chat')
def being_chat(data):
    log(data.message)


@extends('smsg_player_chat')
def player_chat(data):
    message = data.message
    log(message)


@extends('smsg_whisper')
def got_whisper(data):
    nick, message = data.nick, data.message
    m = "[{} ->] {}".format(nick, message)
    log(m, nick)


@extends('smsg_whisper_response')
def send_whisper_result(data):
    if data.code == 0:
        m = "[-> {}] {}".format(mapserv.last_whisper['to'],
                                mapserv.last_whisper['msg'])
        log(m, mapserv.last_whisper['to'])


@extends('smsg_party_chat')
def party_chat(data):
    nick = mapserv.party_members.get(data.id, str(data.id))
    msg = data.message
    m = "[Party] {} : {}".format(nick, msg)
    log(m, "Party")


def init(config):
    chatlog_dir = config.get('Other', 'chatlog_dir')

    clh = ChatLogHandler(chatlog_dir)
    clh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                       datefmt="%Y-%m-%d %H:%M:%S"))
    chatlog.addHandler(clh)
    chatlog.setLevel(logging.INFO)
