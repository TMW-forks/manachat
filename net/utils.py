import socket
import asyncore
import logging
from construct import String
from dispatcher import dispatch

def StringZ(name, length, **kw):
    kw['padchar'] = "\x00"
    kw['paddir'] = "right"
    return String(name, length, **kw)

def log_function(fun):
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

class SocketWrapper(asyncore.dispatcher):
    def __init__(self, host=None, port=0, buffer_size=1500, protodef={}):
        asyncore.dispatcher.__init__(self)
        self.buffer_size = buffer_size
        self.read_buffer = self.write_buffer = ''
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.protodef = protodef
        if host is not None:
            self.connect((host, port))

    def writable(self):
        return len(self.write_buffer) > 0

    def readable(self):
        return True

    def handle_write(self):
        sent = self.send(self.write_buffer)
        self.write_buffer = self.write_buffer[sent:]

    def handle_read(self):
        try:
            self.read_buffer += self.recv(2)
        except socket.error:
            return
        while len(self.read_buffer) > 0:
            dispatch(self, self.protodef)

    # @log_function
    def read(self, n = -1):
        data = ''
        if n < 0:
            data = self.read_buffer
            self.read_buffer = ''
        else:
            while len(self.read_buffer) < n:
                try:
                    self.read_buffer += self.recv(n - len(self.read_buffer))
                except socket.error:
                    break
            data = self.read_buffer[:n]
            self.read_buffer = self.read_buffer[n:]
        # print 'data=', repr(data)
        return data

    def write(self, data):
        self.write_buffer += data
