import logging
import string
import random
from logging.handlers import RotatingFileHandler
from collections import OrderedDict
import net.mapserv as mapserv
import chatbot
from net.inventory import get_item_index
from net.trade import reset_trade_state
from utils import encode_str, extends, Schedule
from itemdb import item_name
from playerlist import PlayerList


__all__ = [ 'PLUGIN', 'init', 'shoplog', 'buying', 'selling' ]


PLUGIN = {
    'name': 'crcshop',
    'requires': ('chatbot', 'msgqueue'),
    'blocks': ('shop'),
}

shoplog = logging.getLogger('ManaChat.Shop')
whisper = mapserv.cmsg_chat_whisper
trade_timeout = 90
crc_members = None


class s:
    player = ''
    mode = ''
    item_id = 0
    amount = 0
    price = 0
    index = 0
    timer = None


buying = OrderedDict([
    (753,  (100, 5000)),    # Bat Wing
])

selling = OrderedDict([
    (753,  (100, 1000)),    # Bat Wing
])


def two_rand_chars():
    return random.choice(string.letters) + random.choice(string.letters)


# =========================================================================
def selllist(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if not crc_members.check_player(nick):
        whisper(nick, "I sell only to CRC members, but I buy bat wings from everybody (100gp)")
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

    data += two_rand_chars()

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

    data += two_rand_chars()

    whisper(nick, data)


def cleanup():
    s.player = ''
    s.mode = ''
    s.item_id = 0
    s.amount = 0
    s.price = 0
    s.index = 0
    if s.timer is not None:
        s.timer.cancel()
        s.timer = None


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

    mapserv.cmsg_trade_request(player_id)


def buyitem(nick, message, is_whisper, match):
    if not is_whisper:
        return

    if not crc_members.check_player(nick):
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
        mapserv.cmsg_chat_whisper(nick, "usage: !buyitem ID PRICE AMOUNT")
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

    mapserv.cmsg_trade_request(player_id)


def cancel_timer_function():
    shoplog.warning("%s timed out", s.player)
    mapserv.cmsg_trade_cancel_request()


# =========================================================================
@extends('smsg_trade_request')
def trade_request(data):
    shoplog.info("Trade request from %s", data.nick)
    mapserv.cmsg_trade_response(False)

    if crc_members.check_player(data.nick):
        selllist(data.nick, '', True, None)
    else:
        buylist(data.nick, '', True, None)


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
        s.timer = Schedule(trade_timeout, 30, cancel_timer_function)
        if s.mode == 'sell':
            mapserv.cmsg_trade_item_add_request(s.index, s.amount)
            mapserv.cmsg_trade_add_complete()
        elif s.mode == 'buy':
            mapserv.cmsg_trade_item_add_request(0, s.price)
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
    else:
        shoplog.info("Trade with %s completed. Unknown shop state %s",
                     s.player, s.mode)

    reset_trade_state(mapserv.trade_state)

    cleanup()

# =========================================================================
shop_commands = {
    r'^!selllist' : selllist,
    r'^!buylist' : buylist,
    r'^!sellitem (\d+) (\d+) (\d+)' : sellitem,
    r'^!buyitem (\d+) (\d+) (\d+)' : buyitem,
    r'^!help' : ['[@@https://bitbucket.org/rumly111/manachat|ManaChat@@] by Travolta'],
}


def load_shop_list(config):
    global buying
    global selling
    # here should load shop setup from file


def init(config):
    global crc_members
    chatbot.commands = shop_commands
    load_shop_list(config)
    crc_members = PlayerList('crc.txt')
    logfile = 'shoplog.txt'
    shoplog.setLevel(logging.INFO)
    h = RotatingFileHandler(logfile, maxBytes=102400, backupCount=3)
    fmt = logging.Formatter("[%(asctime)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    h.setFormatter(fmt)
    shoplog.addHandler(h)

    mapserv.timers.append(Schedule(30, 60, mapserv.cmsg_player_emote, 193))
