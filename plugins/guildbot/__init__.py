import handlers
from guilddb import GuildDB
from net.onlineusers import OnlineUsers

PLUGIN = {
    'name': 'guildbot',
    'requires': (),
    'blocks': (),
}

online_users = None
db = None


def init(config):
    global online_users, db
    online_users = OnlineUsers(config.get('Other', 'online_txt_url'))
    online_users.start()
    db = GuildDB(config.get('GuildBot', 'dbfile'))
