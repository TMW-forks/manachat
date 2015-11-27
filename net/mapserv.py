
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from dispatcher import dispatch
from utils import *

mapserv = None

def smsg_ignore(data):
    pass

def smsg_being_chat(data):
    print "SMSG_BEING_CHAT {} : {}".format(data.id, data.message)

def smsg_being_emotion(data):
    print "SMSG_BEING_EMOTION {} : {}".format(data.id, data.emote)

def smsg_being_move(data):
    pass

def smsg_being_name_response(data):
    print "SMSG_BEING_NAME_RESPONSE", data

def smsg_being_remove(data):
    print "SMSG_BEING_REMOVE (id={}, deadflag={})".format(data.id, data.deadflag)

def smsg_being_visible(data):
    print "SMSG_BEING_VISIBLE (id={}, job={})".format(data.id, data.job)

def smsg_player_chat(data):
    print "SMSG_PLAYER_CHAT {}".format(data.message)

def smsg_player_equipment(data):
    print "SMSG_PLAYER_EQUIPMENT", data

def smsg_player_inventory(data):
    print "SMSG_PLAYER_INVENTORY", data

def smsg_player_inventory_add(data):
    print "SMSG_PLAYER_INVENTORY_ADD", data

def smsg_player_inventory_remove(data):
    print "SMSG_PLAYER_INVENTORY_REMOVE", data

def smsg_player_move(data):
    print "SMSG_PLAYER_MOVE (id={}, job={})".format(data.id, data.job)

def smsg_player_stop(data):
    print "SMSG_PLAYER_STOP (id={}, x={}, y={}".format(data.id, data.x, data.y)

def smsg_player_update(data):
    pass

def smsg_player_warp(data):
    print "SMSG_PLAYER_WARP (map={}, x={}, y={}".format(data.map, data.x, data.y)

def smsg_ip_response(data):
    print "SMSG_IP_RESPONSE", data

def smsg_connection_problem(data):
    print "SMSG_CONNECTION_PROBLEM (code={})".format(data.code)

def smsg_gm_chat(data):
    print "SMSG_GM_CHAT {}".format(data.message)

def smsg_party_info(data):
    print "SMSG_PARTY_INFO", data

def smsg_party_chat(data):
    print "SMSG_PARTY_CHAT", data

def smsg_trade_request(data):
    print "SMSG_TRADE_REQUEST", data

def smsg_trade_response(data):
    print "SMSG_TRADE_RESPONSE", data

def smsg_trade_item_add(data):
    print "SMSG_TRADE_ITEM_ADD", data

def smsg_trade_item_add_response(data):
    print "SMSG_TRADE_ITEM_ADD_RESPONSE", data

def smsg_trade_cancel(data):
    print "SMSG_TRADE_CANCEL", data

def smsg_trade_ok(data):
    print "SMSG_TRADE_OK", data

def smsg_trade_complete(data):
    print "SMSG_TRADE_COMPLETE", data

def smsg_whisper(data):
    print "SMSG_WHISPER (nick={}, message={})".format(data.nick, data.message)

def smsg_whisper_response(data):
    print "SMSG_WHISPER_RESPONSE", data

def smsg_server_ping(data):
    pass

def smsg_map_login_success(data):
    print "SMSG_MAP_LOGIN_SUCCESS", data

mapserv_packets = {
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
                     ULInt32("effect")))
    0x007c : (smsg_ignore, Field("data", 39)),  # spawn
    0x0196 : (smsg_ignore, Field("data", 7)),   # status-change
    0x0178 : (smsg_being_visible,
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
                     Array(lambda ctx: (ctx.length - 4) / 20,
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
                     ULInt16("length"),
                     StringZ("message", lambda ctx: ctx.length - 4)),
    0x009e : (smsg_ignore, Field("data", 15)),    # item-dropped
    0x00a1 : (smsg_ignore, Field("data", 4)),     # item-remove
    0x009d : (smsg_ignore, Field("data", 15)),    # item-visible
    0x00fb : (smsg_party_info,
              Struct("data",
                     ULInt16("length"),
                     Stringz("name", 24),
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
                     StringZ("message", lambda ctx: ctx.length - 8))),
    0x0109 : (smsg_ignore, Field("data", 4)),     # skill-cast-cancel
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
                     ULInt24("coor"),
                     Padding(2))),
    0x007f : (smsg_server_ping,
              Struct("data",
                     ULInt32("tick")))
}
    

def cmsg_map_server_connect(data):
    global mapserv
    mapserv = SocketWrapper()
    mapserv.connect('server.themanaworld.org', data.worlds[0].port)

    data_def = Struct("packet",
                      ULInt16("opcode"),
                      ULInt32("account"),
                      ULInt32("charid"),
                      ULInt32("session1"),
                      ULInt32("session2"),
                      Enum(Byte("gender"),
                           BOY = 1,
                           GIRL = 0))

    data.opcode = CMSG_MAP_SERVER_CONNECT
    data_def.build_stream(data, mapserv)
