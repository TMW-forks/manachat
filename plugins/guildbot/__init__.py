import handlers
from net.onlineusers import OnlineUsers

PLUGIN = {
    'name': 'guildbot',
    'requires': (),
    'blocks': (),
}

online_users = None
db = None


def init(config):
    global online_users
    online_users = OnlineUsers(config.get('Other', 'online_txt_url'))
    online_users.start()
