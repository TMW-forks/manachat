import re

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


def parse_player_name(line):
    line = line.lstrip()
    if len(line) < 2:
        return "", ""
    if line[0] == '"':
        end = line[1:].find('"')
        if end < 0:
            return line[1:], ""
        else:
            return line[1:end+1], line[end+3:]
    else:
        end = line.find(" ")
        if end < 0:
            return line, ""
        else:
            return line[:end], line[end+1:]


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
            arg = line[end+1:]
        if cmd in ("/w", "/whisper"):
            nick, message = parse_player_name(arg)
            if len(nick) > 0 and len(message) > 0:
                send_whisper(nick, message)
        elif cmd in ("/p", "/party"):
            if len(arg) > 0:
                send_party_message(arg)
        else:
            pass
            # chatlog.warning("[warning] command {} not found".format(cmd))
    else:
        general_chat(line)
