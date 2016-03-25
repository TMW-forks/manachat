import net.mapserv as mapserv
from commands import commands, must_have_arg
from loggers import debuglog


__all__ = [ 'PLUGIN', 'init', 'click_npc' ]


PLUGIN = {
    'name': 'npc',
    'requires': (),
    'blocks': (),
}


def find_npc_id(npc_type):
    for _id, b in mapserv.beings_cache.iteritems():
        if b.type == "npc" and b.job == npc_type:
            return _id

    return -1


def click_npc(npc_type):
    npc_id = find_npc_id(npc_type)
    if npc_id > -1:
        mapserv.cmsg_npc_talk(npc_id)


@must_have_arg
def cmd_npctalk(_, type_str):
    try:
        npc_type = int(type_str)
        npc_id = find_npc_id(npc_type)
        if npc_id > -1:
            mapserv.cmsg_npc_talk(npc_id)
        else:
            debuglog.warning("NPC type %d not found", npc_type)
    except ValueError, e:
        debuglog.error(e.message)


def init(config):
    commands['npctalk'] = cmd_npctalk
