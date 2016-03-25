#!/usr/bin/python2

import asyncore
import logging

import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.logger import Logger
# from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (ObjectProperty, NumericProperty,
        StringProperty, BooleanProperty, ListProperty, OptionProperty)

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.listview import ListView, ListItemLabel
from kivy.adapters.listadapter import ListAdapter

from kivy.config import ConfigParser

config = ConfigParser()
config.read("manachat.ini")

import monsterdb
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


class MessagesLog(BoxLayout):

    def append_message(self, msg):
        if not msg.endswith("\n"):
            msg += "\n"
        self.msg_log_label.text += msg
        self.msg_log_label.parent.scroll_y = 0.0


class PlayersListItem(BoxLayout, ListItemLabel):
    nick = StringProperty(allow_none=False)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)
        return True

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if touch.grab_current is self:
            app = App.get_running_app()
            app.root.chat_input.text = '/w "{}" '.format(self.nick)
            app.root.chat_input.focus = True
            touch.ungrab(self)
            return True


class PlayersList(FloatLayout):
    items = ListProperty([])

    def __init__(self, **kwargs):
        super(PlayersList, self).__init__(**kwargs)

        player_args_coverter = lambda row_index, nick: {"nick" : nick,
            "size_hint_y": None, "height": "30dp", "pos_hint_y": 0.9 }

        list_adapter = ListAdapter(
            data=["Ginaria", "Celestia"],
            args_converter=player_args_coverter,
            selection_mode='single',
            allow_empty_selection=True,
            cls=PlayersListItem)

        list_view = ListView(adapter=list_adapter,
                             size_hint=(1.0, 1.0),
                             pos_hint={'center_x': 0.5})

        def data_changed(instance, value):
            list_adapter.data = value

        self.bind(items=data_changed)

        self.add_widget(list_view)


class RootWidget(FloatLayout):
    mobile = BooleanProperty(False)

    def _focus_chat_input(self, dt):
        self.chat_input.focus = True

    def on_command_enter(self, *args):
        process_line(self.chat_input.text)
        self.chat_input.text = ''
        Clock.schedule_once(self._focus_chat_input, 0.1)  # dirty hack :^)


# class RootWidgetMobile(RootWidget):
#     pass


class ManaGuiApp(App):
    use_kivy_settings = BooleanProperty(False)

    def update_online_list(self, *l):
        self.root.players_list.items = OnlineUsers.dl_online_list(
            config.get('Other', 'online_txt_url'))

    # def move_player(self, sender, touch):
    #     gx, gy = self.root.map_w.to_game_coords(touch.pos)
    #     Logger.info("move_player (%s, %s)", gx, gy)
    #     mapserv.cmsg_player_change_dest(gx, gy)

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.stop()
            return True
        return False

    def on_start(self):
        if config.getboolean('Other', 'log_network_packets'):
            import os
            import tempfile

            logfile = os.path.join(tempfile.gettempdir(), "netlog.txt")
            netlog.setLevel(logging.INFO)
            fh = logging.FileHandler(logfile, mode="w")
            fmt = logging.Formatter("[%(asctime)s] %(message)s",
                                    datefmt="%Y-%m-%d %H:%M:%S")
            fh.setFormatter(fmt)
            netlog.addHandler(fh)

        monsterdb.read_monster_db()

        dbgh = DebugLogHandler(self)
        dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                            datefmt="%H:%M"))
        debuglog.addHandler(dbgh)
        debuglog.setLevel(logging.INFO)

        plugin_list = config.get('Core', 'plugins').split()
        plugins.load_plugins(config, *plugin_list)

        handlers.app = self

        net.login(host=config.get('Server', 'host'),
                  port=config.getint('Server', 'port'),
                  username=config.get('Player', 'username'),
                  password=config.get('Player', 'password'),
                  charname=config.get('Player', 'charname'))

        # self.root.map_w.tile_size = config.getint('GUI', 'tile_size')

        Clock.schedule_once(self.update_online_list, 0.2)
        Clock.schedule_interval(self.update_online_list, 35)
        Clock.schedule_interval(self.update_loop, 0)

    def build(self):
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


if __name__ == "__main__":
    ManaGuiApp().run()
