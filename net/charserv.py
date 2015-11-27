
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from dispatcher import dispatch
from utils import *

charserv = None
char_name = "Trav2"

def smsg_ignore(data):
    dispatch(charserv, charsrv_packets)

def smsg_char_login(data):
    print "SMSG_CHAR_LOGIN", data

    char_slot = -1
    for c in data.chars:
        if c.name == char_name:
            char_slot = c.slot
    if char_slot < 0:
        raise Exception("CharName {} not found".format(char_name))

    data_def = Struct("packet",
                      ULInt16("opcode"),
                      Byte("slot"))

    class packet:
        opcode = CMSG_CHAR_SELECT
        slot = char_slot

    data_def.build_stream(packet, charserv)
    dispatch(charserv, charsrv_packets)

def smsg_char_login_error(data):
    print "SMSG_CHAR_LOGIN_ERROR (code={})".format(data.code)
    charserv.close()

def smsg_char_map_info(data):
    print "SMSG_CHAR_MAP_INFO (CID={} map={} addr={} port={}".format(
        data.char_id, data.map_name, data.address, data.port)
    charserv.close()

charsrv_packets = {
    0x8000 : (smsg_ignore, Field("data", 2)),
    0x006b : (smsg_char_login,
              Struct("data",
                     ULInt16("length"),
                     ULInt16("slots"),
                     Byte("version"),
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

def cmsg_char_server_connect(data):
    global charserv
    charserv = SocketWrapper()
    host, port = 'server.themanaworld.org', data.worlds[0].port
    charserv.connect((host, port))

    data_def = Struct("packet",
                      ULInt16("opcode"),
                      ULInt32("account"),
                      ULInt32("session1"),
                      ULInt32("session2"),
                      ULInt16("proto"),
                      Enum(Byte("gender"),
                           BOY = 1,
                           GIRL = 0))
                      # Byte("gender"))

    data.opcode = CMSG_CHAR_SERVER_CONNECT
    data.proto = 1

    data_def.build_stream(data, charserv)
    dispatch(charserv, charsrv_packets)

