import os
import time
import logging
from collections import OrderedDict
import net.mapserv as mapserv
import chatbot
import logicmanager
import status
from net.inventory import get_item_index
from net.trade import reset_trade_state
from utils import encode_str, extends
from itemdb import item_name
from playerlist import PlayerList
from chat import send_whisper as whisper


__all__ = [ 'PLUGIN', 'init', 'shoplog', 'buying', 'selling' ]


PLUGIN = {
    'name': 'shop',
    'requires': ('chatbot',),
    'blocks': (),
    'default_config' : {
        'timeout' : 60,
        'shoplist_txt' : 'shoplist.txt',
        'admins_file' : ''
    }
}

shoplog = logging.getLogger('ManaChat.Shop')
trade_timeout = 60
shop_admins = None


class s:
    player = ''
    mode = ''
    item_id = 0
    amount = 0
    price = 0
    index = 0
    start_time = 0


buying = OrderedDict([
    (621,  (5000, 1)),    # Eyepatch
    (640,  (1450, 100)),  # Iron Ore
    (4001, (650, 300)),   # Coal
])

selling = OrderedDict([
    (535,  (100, 50)),    # Red Apple
    (640,  (1750, 100)),  # Iron Ore
])


def cleanup():
    s.player = ''
    s.mode = ''
    s.item_id = 0
    s.amount = 0
    s.price = 0
    s.index = 0
    s.start_time = 0


# =========================================================================
def selllist(nick, message, is_whisper, match):
    if not is_whisper:
        return

    # Support for 4144's shop (Sell list)
    data = '\302\202B1'

    for id_, (price, amount) in selling.iteritems():
        index = get_item_index(id_)
        if index < 0:
            continue

        _, curr_amount = mapserv.player_inventory[index]
        amount = min(curr_amount, amount)

        data += encode_str(id_, 2)
        data += encode_str(price, 4)
        data += encode_str(amount, 3)

    whisper(nick, data)


def buylist(nick, message, is_whisper, match):
    if not is_whisper:
        return

    # Support for 4144's shop (Sell list)
    data = '\302\202S1'

    for id_, (price, amount) in buying.iteritems():
        index = get_item_index(id_)
        if index > 0:
            _, curr_amount = mapserv.player_inventory[index]
            amount -= curr_amount

        try:
            can_afford = mapserv.player_money / price
        except ZeroDivisionError:
            can_afford = 10000000

        amount = min(can_afford, amount)

        if amount <= 0:
            continue

        data += encode_str(id_, 2)
        data += encode_str(price, 4)
        data += encode_str(amount, 3)

    whisper(nick, data)


def sellitem(nick, message, is_whisper, match):
    if not is_whisper:
        return

    item_id = amount = 0

    # FIXME: check if amount=0 or id=0
    try:
        item_id = int(match.group(1))
        # price = int(match.group(2))
        amount = int(match.group(3))
        if item_id < 1 or amount < 1:
            raise ValueError
    except ValueError:
        whisper(nick, "usage: !sellitem ID PRICE AMOUNT")
        return

    if s.player:
        whisper(nick, "I am currently trading with someone")
        return

    player_id = mapserv.beings_cache.findId(nick)
    if player_id < 0:
        whisper(nick, "I don't see you nearby")
        return

    if item_id not in buying:
        whisper(nick, "I don't buy that")
        return

    real_price, max_amount = buying[item_id]

    index = get_item_index(item_id)
    if index > 0:
        _, curr_amount = mapserv.player_inventory[index]
        max_amount -= curr_amount

    if amount > max_amount:
        whisper(nick, "I don't need that many")
        return

    total_price = real_price * amount
    if total_price > mapserv.player_money:
        whisper(nick, "I can't afford it")
        return

    s.player = nick
    s.mode = 'buy'
    s.item_id = item_id
    s.amount = amount
    s.price = total_price
    s.index = index
    s.start_time = time.time()

    mapserv.cmsg_trade_request(player_id)


def buyitem(nick, message, is_whisper, match):
    if not is_whisper:
        return

    item_id = amount = 0

    # FIXME: check if amount=0 or id=0
    try:
        item_id = int(match.group(1))
        # price = int(match.group(2))
        amount = int(match.group(3))
        if item_id < 1 or amount < 1:
            raise ValueError
    except ValueError:
        whisper(nick, "usage: !buyitem ID PRICE AMOUNT")
        return

    if s.player:
        whisper(nick, "I am currently trading with someone")
        return

    player_id = mapserv.beings_cache.findId(nick)
    if player_id < 0:
        whisper(nick, "I don't see you nearby")
        return

    if item_id not in selling:
        whisper(nick, "I don't sell that")
        return

    real_price, max_amount = selling[item_id]

    index = get_item_index(item_id)
    if index > 0:
        _, curr_amount = mapserv.player_inventory[index]
        max_amount = min(max_amount, curr_amount)
    else:
        max_amount = 0

    if amount > max_amount:
        whisper(nick, "I don't have that many")
        return

    total_price = real_price * amount

    s.player = nick
    s.mode = 'sell'
    s.item_id = item_id
    s.amount = amount
    s.price = total_price
    s.index = index
    s.start_time = time.time()

    mapserv.cmsg_trade_request(player_id)


def retrieve(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if shop_admins is None:
        return

    if not shop_admins.check_player(nick):
        return

    item_id = amount = 0

    try:
        item_id = int(match.group(1))
        amount = int(match.group(2))
        if amount < 1:
            raise ValueError
    except ValueError:
        whisper(nick, "usage: !retrieve ID AMOUNT  (ID=0 for money)")
        return

    if s.player:
        whisper(nick, "I am currently trading with someone")
        return

    player_id = mapserv.beings_cache.findId(nick)
    if player_id < 0:
        whisper(nick, "I don't see you nearby")
        return

    index = max_amount = 0

    if item_id == 0:
        max_amount = mapserv.player_money
    else:
        index = get_item_index(item_id)
        if index > 0:
            max_amount = mapserv.player_inventory[index][1]

    if amount > max_amount:
        whisper(nick, "I don't have that many")
        return

    s.player = nick
    s.mode = 'retrieve'
    s.item_id = item_id
    s.amount = amount
    s.index = index
    s.start_time = time.time()

    mapserv.cmsg_trade_request(player_id)


def invlist(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if shop_admins is None:
        return

    if not shop_admins.check_player(nick):
        return

    ls = status.invlists(50)
    for l in ls:
        whisper(nick, l)


# =========================================================================
@extends('smsg_trade_request')
def trade_request(data):
    shoplog.info("Trade request from %s", data.nick)
    mapserv.cmsg_trade_response(False)
    selllist(data.nick, '', True, None)


@extends('smsg_trade_response')
def trade_response(data):
    code = data.code

    if code == 0:
        shoplog.info("%s is too far", s.player)
        whisper(s.player, "You are too far, please come closer")
        mapserv.cmsg_trade_cancel_request()  # NOTE: do I need it?
        cleanup()

    elif code == 3:
        shoplog.info("%s accepts trade", s.player)
        if s.mode == 'sell':
            mapserv.cmsg_trade_item_add_request(s.index, s.amount)
            mapserv.cmsg_trade_add_complete()
        elif s.mode == 'buy':
            mapserv.cmsg_trade_item_add_request(0, s.price)
            mapserv.cmsg_trade_add_complete()
        elif s.mode == 'retrieve':
            mapserv.cmsg_trade_item_add_request(s.index, s.amount)
            mapserv.cmsg_trade_add_complete()
        else:
            shoplog.error("Unknown shop state: %s", s.mode)
            mapserv.cmsg_trade_cancel_request()
            cleanup()

    elif code == 4:
        shoplog.info("%s cancels trade", s.player)
        cleanup()

    else:
        shoplog.info("Unknown TRADE_RESPONSE code %d", code)
        cleanup()


@extends('smsg_trade_item_add')
def trade_item_add(data):
    item_id, amount = data.id, data.amount

    shoplog.info("%s adds %d %s", s.player, amount, item_name(item_id))

    if item_id == 0:
        return

    if s.mode == 'sell':
        whisper(s.player, "I accept only GP")
        mapserv.cmsg_trade_cancel_request()
        cleanup()

    elif s.mode == 'buy':
        if s.item_id != item_id or s.amount != amount:
            whisper(s.player, "You should give me {} {}".format(
                s.amount, item_name(s.item_id)))
            mapserv.cmsg_trade_cancel_request()
            cleanup()

    elif s.mode == 'retrieve':
        pass

    else:
        shoplog.error("Unknown shop state: %s", s.mode)
        mapserv.cmsg_trade_cancel_request()
        cleanup()


@extends('smsg_trade_item_add_response')
def trade_item_add_response(data):
    code = data.code
    amount = data.amount

    if code == 0:
        if amount > 0:
            item_id, _ = mapserv.trade_state['items_give'][-1]
            shoplog.info("I add to trade %d %s", amount, item_name(item_id))

    elif code == 1:
        shoplog.info("%s is overweight", s.player)
        whisper(s.player, "You are overweight")
        mapserv.cmsg_trade_cancel_request()
        cleanup()

    elif code == 2:
        shoplog.info("%s has no free slots", s.player)
        whisper(s.player, "You don't have free slots")
        mapserv.cmsg_trade_cancel_request()
        cleanup()

    else:
        shoplog.error("Unknown ITEM_ADD_RESPONSE code: ", code)
        mapserv.cmsg_trade_cancel_request()
        cleanup()


@extends('smsg_trade_cancel')
def trade_cancel(data):
    shoplog.error("Trade with %s canceled", s.player)
    cleanup()


@extends('smsg_trade_ok')
def trade_ok(data):
    who = data.who

    if who == 0:
        return

    shoplog.info("Trade OK: %s", s.player)

    if s.mode == 'sell':
        zeny_get = mapserv.trade_state['zeny_get']
        if zeny_get >= s.price:
            mapserv.cmsg_trade_ok()
        else:
            whisper(s.player, "Your offer makes me sad")
            mapserv.cmsg_trade_cancel_request()
            cleanup()

    elif s.mode == 'buy':
        items_get = {}
        for item_id, amount in mapserv.trade_state['items_get']:
            try:
                items_get[item_id] += amount
            except KeyError:
                items_get[item_id] = amount

        if s.item_id in items_get and s.amount == items_get[s.item_id]:
            mapserv.cmsg_trade_ok()
        else:
            whisper(s.player, "You should give me {} {}".format(
                s.amount, item_name(s.item_id)))
            mapserv.cmsg_trade_cancel_request()
            cleanup()

    elif s.mode == 'retrieve':
        mapserv.cmsg_trade_ok()

    else:
        shoplog.error("Unknown shop state: %s", s.mode)
        mapserv.cmsg_trade_cancel_request()
        cleanup()


@extends('smsg_trade_complete')
def trade_complete(data):
    if s.mode == 'sell':
        shoplog.info("Trade with %s completed. I sold %d %s for %d GP",
                     s.player, s.amount, item_name(s.item_id),
                     mapserv.trade_state['zeny_get'])
    elif s.mode == 'buy':
        shoplog.info("Trade with %s completed. I bought %d %s for %d GP",
                     s.player, s.amount, item_name(s.item_id),
                     mapserv.trade_state['zeny_give'])
    elif s.mode == 'retrieve':
        shoplog.info("Trade with %s completed.", s.player)
    else:
        shoplog.info("Trade with %s completed. Unknown shop state %s",
                     s.player, s.mode)

    reset_trade_state(mapserv.trade_state)

    cleanup()


# =========================================================================
def shop_logic(ts):
    if s.start_time > 0:
        if ts > s.start_time + trade_timeout:
            shoplog.warning("%s timed out", s.player)
            mapserv.cmsg_trade_cancel_request()


# =========================================================================
shop_commands = {
    '!selllist' : selllist,
    '!buylist' : buylist,
    '!sellitem (\d+) (\d+) (\d+)' : sellitem,
    '!buyitem (\d+) (\d+) (\d+)' : buyitem,
    '!retrieve (\d+) (\d+)' : retrieve,
    '!invlist' : invlist,
}


def load_shop_list(config):
    global buying
    global selling

    shoplist_txt = config.get('shop', 'shoplist_txt')
    if not os.path.isfile(shoplist_txt):
        shoplog.warning('shoplist file not found : %s', shoplist_txt)
        return

    with open(shoplist_txt, 'r') as f:
        for l in f:
            try:
                item_id, buy_amount, buy_price, sell_amount, sell_price = \
                    map(int, l.split())
                if buy_amount > 0:
                    buying[item_id] = buy_price, buy_amount
                if sell_amount > 0:
                    selling[item_id] = sell_price, sell_amount
            except ValueError:
                pass


def init(config):
    for cmd, action in shop_commands.items():
        chatbot.add_command(cmd, action)

    global trade_timeout
    global shop_admins

    trade_timeout = config.getint('shop', 'timeout')

    shop_admins_file = config.get('shop', 'admins_file')
    if os.path.isfile(shop_admins_file):
        shop_admins = PlayerList(shop_admins_file)

    load_shop_list(config)
    logicmanager.logic_manager.add_logic(shop_logic)
