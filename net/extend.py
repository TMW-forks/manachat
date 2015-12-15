
extensions = {}

def register_extension(name, func):
    if name in extensions:
        extensions[name].append(func)
    else:
        extensions[name] = [func]

def extendable(fun):

    def wrapper(*args, **kwargs):
        name = fun.__name__
        fun(*args, **kwargs)
        if name in extensions:
            for f in extensions[name]:
                f(*args, **kwargs)

    return wrapper
