import time
import threading
from collections import deque
from loggers import debuglog


__all__ = [ 'PLUGIN', 'init', 'delayed_functions', 'reload_function' ]


PLUGIN = {
    'name': 'msgqueue',
    'requires': (),
    'blocks': (),
}


scheduler = None
reloaded_functions = {}

delayed_functions = {
    'net.mapserv.cmsg_chat_whisper': 4.5,
    'net.mapserv.cmsg_chat_message': 3.5,
}


class EventScheduler(threading.Thread):

    def __init__(self, start=True):
        threading.Thread.__init__(self)
        self._queue = deque()
        self._active = True
        self._next_event = 0
        if start:
            self.start()

    def run(self, *args, **kwargs):
        while self._active:
            if len(self._queue):
                now = time.time()
                if now >= self._next_event:
                    delay, func, args, kwargs = self._queue.popleft()
                    self._next_event = now + delay
                    func(*args, **kwargs)

            time.sleep(0.1)

    def schedule(self, delay, func, *args, **kwargs):
        call = (delay, func, args, kwargs)
        self._queue.append(call)

    def cancel(self):
        self._active = False


def delayed_function(func_name, delay):

    def func(*args, **kwargs):
        scheduler.schedule(delay, reloaded_functions[func_name],
                           *args, **kwargs)

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


def init(config):
    global scheduler

    for func_name, delay in delayed_functions.iteritems():
        reload_function(func_name, delay)

    scheduler = EventScheduler(start=False)
    scheduler.setDaemon(True)
    scheduler.start()
