#!/usr/bin/python2

import datetime
import asyncore

import kivy
kivy.require('1.9.0')

from kivy.app import App
# from kivy.logger import Logger
# from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, \
    StringProperty, BooleanProperty, ListProperty, OptionProperty

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.listview import ListView, ListItemLabel
from kivy.adapters.listadapter import ListAdapter

from kivy.config import ConfigParser

config = ConfigParser()
config.read("manachat.ini")

import net.loginsrv as loginsrv
import net.mapserv as mapserv
from handlers import register_all
from commands import process_line
from net.onlineusers import OnlineUsers


class MessagesLog(BoxLayout):

    def append_message(self, msg):
        self.msg_log_label.text += '\n{} {}'.format(
            datetime.datetime.now().strftime('%H:%M:%S'), msg)
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

    def _focus_chat_input(self, dt):
        self.chat_input.focus = True

    def on_command_enter(self, *args):
        # self.messages_log.append_message(self.chat_input.text)
        process_line(self.chat_input.text)
        self.chat_input.text = ''
        Clock.schedule_once(self._focus_chat_input, 0.1)  # dirty hack :^)
        # app = App.get_running_app()
        # app.root.players_list.items = ["one", "two", "three"]


class RootWidgetMobile(FloatLayout):

    def on_command_enter(self, *args):
        pass


class ManaGuiApp(App):
    use_kivy_settings = BooleanProperty(False)

    def connect(self):
        loginsrv.connect(config.get('Server', 'host'),
                         config.getint('Server', 'port'))

        loginsrv.server.username = config.get('Player', 'username')
        loginsrv.server.password = config.get('Player', 'password')
        loginsrv.server.char_name = config.get('Player', 'charname')

        loginsrv.cmsg_server_version_request()

    def update_online_list(self, *l):
        self.root.players_list.items = OnlineUsers.dl_online_list(
            config.get('Other', 'online_txt_url'))

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.stop()
            return True
        return False

    def on_start(self):
        if config.getboolean('Other', 'log_network_packets'):
            import os
            import logging
            import tempfile
            from net.common import netlog

            logfile = os.path.join(tempfile.gettempdir(), "netlog.txt")
            netlog.setLevel(logging.INFO)
            fh = logging.FileHandler(logfile, mode="w")
            fmt = logging.Formatter("[%(asctime)s] %(message)s",
                                    datefmt="%Y-%m-%d %H:%M:%S")
            fh.setFormatter(fmt)
            netlog.addHandler(fh)

    def build(self):
        Window.bind(on_keyboard=self.hook_keyboard)
        register_all()
        self.connect()
        Clock.schedule_once(self.update_online_list, 0.2)
        Clock.schedule_interval(self.update_online_list, 35)
        Clock.schedule_interval(self.update_loop, 0)

        use_mobile = config.getboolean('Other', 'use_mobile_interface')
        if use_mobile:
            return RootWidgetMobile()
        else:
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