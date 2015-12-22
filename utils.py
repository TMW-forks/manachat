import time
import threading
import logging


def log_method(fun):
    def wrapper(self, *args, **kwargs):
        s_args = s_kwargs = ''
        if args: s_args = ','.join(str(a) for a in args)
        if kwargs: s_kwargs = ','.join('{}={}'.format(k, v)
                                       for k, v in kwargs.items())
        logging.debug('CALL: {}.{}({},{})'.format(self.__class__.__name__,
                                                 fun.__name__,
                                                 s_args, s_kwargs))
        result = fun(self, *args, **kwargs)
        return result
    return wrapper


class Schedule:
    """Class to schedule repeatable events"""
    def __init__(self, start, delay, func, *args, **kwargs):
        self._active = True
        self._next_event = time.time() + start
        self._delay = delay
        self._func = func
        self._thread = threading.Thread(target=self._threadfunc,
                                        args=args, kwargs=kwargs)
        self._thread.start()

    def _threadfunc(self, *args, **kwargs):
        while self._active:
            now = time.time()
            if now >= self._next_event:
                self._next_event += self._delay
                self._func(*args, **kwargs)
            time.sleep(0.1)

    def cancel(self):
        if self._active:
            self._active = False
            self._thread.join()


# The following group of functions is to provide a way to extend
# a module's functions by decorating them with @extendable

_extensions = {}


def register_extension(name, func):
    if name in _extensions:
        _extensions[name].append(func)
    else:
        _extensions[name] = [func]


def extendable(fun):

    def wrapper(*args, **kwargs):
        name = fun.__name__
        fun(*args, **kwargs)
        if name in _extensions:
            for f in _extensions[name]:
                f(*args, **kwargs)

    return wrapper
