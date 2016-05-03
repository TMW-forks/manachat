
import os
import re
from kivy.app import App
from kivy.core.audio import SoundLoader
from plyer import notification
import net.mapserv as mapserv
from utils import extends


__all__ = [ 'PLUGIN', 'init', 'timeout', 'guard_words' ]

timeout = 5000
guard_words = ["test1", "illia", "eyepatch"]
sound = None


PLUGIN = {
    'name': 'notify',
    'requires': (),
    'blocks': (),
}


def notify(title, message, use_regex):
    bNotify = False
    if use_regex:
        for regex in guard_words:
            if regex.search(message):
                bNotify = True
                break
    else:
        bNotify = True

    if bNotify:
        app = App.get_running_app()
        icon = os.path.join(app.directory, app.icon)
        notification.notify(title=title, message=message,
                            timeout=timeout,
                            app_name=app.get_application_name(),
                            app_icon=icon)
        if sound is not None:
            sound.play()


@extends('smsg_being_chat')
def being_chat(data):
    app = App.get_running_app()
    if app.root_window.focus:
        return

    notify('General', data.message, True)


@extends('smsg_whisper')
def got_whisper(data):
    app = App.get_running_app()
    if app.root_window.focus:
        return

    nick, message = data.nick, data.message

    notify(nick, message, nick == 'guild')


@extends('smsg_party_chat')
def party_chat(data):
    app = App.get_running_app()
    if app.root_window.focus:
        return

    nick = mapserv.party_members.get(data.id, str(data.id))
    message = data.message
    m = "{} : {}".format(nick, message)

    notify('Party', m, True)


def init(config):
    global timeout
    global sound
    global guard_words

    gw = []
    for w in guard_words:
        gw.append(re.compile(w, re.IGNORECASE))

    gw.append(re.compile(config.get('Player', 'charname'),
                         re.IGNORECASE))
    guard_words = gw

    timeout = config.getint('notify', 'notif_timeout')

    if config.getboolean('notify', 'notif_sound'):
        sound = SoundLoader.load('newmessage.wav')
