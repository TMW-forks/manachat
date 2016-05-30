import time
import socket
import asyncore
from logging import DEBUG
from construct import Struct, ULInt16, String, Enum, Byte
from dispatcher import dispatch
from loggers import netlog


def StringZ(name, length, **kw):
    kw['padchar'] = "\x00"
    kw['paddir'] = "right"
    return String(name, length, **kw)


def Gender(name):
    return Enum(Byte(name), BOY=1, GIRL=0, UNSPECIFIED=2, OTHER=3)


class SocketWrapper(asyncore.dispatcher_with_send):
    """
    socket wrapper with file-like read() and write() methods
    """
    def __init__(self, host=None, port=0,
                 protodef={}, onerror=None, sock=None):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.read_buffer = ''
        if sock is None:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.protodef = protodef
        self.raw = False
        self.onerror = onerror
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

    def handle_error(self):
        if self.onerror is not None:
            self.onerror()
        else:
            raise

    def read(self, n=-1):
        data = ''
        if n < 0:
            data = self.read_buffer
            self.read_buffer = ''
        else:
            tries = 0
            while len(self.read_buffer) < n:
                try:
                    self.read_buffer += self.recv(n - len(self.read_buffer))
                except socket.error as e:
                    tries += 1
                    if tries < 10:
                        netlog.error("socket.error %s", e)
                        time.sleep(0.2)
                    else:
                        raise

            data = self.read_buffer[:n]
            self.read_buffer = self.read_buffer[n:]

        if netlog.isEnabledFor(DEBUG):
            netlog.debug("read  " +
                         ":".join("{:02x}".format(ord(c)) for c in data))
        return data

    def write(self, data):
        if netlog.isEnabledFor(DEBUG):
            netlog.debug("write " +
                         ":".join("{:02x}".format(ord(c)) for c in data))
        if self.raw:
            self.socket.sendall(data)
        else:
            self.send(data)


def send_packet(srv, opcode_, *fields):
    class C:
        opcode = opcode_

    ms = [ULInt16("opcode")]

    for macro, value in fields:
        setattr(C, macro.name, value)
        ms.append(macro)

    d = Struct("packet", *ms)
    d.build_stream(C, srv)


def distance(x1, y1, x2, y2):
    return max(abs(x2 - x1), abs(y2 - y1))
