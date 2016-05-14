import net.mapserv as mapserv
from commands import commands, must_have_arg
from loggers import debuglog
from utils import extends
from actor import find_nearest_being


__all__ = [ 'PLUGIN', 'init', 'autonext', 'npc_id' ]


PLUGIN = {
    'name': 'npc',
    'requires': (),
    'blocks': (),
}

npc_id = -1
autonext = True
input_type = 'str'


@extends('smsg_npc_message')
def npc_message(data):
    npc = mapserv.beings_cache.findName(data.id)
    m = '[npc] {} : {}'.format(npc, data.message)
    debuglog.info(m)


@extends('smsg_npc_choice')
def npc_choice(data):
    global npc_id
    global input_type
    npc_id = data.id
    input_type = 'select'
    choices = filter(lambda s: len(s.strip()) > 0,
        data.select.split(':'))
    debuglog.info('[npc][select]')
    for i, s in enumerate(choices):
        debuglog.info('    %d) %s', i + 1, s)


@extends('smsg_npc_close')
def npc_close(data):
    if autonext:
        global npc_id
        npc_id = -1
        mapserv.cmsg_npc_close(data.id)
    else:
        debuglog.info('[npc][close]')


@extends('smsg_npc_next')
def npc_next(data):
    if autonext:
        mapserv.cmsg_npc_next_request(data.id)
    else:
        debuglog.info('[npc][next]')


@extends('smsg_npc_int_input')
def npc_int_input(data):
    global input_type
    input_type = 'int'
    debuglog.info('[npc][input] Enter number:')


@extends('smsg_npc_str_input')
def npc_str_input(data):
    global input_type
    input_type = 'str'
    debuglog.info('[npc][input] Enter string:')


@must_have_arg
def cmd_npctalk(_, arg):
    global npc_id
    jobs = []
    name = ''
    try:
        jobs = [int(arg)]
    except ValueError:
        name = arg

    b = find_nearest_being(name=name, type='npc', allowed_jobs=jobs)

    if b is not None:
        npc_id = b.id
        mapserv.cmsg_npc_talk(npc_id)
    else:
        debuglog.warning("NPC not found")


def cmd_npcclose(*unused):
    global npc_id
    if npc_id > -1:
        mapserv.cmsg_npc_close(npc_id)
        npc_id = -1


def cmd_npcnext(*unused):
    if npc_id > -1:
        mapserv.cmsg_npc_next_request(npc_id)


@must_have_arg
def cmd_npcinput(_, arg):
    if npc_id < 0:
        return

    global input_type

    if input_type == 'int':
        try:
            n = int(arg)
        except ValueError, e:
            debuglog.error(e.message)
            return

        mapserv.cmsg_npc_int_response(npc_id, n)

    elif input_type == 'str':
        mapserv.cmsg_npc_str_response(npc_id, arg)

    elif input_type == 'select':
        mapserv.cmsg_npc_list_choice(npc_id, n)

    input_type = ''


def init(config):
    commands['talk'] = cmd_npctalk
    commands['close'] = cmd_npcclose
    commands['next'] = cmd_npcnext
    commands['input'] = cmd_npcinput
