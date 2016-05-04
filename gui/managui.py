#!/usr/bin/python2
# -- coding: utf-8 --

import asyncore
import logging
import webbrowser

import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

from kivy.config import ConfigParser
config = ConfigParser()
config.read("manachat.ini")

import monsterdb
import itemdb
import net
import net.mapserv as mapserv
import gui.handlers as handlers
import plugins
from commands import process_line
from net.onlineusers import OnlineUsers
from loggers import netlog, debuglog


class DebugLogHandler(logging.Handler):

    def __init__(self, app, **kwargs):
        self.app = app
        super(self.__class__, self).__init__(**kwargs)

    def emit(self, record):
        msg = self.format(record)
        self.app.root.messages_log.append_message(msg)


class MenuPopup(Popup):
    visible = BooleanProperty(False)

    def on_open(self, *args):
        self.visible = True

    def on_dismiss(self, *args):
        self.visible = False


class AboutPopup(Popup):
    pass


class RootWidget(FloatLayout):
    mobile = BooleanProperty(False)

    def _focus_chat_input(self, dt):
        self.chat_input.focus = True

    def on_command_enter(self, *args):
        process_line(self.chat_input.text.encode('utf-8'))
        self.chat_input.text = ''
        Clock.schedule_once(self._focus_chat_input, 0.1)  # dirty hack :^)


class ManaGuiApp(App):
    use_kivy_settings = BooleanProperty(False)

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.show_menu(not self._menu_popup.visible)
            # self.stop()
            return True
        return False

    def on_start(self):
        if config.getboolean('Other', 'log_network_packets'):
            import os
            import tempfile

            logfile = os.path.join(tempfile.gettempdir(), "netlog.txt")
            netlog.setLevel(logging.DEBUG)
            fh = logging.FileHandler(logfile, mode="w")
            fmt = logging.Formatter("[%(asctime)s] %(message)s",
                                    datefmt="%Y-%m-%d %H:%M:%S")
            fh.setFormatter(fmt)
            netlog.addHandler(fh)

        monsterdb.read_monster_db()
        itemdb.load_itemdb('itemdb.txt')

        dbgh = DebugLogHandler(self)
        dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                            datefmt="%H:%M"))
        debuglog.addHandler(dbgh)
        debuglog.setLevel(logging.INFO)

        net2 = DebugLogHandler(self)
        net2.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                            datefmt="%H:%M"))
        net2.setLevel(logging.ERROR)
        netlog.addHandler(net2)

        plugins.load_plugins(config)

        handlers.app = self

        # self.reconnect()

        Clock.schedule_once(self.update_online_list, 0.2)
        Clock.schedule_interval(self.update_online_list, 35)
        Clock.schedule_interval(self.update_loop, 0)
        Clock.schedule_once(self.show_menu, 1.5)

    def build(self):
        self.icon = 'icon.png'
        Window.bind(on_keyboard=self.hook_keyboard)
        return RootWidget()

    def build_settings(self, settings):
        settings.add_json_panel('ManaChat', config,
                                filename='manachat.json')

    def update_loop(self, *l):
        asyncore.loop(timeout=0, count=10)

    def on_pause(self):
        return True

    def on_stop(self):
        Clock.unschedule(self.update_loop)
        Clock.unschedule(self.update_online_list)
        mapserv.cleanup()

    def open_link(self, link):
        webbrowser.open(link)

    def update_online_list(self, *l):
        lst = OnlineUsers.dl_online_list(config.get('Other',
                                                    'online_txt_url'))
        if lst is not None:
            lst.sort()
        self.root.players_list.items = lst

    def reconnect(self):
        if mapserv.server is not None:
            mapserv.cleanup()

        net.login(host=config.get('Server', 'host'),
                  port=config.getint('Server', 'port'),
                  username=config.get('Player', 'username'),
                  password=config.get('Player', 'password'),
                  charname=config.get('Player', 'charname'))

        if hasattr(self, '_menu_popup'):
            self._menu_popup.dismiss()

    def show_about(self):
        AboutPopup().open()

    def show_menu(self, show=True):
        if not hasattr(self, '_menu_popup'):
            self._menu_popup = MenuPopup()
        if show:
            self._menu_popup.open()
        else:
            self._menu_popup.dismiss()


if __name__ == "__main__":
    ManaGuiApp().run()
