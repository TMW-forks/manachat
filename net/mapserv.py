
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from utils import *
from common import netlog, SocketWrapper, send_packet
import charserv
from being import BeingsCache

# migrate to asyncore
# Struct("data"...) should be Struct("functionname"...)
# Session class with it's own asyncore loop and state (???)
# chatlog (where, message)     where=General|Party|Nick|Guild
# move all global variables to g.py

server = None
timers = []
beings_cache = None
party_info = []
party_members = {}


def smsg_ignore(data):
    pass


@extendable
def smsg_being_chat(data):
    beings_cache.add(data.id, 1)
    netlog.info("SMSG_BEING_CHAT {} : {}".format(data.id, data.message))


@extendable
def smsg_being_emotion(data):
    beings_cache.add(data.id, 1)
    netlog.info("SMSG_BEING_EMOTION {} : {}".format(data.id, data.emote))


@extendable
def smsg_being_move(data):
    beings_cache.add(data.id, 1)
    netlog.info("SMSG_BEING_MOVE id={}".format(data.id))


@extendable
def smsg_being_name_response(data):
    beings_cache[data.id].name = data.name
    netlog.info("SMSG_BEING_NAME_RESPONSE id={} name={}".format(
        data.id, data.name))


@extendable
def smsg_being_remove(data):
    beings_cache[data.id].nearby = False
    netlog.info("SMSG_BEING_REMOVE (id={}, deadflag={})".format(
        data.id, data.deadflag))


@extendable
def smsg_being_visible(data):
    beings_cache.add(data.id, data.job)
    netlog.info("SMSG_BEING_VISIBLE (id={}, job={})".format(data.id, data.job))


@extendable
def smsg_player_chat(data):
    netlog.info("SMSG_PLAYER_CHAT {}".format(data.message))


@extendable
def smsg_player_equipment(data):
    netlog.info("SMSG_PLAYER_EQUIPMENT {}".format(data))


@extendable
def smsg_player_inventory(data):
    netlog.info("SMSG_PLAYER_INVENTORY {}".format(data))


@extendable
def smsg_player_inventory_add(data):
    netlog.info("SMSG_PLAYER_INVENTORY_ADD index={} id={} amount={}".format(
        data.index, data.id, data.amount))


@extendable
def smsg_player_inventory_remove(data):
    netlog.info("SMSG_PLAYER_INVENTORY_REMOVE index={} amount={}".format(
        data.index, data.amount))


@extendable
def smsg_player_move(data):
    beings_cache.add(data.id, data.job)
    netlog.info("SMSG_PLAYER_MOVE (id={}, job={})".format(data.id, data.job))


@extendable
def smsg_player_stop(data):
    beings_cache.add(data.id, 1)
    netlog.info("SMSG_PLAYER_STOP (id={}, x={}, y={}".format(
        data.id, data.x, data.y))


@extendable
def smsg_player_update(data):
    beings_cache.add(data.id, data.job)
    netlog.info("SMSG_PLAYER_UPDATE_ (id={}, job={})".format(
        data.id, data.job))


@extendable
def smsg_player_warp(data):
    netlog.info("SMSG_PLAYER_WARP (map={}, x={}, y={}".format(
        data.map, data.x, data.y))


@extendable
def smsg_ip_response(data):
    netlog.info("SMSG_IP_RESPONSE id={} ip={}".format(data.id, data.ip))


@extendable
def smsg_connection_problem(data):
    error_codes = {
        2 : "Account already in use"
    }
    msg = error_codes.get(data.code, str(data.code))
    netlog.error("SMSG_CONNECTION_PROBLEM {}".format(msg))


@extendable
def smsg_gm_chat(data):
    netlog.info("SMSG_GM_CHAT {}".format(data.message))


@extendable
def smsg_party_info(data):
    global party_info, party_members
    party_info = data
    for m in data.members:
        party_members[m.id] = m.nick
    netlog.info("SMSG_PARTY_INFO {}".format(data))


@extendable
def smsg_party_chat(data):
    netlog.info("SMSG_PARTY_CHAT {} : {}".format(data.id, data.message))


@extendable
def smsg_trade_request(data):
    netlog.info("SMSG_TRADE_REQUEST {}".format(data.nick))
    cmsg_trade_response("DECLINE")


@extendable
def smsg_trade_response(data):
    netlog.info("SMSG_TRADE_RESPONSE {}".format(data.code))


@extendable
def smsg_trade_item_add(data):
    netlog.info("SMSG_TRADE_ITEM_ADD id={} amount={}".format(
        data.id, data.amount))


@extendable
def smsg_trade_item_add_response(data):
    netlog.info("SMSG_TRADE_ITEM_ADD_RESPONSE index={} amount={} code={}".format(
        data.index, data.amount, data.code))


@extendable
def smsg_trade_cancel(data):
    netlog.info("SMSG_TRADE_CANCEL")


@extendable
def smsg_trade_ok(data):
    netlog.info("SMSG_TRADE_OK who={}".format(data.who))


@extendable
def smsg_trade_complete(data):
    netlog.info("SMSG_TRADE_COMPLETE")


@extendable
def smsg_whisper(data):
    netlog.info("SMSG_WHISPER {} : {}".format(data.nick, data.message))


@extendable
def smsg_whisper_response(data):
    m = {0: "OK", 1: "Recepient is offline"}
    netlog.info("SMSG_WHISPER_RESPONSE {}".format(m.get(data.code, "error")))


@extendable
def smsg_server_ping(data):
    netlog.info("SMSG_SERVER_PING tick={}".format(data.tick))


@extendable
def smsg_map_login_success(data):
    netlog.info("SMSG_MAP_LOGIN_SUCCESS {}".format(data))
    cmsg_map_loaded()


protodef = {
    0x8000 : (smsg_ignore, Field("data", 2)),      # ignore
    0x008a : (smsg_ignore, Field("data", 27)),     # being-action
    0x009c : (smsg_ignore, Field("data", 7)),      # being-change-direction
    0x00c3 : (smsg_ignore, Field("data", 6)),      # being-change-looks
    0x01d7 : (smsg_ignore, Field("data", 9)),      # being-change-looks2
    0x008d : (smsg_being_chat,
              Struct("data",
                     ULInt16("length"),
                     ULInt32("id"),
                     StringZ("message", lambda ctx: ctx.length - 8))),
    0x00c0 : (smsg_being_emotion,
              Struct("data",
                     ULInt32("id"),
                     Byte("emote"))),
    0x007b : (smsg_being_move,
              Struct("data",
                     ULInt32("id"),
                     Padding(8),
                     ULInt16("job"),
                     Padding(44))),
    0x0086 : (smsg_being_move,
              Struct("data",
                     ULInt32("id"),
                     Padding(10))),
    0x0095 : (smsg_being_name_response,
              Struct("data",
                     ULInt32("id"),
                     StringZ("name", 24))),
    0x0080 : (smsg_being_remove,
              Struct("data",
                     ULInt32("id"),
                     Byte("deadflag"))),
    0x0148 : (smsg_ignore, Field("data", 6)),   # being-resurrect
    0x019b : (smsg_ignore,                      # being-self-effect
              Struct("data",
                     ULInt32("id"),
                     ULInt32("effect"))),
    0x007c : (smsg_ignore, Field("data", 39)),  # spawn
    0x0196 : (smsg_ignore, Field("data", 7)),   # status-change
    0x0078 : (smsg_being_visible,
              Struct("data",
                     ULInt32("id"),
                     Padding(8),
                     ULInt16("job"),
                     Padding(38))),
    0x013c : (smsg_ignore, Field("data", 2)),   # arrow-equip
    0x013b : (smsg_ignore, Field("data", 2)),   # arrow-message
    0x013a : (smsg_ignore, Field("data", 2)),   # attack-range
    0x008e : (smsg_player_chat,
              Struct("data",
                     ULInt16("length"),
                     StringZ("message", lambda ctx: ctx.length - 4))),
    0x00aa : (smsg_ignore,                      # player-equip
              Struct("data",
                     ULInt16("index"),
                     ULInt16("type"),
                     Byte("flag"))),
    0x00a4 : (smsg_player_equipment,
              Struct("data",
                     ULInt16("length"),
                     Array(lambda ctx: (ctx.length - 4) / 20,
                           Struct("items",
                                  ULInt16("index"),
                                  ULInt16("id"),
                                  Padding(16))))),
    0x0195 : (smsg_ignore, Field("data", 100)),  # guild-party-info
    0x01ee : (smsg_player_inventory,
              Struct("data",
                     ULInt16("length"),
                     Array(lambda ctx: (ctx.length - 4) / 18,
                           Struct("items",
                                  ULInt16("index"),
                                  ULInt16("id"),
                                  Padding(2),
                                  ULInt16("amount"),
                                  Padding(10))))),
    0x00a0 : (smsg_player_inventory_add,
              Struct("data",
                     ULInt16("index"),
                     ULInt16("amount"),
                     ULInt16("id"),
                     Padding(15))),
    0x00af : (smsg_player_inventory_remove,
              Struct("data",
                     ULInt16("index"),
                     ULInt16("amount"))),
    0x01c8 : (smsg_ignore, Field("data", 11)),    # player-inventory-use
    0x01da : (smsg_player_move,
              Struct("data",
                     ULInt32("id"),
                     Padding(8),
                     ULInt16("job"),
                     Padding(44))),
    0x0139 : (smsg_ignore, Field("data", 14)),    # player-move-to-attack
    0x010f : (smsg_ignore,                        # player-skills
              Struct("data",
                     ULInt16("length"),
                     Field("data", lambda ctx: ctx.length - 4))),
    0x00b0 : (smsg_ignore, Field("data", 6)),    # player-stat-update-1
    0x00b1 : (smsg_ignore, Field("data", 6)),    # player-stat-update-2
    0x0141 : (smsg_ignore, Field("data", 12)),   # player-stat-update-3
    0x00bc : (smsg_ignore, Field("data", 4)),    # player-stat-update-4
    0x00bd : (smsg_ignore, Field("data", 42)),   # player-stat-update-5
    0x00be : (smsg_ignore, Field("data", 3)),    # player-stat-update-6
    0x0119 : (smsg_ignore, Field("data", 11)),   # player-status-change
    0x0088 : (smsg_player_stop,
              Struct("data",
                     ULInt32("id"),
                     ULInt16("x"),
                     ULInt16("y"))),
    0x00ac : (smsg_ignore, Field("data", 5)),    # player-unequip
    0x01d8 : (smsg_player_update,
              Struct("data",
                     ULInt32("id"),
                     Padding(8),
                     ULInt16("job"),
                     Padding(38))),
    0x01d9 : (smsg_player_update,
              Struct("data",
                     ULInt32("id"),
                     Padding(8),
                     ULInt16("job"),
                     Padding(37))),
    0x0091 : (smsg_player_warp,
              Struct("data",
                     StringZ("map", 16),
                     ULInt16("x"),
                     ULInt16("y"))),
    0x0020 : (smsg_ip_response,
              Struct("data",
                     ULInt32("id"),
                     IpAddress("ip"))),
    0x019a : (smsg_ignore, Field("data", 12)),    # pvp-set
    0x0081 : (smsg_connection_problem,
              Struct("data", Byte("code"))),
    0x009a : (smsg_gm_chat,
              Struct("data",
                     ULInt16("length"),
                     StringZ("message", lambda ctx: ctx.length - 4))),
    0x009e : (smsg_ignore, Field("data", 15)),    # item-dropped
    0x00a1 : (smsg_ignore, Field("data", 4)),     # item-remove
    0x009d : (smsg_ignore, Field("data", 15)),    # item-visible
    0x00fb : (smsg_party_info,
              Struct("data",
                     ULInt16("length"),
                     StringZ("name", 24),
                     Array(lambda ctx: (ctx.length - 28) / 46,
                           Struct("members",
                                  ULInt32("id"),
                                  StringZ("nick", 24),
                                  StringZ("map", 16),
                                  Flag("leader"),
                                  Flag("online"))))),
    0x00fe : (smsg_ignore, Field("data", 28)),    # party-invited
    0x0107 : (smsg_ignore, Field("data", 8)),     # party-update-coords
    0x0106 : (smsg_ignore, Field("data", 8)),     # party-update-hp
    0x0109 : (smsg_party_chat,
              Struct("data",
                     ULInt16("length"),
                     ULInt32("id"),
                     # Probe("debug", show_stream=False, show_stack=False),
                     StringZ("message", lambda ctx: ctx.length - 8))),
    0x01b9 : (smsg_ignore, Field("data", 4)),     # skill-cast-cancel
    0x013e : (smsg_ignore, Field("data", 22)),    # skill-casting
    0x01de : (smsg_ignore, Field("data", 31)),    # skill-damage
    0x011a : (smsg_ignore, Field("data", 13)),    # skill-no-damage
    0x00e5 : (smsg_trade_request,
              Struct("data",
                     StringZ("nick", 24))),
    0x00e7 : (smsg_trade_response,
              Struct("data", Byte("code"))),
    0x00e9 : (smsg_trade_item_add,
              Struct("data",
                     ULInt32("amount"),
                     ULInt16("id"))),
    0x01b1 : (smsg_trade_item_add_response,
              Struct("data",
                     ULInt16("index"),
                     ULInt16("amount"),
                     Byte("code"))),
    0x00ee : (smsg_trade_cancel,
              StaticField("data", 0)),
    0x00f0 : (smsg_trade_complete,
              StaticField("data", 1)),
    0x00ec : (smsg_trade_ok,
              Struct("data", Byte("who"))),
    0x0097 : (smsg_whisper,
              Struct("data",
                     ULInt16("length"),
                     StringZ("nick", 24),
                     StringZ("message", lambda ctx: ctx.length - 28))),
    0x0098 : (smsg_whisper_response,
              Struct("data", Byte("code"))),
    0x0073 : (smsg_map_login_success,
              Struct("data",
                     ULInt32("tick"),
                     # ULInt24("coor"),
                     BitStruct("coor",
                               BitField("x", 10),
                               BitField("y", 10),
                               Nibble("dir")),
                     Padding(2))),
    0x007f : (smsg_server_ping,
              Struct("data",
                     ULInt32("tick")))
}


def cmsg_map_server_connect(account, char_id, session1, session2, gender):
    netlog.info(("CMSG_MAP_SERVER_CONNECT account={} char_id={} "
                 "session1={} session2={} gender={}").format(account,
                    char_id, session1, session2, gender))

    send_packet(server, CMSG_MAP_SERVER_CONNECT,
                (ULInt32("account"), account),
                (ULInt32("char_id"), char_id),
                (ULInt32("session1"), session1),
                (ULInt32("session2"), session2),
                (Gender("gender"), gender))


def cmsg_map_loaded():
    netlog.info("CMSG_MAP_LOADED")
    ULInt16("opcode").build_stream(CMSG_MAP_LOADED, server)


def cmsg_map_server_ping(tick=1):
    netlog.info("CMSG_MAP_SERVER_PING tick={}".format(tick))
    send_packet(server, CMSG_NAME_REQUEST,
                (ULInt32("tick"), tick))


def cmsg_trade_response(answer):
    if answer in ("OK", "ACCEPT", "YES", True):
        answer = 3
    elif answer in ("DECLINE", "CANCEL", "NO", False):
        answer = 4

    s = {3: "ACCEPT", 4: "DECLINE"}

    netlog.info("CMSG_TRADE_RESPONSE {}".format(s[answer]))
    send_packet(server, CMSG_TRADE_RESPONSE,
                (Byte("answer"), answer))


def cmsg_name_request(id_):
    netlog.info("CMSG_NAME_REQUEST id={}".format(id_))
    send_packet(server, CMSG_NAME_REQUEST,
                (ULInt32("id"), id_))


def cmsg_chat_message(msg):
    netlog.info("CMSG_CHAT_MESSAGE {}".format(msg))
    m = "{} : {}".format(charserv.char_name, msg)
    l = len(m)
    send_packet(server, CMSG_CHAT_MESSAGE,
                (ULInt16("len"), l + 5),
                (StringZ("msg", l + 1), m))


def cmsg_chat_whisper(to_, msg):
    netlog.info("CMSG_CHAT_WHISPER to {} : {}".format(to_, msg))
    l = len(msg)
    send_packet(server, CMSG_CHAT_WHISPER,
                (ULInt16("len"), l + 29),
                (StringZ("nick", 24), to_),
                (StringZ("msg", l + 1), msg))


def cmsg_party_message(msg):
    netlog.info("CMSG_PARTY_MESSAGE {}".format(msg))
    l = len(msg)
    send_packet(server, CMSG_PARTY_MESSAGE,
                (ULInt16("len"), l + 4),
                (String("msg", l), msg))


def connect(host, port):
    global server, beings_cache
    beings_cache = BeingsCache(cmsg_name_request)
    server = SocketWrapper(host=host, port=port, protodef=protodef)
    timers.append(Schedule(15, 30, cmsg_map_server_ping))


def cleanup():
    global server
    for t in timers:
        t.cancel()
    server.close()
