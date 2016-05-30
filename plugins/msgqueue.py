from collections import deque
from loggers import debuglog
from logicmanager import logic_manager


__all__ = [ 'PLUGIN', 'init', 'delayed_functions', 'reload_function' ]


PLUGIN = {
    'name': 'msgqueue',
    'requires': (),
    'blocks': (),
}


reloaded_functions = {}
event_queue = deque()
_times = { 'next_event' : 0 }

delayed_functions = {
    # 'net.mapserv.cmsg_chat_whisper': 7.5,
    # 'net.mapserv.cmsg_chat_message': 3.5,
}


def delayed_function(func_name, delay):

    def func(*args, **kwargs):
        call = (delay, reloaded_functions[func_name], args, kwargs)
        event_queue.append(call)

    return func


def reload_function(name, delay):

    def recurs_import(name):
        m = __import__(name)
        for n in name.split('.')[1:]:
            m = getattr(m, n)
        return m

    ss = name.rsplit('.', 1)

    if len(ss) == 1:
        ss.insert(0, 'net.mapserv')
        name = 'net.mapserv.' + name

    try:
        module = recurs_import(ss[0])
        func_name = ss[1]
        reloaded_functions[name] = getattr(module, func_name)
        setattr(module, func_name, delayed_function(name, delay))
        debuglog.debug('function %s wrapped with delay %d', name, delay)

    except Exception as e:
        debuglog.error('error wrapping function %s: %s', name, e)


def msgq_logic(ts):
    if len(event_queue):
        if ts > _times['next_event']:
            delay, func, args, kwargs = event_queue.popleft()
            _times['next_event'] = ts + delay
            func(*args, **kwargs)


def init(config):
    section = PLUGIN['name']
    for option in config.options(section):
        delayed_functions[option] = config.getfloat(section, option)

    for func_name, delay in delayed_functions.iteritems():
        reload_function(func_name, delay)

    logic_manager.add_logic(msgq_logic)
