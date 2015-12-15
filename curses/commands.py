import re
import mapserv

regex = re.compile('^/(\w+)\s+((?:")[^"]+(?:")|\S+)(\s+(.*))?$')
last_event = []
whisper_to = ''
whisper_msg = ''

def general_chat(msg):
    mapserv.cmsg_chat_message(msg)


def send_whisper(to_, msg):
    global whisper_to, whisper_msg
    whisper_to = to_
    whisper_msg = msg
    mapserv.cmsg_chat_whisper(to_, msg)


commands = {
    "w" : send_whisper,
    "whisper" : send_whisper,
}

def parse_cmdargs(line):
    cmd = player = args = None
    m = regex.search(line)
    if m:
        cmd = m.group(1)
        player = m.group(2)
        if player.startswith('"') and player.endswith('"'):
            player = player[1:-1]
        args = m.group(4)
    return (cmd, player, args)


def process_line(line):
    cmd, player, args = parse_cmdargs(line)
    if cmd is None:
        general_chat(line)
    else:
        f = commands.get(cmd)
        if f is not None:
            f(player, args)
        else:
            cui.chatlog_append("Command {} not found".format(cmd))



if __name__ == "__main__":
    s = raw_input("Enter command: ")
    print parse_cmdargs(s)
