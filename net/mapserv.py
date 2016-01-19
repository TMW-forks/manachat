
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from common import *
from utils import *
from being import BeingsCache
from item import FloorItem
from inventory import add_to_inventory, remove_from_inventory
from trade import reset_trade_state
from loggers import netlog

server = None
timers = []
beings_cache = None
party_info = []
party_members = {}
player_pos = {'x': 0, 'y': 0, 'dir': 0}
tick = 0
last_whisper = {'to': '', 'msg': ''}
player_inventory = {}
player_stats = {}
player_money = 0
trade_state = {'items_give': [], 'items_get': [],
               'zeny_give': 0, 'zeny_get': 0}
floor_items = {}


# --------------------------------------------------------------------
def smsg_ignore(data):
    pass


@extendable
def smsg_being_chat(data):
    beings_cache.findName(data.id)
    netlog.info("SMSG_BEING_CHAT {} : {}".format(data.id, data.message))


@extendable
def smsg_being_emotion(data):
    beings_cache.findName(data.id)
    netlog.info("SMSG_BEING_EMOTION {} : {}".format(data.id, data.emote))


@extendable
def smsg_being_move(data):
    global tick
    tick = data.tick
    beings_cache.findName(data.id, data.job)
    netlog.info("SMSG_BEING_MOVE {}".format(data))


@extendable
def smsg_being_action(data):
    global tick
    tick = data.tick
    netlog.info("SMSG_BEING_ACTION {}".format(data))


@extendable
def smsg_being_name_response(data):
    beings_cache[data.id].name = data.name
    netlog.info("SMSG_BEING_NAME_RESPONSE id={} name={}".format(
        data.id, data.name))


@extendable
def smsg_being_remove(data):
    try:
        del beings_cache[data.id]
    except KeyError:
        pass
    netlog.info("SMSG_BEING_REMOVE (id={}, deadflag={})".format(
        data.id, data.deadflag))


@extendable
def smsg_being_visible(data):
    beings_cache.findName(data.id, data.job)
    beings_cache[data.id].speed = data.speed
    netlog.info("SMSG_BEING_VISIBLE {}".format(data))


@extendable
def smsg_player_chat(data):
    netlog.info("SMSG_PLAYER_CHAT {}".format(data.message))


@extendable
def smsg_player_equipment(data):
    netlog.info("SMSG_PLAYER_EQUIPMENT {}".format(data))
    for item in data.equipment:
        player_inventory[item.index] = (item.id, 1)


@extendable
def smsg_player_inventory(data):
    netlog.info("SMSG_PLAYER_INVENTORY {}".format(data))
    for item in data.inventory:
        player_inventory[item.index] = (item.id, item.amount)


@extendable
def smsg_player_inventory_add(data):
    netlog.info("SMSG_PLAYER_INVENTORY_ADD index={} id={} amount={}".format(
        data.index, data.id, data.amount))
    add_to_inventory(data.index, data.id, data.amount)


@extendable
def smsg_player_inventory_remove(data):
    netlog.info("SMSG_PLAYER_INVENTORY_REMOVE index={} amount={}".format(
        data.index, data.amount))
    remove_from_inventory(data.index, data.amount)


@extendable
def smsg_player_move(data):
    global tick
    tick = data.tick
    beings_cache.findName(data.id, data.job)
    netlog.info("SMSG_PLAYER_MOVE {}".format(data))


@extendable
def smsg_player_stop(data):
    beings_cache.findName(data.id)
    netlog.info("SMSG_PLAYER_STOP (id={}, x={}, y={}".format(
        data.id, data.x, data.y))


@extendable
def smsg_player_update(data):
    beings_cache.findName(data.id, data.job)
    beings_cache[data.id].speed = data.speed
    netlog.info("SMSG_PLAYER_UPDATE_ {}".format(data))


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
    # cmsg_trade_response("DECLINE")


@extendable
def smsg_trade_response(data):
    netlog.info("SMSG_TRADE_RESPONSE {}".format(data.code))


@extendable
def smsg_trade_item_add(data):
    netlog.info("SMSG_TRADE_ITEM_ADD id={} amount={}".format(
        data.id, data.amount))
    if data.id == 0:
        trade_state['zeny_get'] = data.amount
    else:
        trade_state['items_get'].append((data.id, data.amount))


@extendable
def smsg_trade_item_add_response(data):
    netlog.info(("SMSG_TRADE_ITEM_ADD_RESPONSE"
                 " index={} amount={} code={}").format(
        data.index, data.amount, data.code))

    index = data.index
    amount = data.amount
    code = data.code

    if code == 0 and amount > 0:
        if index > 0:
            item_id, _ = player_inventory[index]
            remove_from_inventory(index, amount)
            trade_state['items_give'].append((item_id, amount))
        elif index == 0:
            trade_state['zeny_give'] = amount


@extendable
def smsg_trade_cancel(data):
    netlog.info("SMSG_TRADE_CANCEL")
    reset_trade_state(trade_state)


@extendable
def smsg_trade_ok(data):
    netlog.info("SMSG_TRADE_OK who={}".format(data.who))


@extendable
def smsg_trade_complete(data):
    netlog.info("SMSG_TRADE_COMPLETE")
    global player_money
    player_money += trade_state['zeny_get'] - trade_state['zeny_give']
    # reset_trade_state(trade_state)


@extendable
def smsg_whisper(data):
    netlog.info("SMSG_WHISPER {} : {}".format(data.nick, data.message))


@extendable
def smsg_whisper_response(data):
    m = {0: "OK", 1: "Recepient is offline"}
    netlog.info("SMSG_WHISPER_RESPONSE {}".format(m.get(data.code, "error")))


@extendable
def smsg_server_ping(data):
    global tick
    tick = data.tick
    netlog.info("SMSG_SERVER_PING tick={}".format(data.tick))


@extendable
def smsg_map_login_success(data):
    netlog.info("SMSG_MAP_LOGIN_SUCCESS {}".format(data))
    global tick
    tick = data.tick
    player_pos['x'] = data.coor.x
    player_pos['y'] = data.coor.y
    player_pos['dir'] = data.coor.dir


@extendable
def smsg_walk_response(data):
    global tick
    tick = data.tick
    player_pos['x'] = data.coor_pair.dst_x
    player_pos['y'] = data.coor_pair.dst_y
    netlog.info("SMSG_WALK_RESPONSE {}".format(data))


@extendable
def smsg_item_visible(data):
    netlog.info("SMSG_ITEM_VISIBLE {}".format(data))
    item = FloorItem(data.type, data.amount, data.x, data.y)
    floor_items[data.id] = item


@extendable
def smsg_item_dropped(data):
    netlog.info("SMSG_ITEM_DROPPED {}".format(data))
    item = FloorItem(data.type, data.amount, data.x, data.y)
    floor_items[data.id] = item


@extendable
def smsg_item_remove(data):
    netlog.info("SMSG_ITEM_REMOVE {}".format(data))
    if data.id in floor_items:
        del floor_items[data.id]


@extendable
def smsg_player_stat_update_x(data):
    netlog.info("SMSG_PLAYER_STAT_UPDATE_X type={} value={}".format(
        data.type, data.stat_value))
    player_stats[data.type] = data.stat_value


# --------------------------------------------------------------------
protodef = {
    0x8000 : (smsg_ignore, Field("data", 2)),      # ignore
    0x008a : (smsg_being_action,
              Struct("data",
                     ULInt32("src_id"),
                     ULInt32("dst_id"),
                     ULInt32("tick"),
                     ULInt32("src_speed"),
                     ULInt32("dst_speed"),
                     ULInt16("damage"),
                     Padding(2),
                     Byte("type"),
                     Padding(2))),
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
                     ULInt16("speed"),
                     Padding(6),
                     ULInt16("job"),
                     Padding(6),
                     ULInt32("tick"),
                     Padding(10),
                     ULInt32("hp"),
                     ULInt32("max_hp"),
                     # Probe("debug", show_stream=False, show_stack=False),
                     Padding(6),
                     BitStruct("coor_pair",
                               BitField("src_x", 10),
                               BitField("src_y", 10),
                               BitField("dst_x", 10),
                               BitField("dst_y", 10)),
                     Padding(5))),
    0x0086 : (smsg_being_move,
              Struct("data",
                     ULInt32("id"),
                     # Padding(10)
                     BitStruct("coor_pair",
                               BitField("src_x", 10),
                               BitField("src_y", 10),
                               BitField("dst_x", 10),
                               BitField("dst_y", 10)),
                     ULInt32("tick"))),  # NOTE 1 byte missing?
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
                     ULInt16("speed"),
                     Padding(6),
                     ULInt16("job"),
                     Padding(16),
                     ULInt32("hp"),
                     ULInt32("max_hp"),
                     Padding(6),
                     BitStruct("coor",
                               BitField("x", 10),
                               BitField("y", 10),
                               Nibble("dir")),
                     Padding(5))),
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
                           Struct("equipment",
                                  ULInt16("index"),
                                  ULInt16("id"),
                                  Padding(16))))),
    0x0195 : (smsg_ignore, Field("data", 100)),  # guild-party-info
    0x01ee : (smsg_player_inventory,
              Struct("data",
                     ULInt16("length"),
                     Array(lambda ctx: (ctx.length - 4) / 18,
                           Struct("inventory",
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
                     ULInt16("speed"),
                     Padding(6),
                     ULInt16("job"),
                     Padding(8),
                     ULInt32("tick"),
                     Padding(22),
                     BitStruct("coor_pair",
                               BitField("src_x", 10),
                               BitField("src_y", 10),
                               BitField("dst_x", 10),
                               BitField("dst_y", 10)),
                     Padding(5))),
    0x0139 : (smsg_ignore, Field("data", 14)),    # player-move-to-attack
    0x010f : (smsg_ignore,                        # player-skills
              Struct("data",
                     ULInt16("length"),
                     Field("data", lambda ctx: ctx.length - 4))),
    0x00b0 : (smsg_player_stat_update_x,
              Struct("data",
                     ULInt16("type"),
                     ULInt32("stat_value"))),
    0x00b1 : (smsg_player_stat_update_x,
              Struct("data",
                     ULInt16("type"),
                     ULInt32("stat_value"))),
    0x0141 : (smsg_player_stat_update_x,
              Struct("data",
                     ULInt32("type"),
                     ULInt32("stat_value"),
                     ULInt32("bonus"))),
    0x00bc : (smsg_player_stat_update_x,
              Struct("data",
                     ULInt16("type"),
                     Flag("ok"),
                     Byte("stat_value"))),
    0x00bd : (smsg_ignore, Field("data", 42)),   # player-stat-update-5
    0x00be : (smsg_player_stat_update_x,
              Struct("data",
                     ULInt16("type"),
                     Byte("stat_value"))),
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
                     ULInt16("speed"),
                     Padding(6),
                     ULInt16("job"),
                     Padding(30),
                     BitStruct("coor",
                               BitField("x", 10),
                               BitField("y", 10),
                               Nibble("dir")),
                     Padding(5))),
    0x01d9 : (smsg_player_update,
              Struct("data",
                     ULInt32("id"),
                     ULInt16("speed"),
                     Padding(6),
                     ULInt16("job"),
                     Padding(30),
                     BitStruct("coor",
                               BitField("x", 10),
                               BitField("y", 10),
                               Nibble("dir")),
                     Padding(4))),
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
    0x009e : (smsg_item_dropped,
              Struct("data",
                     ULInt32("id"),
                     ULInt16("type"),
                     Byte("identify"),
                     ULInt16("x"),
                     ULInt16("y"),
                     Byte("sub_x"),
                     Byte("sub_y"),
                     ULInt16("amount"))),
    0x00a1 : (smsg_item_remove,
              Struct("data", ULInt32("id"))),
    0x009d : (smsg_item_visible,
              Struct("data",
                     ULInt32("id"),
                     ULInt16("type"),
                     Byte("identify"),
                     ULInt16("x"),
                     ULInt16("y"),
                     ULInt16("amount"),
                     Byte("sub_x"),
                     Byte("sub_y"))),
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
                     ULInt32("tick"))),
    0x0087 : (smsg_walk_response,
              Struct("data",
                     ULInt32("tick"),
                     BitStruct("coor_pair",
                               BitField("src_x", 10),
                               BitField("src_y", 10),
                               BitField("dst_x", 10),
                               BitField("dst_y", 10)),
                     Padding(1)))
}


# --------------------------------------------------------------------
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


def cmsg_map_server_ping(tick_=-1):
    netlog.info("CMSG_MAP_SERVER_PING tick={}".format(tick))
    if tick_ < 0:
        tick_ = tick + 1
    send_packet(server, CMSG_MAP_SERVER_PING,
                (ULInt32("tick"), tick_))


def cmsg_trade_response(answer):
    if answer in ("OK", "ACCEPT", "YES", True):
        answer = 3
    elif answer in ("DECLINE", "CANCEL", "NO", False):
        answer = 4

    s = {3: "ACCEPT", 4: "DECLINE"}

    netlog.info("CMSG_TRADE_RESPONSE {}".format(s[answer]))
    send_packet(server, CMSG_TRADE_RESPONSE,
                (Byte("answer"), answer))


def cmsg_trade_request(player_id):
    netlog.info("CMSG_TRADE_REQUEST id={}".format(player_id))
    send_packet(server, CMSG_TRADE_REQUEST,
                (ULInt32("id"), player_id))


def cmsg_trade_item_add_request(index, amount):
    netlog.info("CMSG_TRADE_ITEM_ADD_REQUEST index={} amount={}".format(
        index, amount))

    # Workaround for TMWA, I'm pretty sure it has a bug related to
    # not sending back the amount of GP player added to trade
    if index == 0 and amount <= player_money:
        trade_state['zeny_give'] = amount

    send_packet(server, CMSG_TRADE_ITEM_ADD_REQUEST,
                (ULInt16("index"), index),
                (ULInt32("amount"), amount))


def cmsg_trade_ok():
    netlog.info("CMSG_TRADE_OK")
    ULInt16("opcode").build_stream(CMSG_TRADE_OK, server)


def cmsg_trade_add_complete():
    netlog.info("CMSG_TRADE_ADD_COMPLETE")
    ULInt16("opcode").build_stream(CMSG_TRADE_ADD_COMPLETE, server)


def cmsg_trade_cancel_request():
    netlog.info("CMSG_TRADE_CANCEL_REQUEST")
    ULInt16("opcode").build_stream(CMSG_TRADE_CANCEL_REQUEST, server)


def cmsg_name_request(id_):
    netlog.info("CMSG_NAME_REQUEST id={}".format(id_))
    send_packet(server, CMSG_NAME_REQUEST,
                (ULInt32("id"), id_))


def cmsg_chat_message(msg):
    netlog.info("CMSG_CHAT_MESSAGE {}".format(msg))
    m = "{} : {}".format(server.char_name, msg)
    l = len(m)
    send_packet(server, CMSG_CHAT_MESSAGE,
                (ULInt16("len"), l + 5),
                (StringZ("msg", l + 1), m))


def cmsg_chat_whisper(to_, msg):
    netlog.info("CMSG_CHAT_WHISPER to {} : {}".format(to_, msg))
    last_whisper['to'] = to_
    last_whisper['msg'] = msg
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


def cmsg_player_change_dest(x_, y_):
    netlog.info("CMSG_PLAYER_CHANGE_DEST x={} y={}".format(x_, y_))

    class C:
        opcode = CMSG_PLAYER_CHANGE_DEST

        class coor:
            x = x_
            y = y_
            dir = 0

    d = Struct("packet",
               ULInt16("opcode"),
               BitStruct("coor", BitField("x", 10),
                         BitField("y", 10), Nibble("dir")))

    d.build_stream(C, server)


def cmsg_player_change_dir(new_dir):
    netlog.info("CMSG_PLAYER_CHANGE_DIR {}".format(new_dir))
    send_packet(server, CMSG_PLAYER_CHANGE_DIR,
                (ULInt16("unused"), 0),
                (ULInt8("dir"), new_dir))


def cmsg_player_change_act(id_, action):
    netlog.info("CMSG_PLAYER_CHANGE_ACT id={} action={}".format(id_, action))
    send_packet(server, CMSG_PLAYER_CHANGE_ACT,
                (ULInt32("id"), id_),
                (Byte("action"), action))


def cmsg_player_respawn():
    netlog.info("CMSG_PLAYER_RESPAWN")
    ULInt16("opcode").build_stream(CMSG_PLAYER_RESPAWN, server)


def cmsg_player_emote(emote):
    netlog.info("CMSG_PLAYER_EMOTE {}".format(emote))
    send_packet(server, CMSG_PLAYER_EMOTE,
                (Byte("emote"), emote))


def cmsg_item_pickup(item_id):
    netlog.info("CMSG_ITEM_PICKUP id={}".format(item_id))
    send_packet(server, CMSG_ITEM_PICKUP,
                (ULInt32("id"), item_id))


def cmsg_player_stop_attack():
    netlog.info("CMSG_PLAYER_STOP_ATTACK")
    ULInt16("opcode").build_stream(CMSG_PLAYER_STOP_ATTACK, server)


def cmsg_player_equip(index):
    netlog.info("CMSG_PLAYER_EQUIP index={}".format(index))
    send_packet(server, CMSG_PLAYER_EQUIP,
                (ULInt16("index"), index),
                (ULInt16("unused"), 0))


def cmsg_player_unequip(index):
    netlog.info("CMSG_PLAYER_UNEQUIP index={}".format(index))
    send_packet(server, CMSG_PLAYER_UNEQUIP,
                (ULInt16("index"), index))


def cmsg_player_inventory_use(index, item_id):
    netlog.info("CMSG_PLAYER_INVENTORY_USE index={} id={}".format(
        index, item_id))
    send_packet(server, CMSG_PLAYER_INVENTORY_USE,
                (ULInt16("index"), index),
                (ULInt32("id"), item_id))


def cmsg_player_inventory_drop(index, amount):
    netlog.info("CMSG_PLAYER_INVENTORY_DROP index={} amount={}".format(
        index, amount))
    send_packet(server, CMSG_PLAYER_INVENTORY_DROP,
                (ULInt16("index"), index),
                (ULInt32("amount"), amount))


# --------------------------------------------------------------------
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
