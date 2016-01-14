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
            if self._thread is not threading.current_thread():
                self._thread.join()


# The following group of functions is to provide a way to extend
# a module's functions by decorating them with @extendable

_extensions = {}


def register_extension(name, func):
    if name in _extensions:
        _extensions[name].append(func)
    else:
        _extensions[name] = [func]


def extendable(func):
    """
    Decorator function. If a function is decorated with
    @extendable, each call of it will be followed by calls of
    _extentions[fun.__name__](*args, **kwargs) with same args
    """

    def wrapper(*args, **kwargs):
        name = func.__name__
        func(*args, **kwargs)
        if name in _extensions:
            for f in _extensions[name]:
                f(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def extends(func_name):
    """
    Return a decorator that registers the wrapped function
    as an extention to func_name call.
    See @extendable.
    """

    def decorator(func):

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        register_extension(func_name, func)
        return wrapper

    return decorator


def preprocess_argument(pp_fun, arg=0):
    """
    Make a decorator that modifies 1 argument of a given function
    before calling it.
    pp_fun accepts this argument and returns the modified.
    arg can be either int, then args[arg] is modified, or it
    can be str, then kwargs[arg] is modified
    """

    def decorator(fun):

        def wrapper(*args, **kwargs):
            if isinstance(arg, int):
                if arg < len(args):
                    args = list(args)
                    args[arg] = pp_fun(args[arg])
                elif isinstance(arg, str):
                    if arg in kwargs:
                        kwargs[arg] = pp_fun(kwargs[arg])

            return fun(*args, **kwargs)

        return wrapper

    return decorator


# Encode string - used with 4144 shop compatibility.
def encode_str(value, size):
    output = ''
    base = 94
    start = 33
    while value:
        output += chr(value % base + start)
        value /= base

    while len(output) < size:
        output += chr(start)

    return output
