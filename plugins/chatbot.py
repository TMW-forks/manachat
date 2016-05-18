import re
import random
import types
import net.mapserv as mapserv
from utils import extends


__all__ = [ 'PLUGIN', 'init', 'answer', 'add_command' ]


PLUGIN = {
    'name': 'chatbot',
    'requires': (),
    'blocks': (),
}

commands = {}


def answer_info(nick, message, is_whisper, match):
    if is_whisper:
        mapserv.cmsg_chat_whisper(nick, "answer to !info")


def answer_random(nick, message, is_whisper, answers):
    resp = random.choice(answers)
    if is_whisper:
        mapserv.cmsg_chat_whisper(nick, resp)
    else:
        mapserv.cmsg_chat_message(resp)


def answer(nick, message, is_whisper):
    for regex, action in commands.iteritems():
        match = regex.match(message)
        if match:
            if isinstance(action, types.ListType):
                answer_random(nick, message, is_whisper, action)
            elif isinstance(action, types.FunctionType):
                action(nick, message, is_whisper, match)
            else:
                raise ValueError("must be either list or function")


@extends('smsg_being_chat')
def being_chat(data):
    idx = data.message.find(' : ')
    if idx > -1:
        nick = data.message[:idx]
        message = data.message[idx + 3:]
        answer(nick, message, False)


@extends('smsg_whisper')
def got_whisper(data):
    nick, message = data.nick, data.message
    answer(nick, message, True)


def add_command(cmd, action):
    cmd_re = re.compile(cmd)
    commands[cmd_re] = action


def init(config):
    add_command('!info', answer_info)
    add_command('!random', ['Random answer #1', 'Random answer #2'])
