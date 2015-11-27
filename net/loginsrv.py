import socket
# import asyncore
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from dispatcher import dispatch

loginsrv = None

def StringZ(name, length, **kw):
    kw['padchar'] = "\x00"
    kw['paddir'] = "right"
    return String(name, length, **kw)

def smsg_server_version(data):
    print "SMSG_SERVER_VERSION {}.{}".format(data.hi, data.lo)

    packet_def = Struct("packet",
                        ULInt16("opcode"),
                        ULInt32("clientversion"),
                        StringZ("username", 24),
                        StringZ("password", 24),
                        Byte("flags"))

    obj = type('login_info', (object,),
               {'opcode': CMSG_LOGIN_REGISTER,
                'clientversion': 3,
                'username': 'john_doe',
                'password': '123456',
                'flags': 3})

    packet_def.build_stream(obj, loginsrv)
    dispatch(loginsrv, login_packets)

def smsg_update_host(data):
    print "SMSG_UPDATE_HOST {}".format(data.host)
    dispatch(loginsrv, login_packets)

def smsg_login_data(data):
    print "SMSG_LOGIN_DATA", data
    loginsrv.close()

def smsg_login_error(data):

    error_codes = {
        0: "Unregistered ID",
        1: "Wrong password",
        2: "Account expired",
        3: "Rejected from server",
        4: "Permban",
        5: "Client too old",
        6: "Temporary ban until {}".format(data.date),
        7: "Server overpopulated",
        9: "Username already taken",
        10: "Wrong name",
        11: "Incurrect email",
        99: "Username permanently erased" }

    print "SMSG_LOGIN_ERROR {}".format(error_codes.get(data.code, "Unknown error"))
    loginsrv.close()

login_packets = {
    0x7531 : (smsg_server_version,
              Struct("data",
                     ULInt32("hi"),
                     ULInt32("lo"))),
    0x0063 : (smsg_update_host,
              Struct("data",
                     ULInt16("length"),
                     StringZ("host",
                            lambda ctx: ctx.length - 4))),
    0x0069 : (smsg_login_data,
              Struct("data",
                     ULInt16("length"),
                     ULInt32("session1"),
                     ULInt32("account"),
                     ULInt32("session2"),
                     IpAddress("oldip"),
                     StringZ("lastlogin", 24),
                     Padding(2),
                     Enum(Byte("gender"),
                          BOY = 1,
                          GIRL = 2),
                     Array(lambda ctx: (ctx.length - 47) / 32,
                           Struct("worlds",
                                  IpAddress("address"),
                                  ULInt16("port"),
                                  StringZ("name", 20),
                                  ULInt16("onlineusers"),
                                  Padding(4))))),

    0x006a : (smsg_login_error,
              Struct("data",
                     Byte("code"),
                     StringZ("date", 20)))
}


class SocketWrapper(socket.socket):
    buffer_size = 1500

    def read(self, n = -1):
        if n < 0:
            n = buffer_size
        return self.recv(n)

    def write(self, data):
        self.send(data)

    def flush():
        pass


if __name__ == "__main__":
    loginsrv = SocketWrapper()
    loginsrv.connect(('server.themanaworld.org', 6902))

    ULInt16("opcode").build_stream(0x7530, loginsrv)
    dispatch(loginsrv, login_packets)

    loginsrv.close()
