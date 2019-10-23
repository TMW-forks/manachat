import net.mapserv as mapserv
from logicmanager import logic_manager

__all__ = ['is_shop', 'is_afk', 'is_idle']

is_shop = False
is_afk = False
is_idle = False

badge_ts = 0


def badge_logic(ts):
    if mapserv.server is None:
        return

    global badge_ts

    if ts > badge_ts + 30:
        badge_ts = ts
        emote = 0xC0
        if is_shop:
            emote += 1
        if is_afk:
            emote += 2
        if is_idle:
            emote += 4
        if is_shop or is_afk or is_idle:
            mapserv.cmsg_player_emote(emote)


logic_manager.add_logic(badge_logic)
