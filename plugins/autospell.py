import re
import time
import commands
import net.mapserv as mapserv
from loggers import debuglog
from logicmanager import logic_manager

__all__ = [ 'PLUGIN', 'init' ]

PLUGIN = {
    'name': 'autospell',
    'requires': (),
    'blocks': (),
    'default_config' : {}
}

as_re = re.compile(r'(\d+) (\d+) (.+)')
times = 0
delay = 0
spell = ''
next_ts = 0


def cmd_autospell(_, arg):
    '''Cast a spell multiple times automatically
/autospell TIMES DELAY SPELL'''
    global times, delay, spell, next_ts
    m = as_re.match(arg)
    if m:
        times = int(m.group(1))
        delay = int(m.group(2))
        spell = m.group(3)
    else:
        debuglog.warning("Usage: /autospell TIMES DELAY SPELL")
        return

    next_ts = time.time() + delay


def cmd_stopspell(*unused):
    '''Stop casting autospells'''
    global times, delay, spell, next_ts
    times = delay = next_ts = 0


def autospell_logic(ts):
    global times, next_ts
    if times > 0 and ts >= next_ts:
        times -= 1
        next_ts = ts + delay
        mapserv.cmsg_chat_message(spell)


def init(config):
    commands.commands['autospell'] = cmd_autospell
    commands.commands['stopspell'] = cmd_stopspell
    logic_manager.add_logic(autospell_logic)
