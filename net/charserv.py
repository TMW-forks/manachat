
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from utils import *
import mapserv
from common import netlog, SocketWrapper


server = None
char_name = ""


def smsg_ignore(data):
    pass


@extendable
def smsg_char_login(data):
    netlog.info("SMSG_CHAR_LOGIN {}".format(data))

    char_slot = -1
    for c in data.chars:
        if c.name == char_name:
            char_slot = c.slot
    if char_slot < 0:
        raise Exception("CharName {} not found".format(char_name))

    cmsg_char_select(char_slot)


@extendable
def smsg_char_login_error(data):
    netlog.error("SMSG_CHAR_LOGIN_ERROR (code={})".format(data.code))
    server.close()


@extendable
def smsg_char_map_info(data):
    netlog.info("SMSG_CHAR_MAP_INFO CID={} map={} addr={} port={}".format(
        data.char_id, data.map_name, data.address, data.port))
    server.close()

    # restore session data
    data.account = server.account
    data.session1 = server.session1
    data.session2 = server.session2
    data.gender = server.gender

    mapserv.connect('server.themanaworld.org', data.port)
    mapserv.cmsg_map_server_connect(data)


protodef = {
    0x8000 : (smsg_ignore, Field("data", 2)),
    0x006b : (smsg_char_login,
              Struct("data",
                     ULInt16("length"),
                     ULInt16("slots"),
                     Byte("version"),
                     # Probe("debug", show_stream=False, show_stack=False),
                     Padding(17),
                     Array(lambda ctx: (ctx["length"] - 24) / 106,
                           Struct("chars",
                                  ULInt32("id"),
                                  ULInt32("exp"),
                                  ULInt32("money"),
                                  Padding(46),
                                  ULInt16("level"),
                                  Padding(14),
                                  StringZ("name", 24),
                                  Padding(6),
                                  Byte("slot"),
                                  Padding(1))))),
    0x006c : (smsg_char_login_error,
              Struct("data", Byte("code"))),
    0x0071 : (smsg_char_map_info,
              Struct("data",
                     ULInt32("char_id"),
                     StringZ("map_name", 16),
                     IpAddress("address"),
                     ULInt16("port")))
}


def connect(host, port, char_name_):
    global server, char_name
    char_name = char_name_
    server = SocketWrapper(host=host, port=port, protodef=protodef)
    return server


def cmsg_char_server_connect(data):
    data_def = Struct("packet",
                      ULInt16("opcode"),
                      ULInt32("account"),
                      ULInt32("session1"),
                      ULInt32("session2"),
                      ULInt16("proto"),
                      Enum(Byte("gender"),
                           BOY = 1,
                           GIRL = 0))

    # save session data
    server.account = data.account
    server.session1 = data.session1
    server.session2 = data.session2
    server.gender = data.gender

    data.opcode = CMSG_CHAR_SERVER_CONNECT
    data.proto = 1

    logging.info("CMSG_CHAR_SERVER_CONNECT account={} session1={} session2={} proto={} gender={}".format(
        data.account, data.session1, data.session2, data.proto, data.gender))
    data_def.build_stream(data, server)


def cmsg_char_select(slot):
    netlog.info("CMSG_CHAR_SELECT slot={}".format(slot))
    send_packet(server, CMSG_CHAR_SELECT, (Byte("slot"), slot))
