import net.mapserv as mapserv
import chatbot
from utils import encode_str


PLUGIN = {
    'name': 'shop',
    'requires': ('chatbot'),
    'blocks': (),
}


buying = {
    621:  (5000, 1),    # Eyepatch
    640:  (1450, 100),  # Iron Ore
    4001: (650, 200),   # Coal
}


selling = {
    535:  (100, 50),    # Red Apple
    640:  (1750, 100),  # Iron Ore
}


def selllist(nick, message, is_whisper, match):
    if not is_whisper:
        return

    # Support for 4144's shop (Sell list)
    data = '\302\202B1'

    for id_, (price, amount) in selling.iteritems():
        data += encode_str(id_, 2)
        data += encode_str(price, 4)
        data += encode_str(amount, 3)

    mapserv.cmsg_chat_whisper(nick, data)


def buylist(nick, message, is_whisper, match):
    if not is_whisper:
        return

    # Support for 4144's shop (Sell list)
    data = '\302\202S1'

    for id_, (price, amount) in buying.iteritems():
        data += encode_str(id_, 2)
        data += encode_str(price, 4)
        data += encode_str(amount, 3)

    mapserv.cmsg_chat_whisper(nick, data)


def sellitem(nick, message, is_whisper, match):
    if not is_whisper:
        return
    id_ = amount = 0
    try:
        id_ = int(match.group(1))
        amount = int(match.group(2))
    except ValueError:
        mapserv.cmsg_chat_whisper(nick, "usage: !sellitem ID AMOUNT")
        return

    mapserv.cmsg_chat_whisper(nick,
        "this is sellitem ID={} AMOUNT={}".format(id_, amount))


def buyitem(nick, message, is_whisper, match):
    if not is_whisper:
        return
    id_ = amount = 0
    try:
        id_ = int(match.group(1))
        amount = int(match.group(2))
    except ValueError:
        mapserv.cmsg_chat_whisper(nick, "usage: !buyitem ID AMOUNT")
        return

    mapserv.cmsg_chat_whisper(nick,
        "this is buyitem ID={} AMOUNT={}".format(id_, amount))


shop_commands = {
    r'^!selllist' : selllist,
    r'^!buylist' : buylist,
    r'^!sellitem (\d+) (\d+)' : sellitem,
    r'^!buyitem (\d+) (\d+)' : buyitem,
}


def init(config):
    chatbot.commands.update(shop_commands)
