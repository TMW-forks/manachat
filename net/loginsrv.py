import asyncore
import logging
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from dispatcher import dispatch
from utils import *
import charserv
from common import netlog, SocketWrapper


server = None
username = ''
password = ''


def smsg_server_version(data):
    netlog.info("SMSG_SERVER_VERSION {}.{}".format(data.hi, data.lo))

    packet_def = Struct("packet",
                        ULInt16("opcode"),
                        ULInt32("clientversion"),
                        StringZ("username", 24),
                        StringZ("password", 24),
                        Byte("flags"))

    class packet:
        opcode = CMSG_LOGIN_REGISTER
        clientversion = 3
        username = username
        password = password
        flags = 3

    netlog.info("CMSG_LOGIN_REGISTER username={} password={}".format(username, password))
    packet_def.build_stream(packet, server)


def smsg_update_host(data):
    netlog.info("SMSG_UPDATE_HOST {}".format(data.host))


def smsg_login_data(data):
    netlog.info("SMSG_LOGIN_DATA {}".format(data))
    server.close()

    charserv.connect('server.themanaworld.org',
                     data.worlds[0].port,
                     'Trav2')                      # FIXME move to config
    charserv.cmsg_char_server_connect(data)


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

    netlog.error("SMSG_LOGIN_ERROR {}".format(error_codes.get(data.code, "Unknown error")))
    server.close()


protodef = {
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
                          GIRL = 0),
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


def cmsg_server_version_request():
    netlog.info("CMSG_SERVER_VERSION_REQUEST")
    ULInt16("opcode").build_stream(0x7530, server)


def connect(host, port, username_, password_):
    global server, username, password
    username = username_
    password = password_
    server = SocketWrapper(host=host, port=port, protodef=protodef)
    return server


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    connect('server.themanaworld.org', 6902, 'john_doe', '123456')
    cmsg_server_version_request()
    asyncore.loop()
