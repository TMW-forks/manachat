
from net import mapserv

whisper_to = ''
whisper_msg = ''


def general_chat(msg):
    mapserv.cmsg_chat_message(msg)


def send_whisper(to_, msg):
    global whisper_to, whisper_msg
    whisper_to = to_
    whisper_msg = msg
    mapserv.cmsg_chat_whisper(to_, msg)


def send_party_message(msg):
    mapserv.cmsg_party_message(msg)


def set_direction(dir_str):
    d = {"down": 0, "left": 2, "up": 4, "right": 6}
    dir_num = d.get(dir_str.lower(), 0)
    mapserv.cmsg_player_change_dir(dir_num)


def sit_or_stand(cmd):
    a = {"/sit": 2, "/stand": 3}
    action = a[cmd]
    mapserv.cmsg_player_change_act(action)


def set_destination(arg):
    try:
        x, y = map(int, arg.split())
        mapserv.cmsg_player_change_dest(x, y, 0)
    except ValueError:
        pass


def parse_player_name(line):
    line = line.lstrip()
    if len(line) < 2:
        return "", ""
    if line[0] == '"':
        end = line[1:].find('"')
        if end < 0:
            return line[1:], ""
        else:
            return line[1:end + 1], line[end + 3:]
    else:
        end = line.find(" ")
        if end < 0:
            return line, ""
        else:
            return line[:end], line[end + 1:]


def process_line(line):
    if line == "":
        return
    elif line[0] == "/":
        end = line.find(" ")
        if end < 0:
            cmd = line
            arg = ""
        else:
            cmd = line[:end]
            arg = line[end + 1:]
        if cmd in ("/w", "/whisper"):
            nick, message = parse_player_name(arg)
            if len(nick) > 0 and len(message) > 0:
                send_whisper(nick, message)
        elif cmd in ("/p", "/party"):
            if len(arg) > 0:
                send_party_message(arg)
        elif cmd == "/respawn":
            mapserv.cmsg_player_respawn()
        elif cmd in ("/dir", "/direction", "/turn"):
            if len(arg) > 0:
                set_direction(arg)
        elif cmd in ("/sit", "/stand"):
            sit_or_stand(cmd)
        elif cmd in ("/goto", "/nav", "/navigate", "/dest", "/destination"):
            if len(arg) > 0:
                set_destination(arg)
        else:
            pass
            # chatlog.warning("[warning] command {} not found".format(cmd))
    else:
        general_chat(line)
