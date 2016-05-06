
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
import mapserv
from protocol import *
from utils import *
from common import *
from loggers import netlog

server = None


def smsg_ignore(data):
    pass


@extendable
def smsg_char_login(data):
    netlog.info("SMSG_CHAR_LOGIN {}".format(data))

    char_slot = -1
    for c in data.chars:
        if c.name == server.char_name:
            char_slot = c.slot
            mapserv.player_money = c.money
            break
    if char_slot < 0:
        netlog.error("CharName {} not found".format(server.char_name))
        server.close()
    else:
        cmsg_char_select(char_slot)


@extendable
def smsg_char_login_error(data):
    netlog.error("SMSG_CHAR_LOGIN_ERROR (code={})".format(data.code))
    server.close()


@extendable
def smsg_char_map_info(data):
    netlog.info("SMSG_CHAR_MAP_INFO CID={} map={} address={} port={}".format(
        data.char_id, data.map_name, data.address, data.port))
    server.close()

    mapserv.connect(data.address, data.port)
    mapserv.server.char_name = server.char_name
    mapserv.server.char_id = data.char_id
    mapserv.player_pos['map'] = data.map_name
    mapserv.cmsg_map_server_connect(server.account, data.char_id,
                                    server.session1, server.session2,
                                    server.gender)


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


def cmsg_char_server_connect(account, session1, session2, proto, gender):
    netlog.info(("CMSG_CHAR_SERVER_CONNECT account={} session1={} "
                 "session2={} proto={} gender={}").format(
        account, session1, session2, proto, gender))

    # save session data
    server.account = account
    server.session1 = session1
    server.session2 = session2
    server.gender = gender

    send_packet(server, CMSG_CHAR_SERVER_CONNECT,
                (ULInt32("account"), account),
                (ULInt32("session1"), session1),
                (ULInt32("session2"), session2),
                (ULInt16("proto"), proto),
                (Gender("gender"), gender))


def cmsg_char_select(slot):
    netlog.info("CMSG_CHAR_SELECT slot={}".format(slot))
    send_packet(server, CMSG_CHAR_SELECT, (Byte("slot"), slot))


def connect(host, port):
    global server
    server = SocketWrapper(host=host, port=port, protodef=protodef)
