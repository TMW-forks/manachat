import socket
import asyncore
import logging
from dispatcher import dispatch


netlog = logging.getLogger("ManaChat.Net")
netlog.setLevel(logging.DEBUG)


class SocketWrapper(asyncore.dispatcher_with_send):
    """
    socket wrapper with file-like read() and write() methods
    """
    def __init__(self, host=None, port=0, buffer_size=1500, protodef={}):
        asyncore.dispatcher_with_send.__init__(self)
        self.buffer_size = buffer_size
        self.read_buffer = ''
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.protodef = protodef
        if protodef == {}:
            netlog.warning("protodef is empty")
        if host is not None:
            self.connect((host, port))

    def handle_read(self):
        try:
            self.read_buffer += self.recv(2)
        except socket.error:
            return
        while len(self.read_buffer) > 0:
            dispatch(self, self.protodef)

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
        return data

    def write(self, data):
        self.send(data)
