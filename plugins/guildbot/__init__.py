import handlers
from guilddb import GuildDB
from net.onlineusers import OnlineUsers

PLUGIN = {
    'name': 'guildbot',
    'requires': (),
    'blocks': (),
}

__all__ = ['PLUGIN', 'init']


def init(config):
    handlers.online_users = OnlineUsers(config.get('Other', 'online_txt_url'),
                                    refresh_hook=handlers.online_list_update)
    handlers.online_users.start()
    handlers.db = GuildDB(config.get('GuildBot', 'dbfile'))
