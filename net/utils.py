from socket import socket
from construct import String

def StringZ(name, length, **kw):
    kw['padchar'] = "\x00"
    kw['paddir'] = "right"
    return String(name, length, **kw)

class SocketWrapper(socket):
    buffer_size = 1500

    def read(self, n = -1):
        if n < 0:
            n = buffer_size
        return self.recv(n)

    def write(self, data):
        self.send(data)

    def flush():
        pass
