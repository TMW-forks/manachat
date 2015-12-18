#!/usr/bin/python2

import sys
import datetime


import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.logger import Logger
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
        self.messages_log.append_message(self.chat_input.text)
        self.chat_input.text = ''
        Clock.schedule_once(self._focus_chat_input, 0.1)  # dirty hack :^)
        # app = App.get_running_app()
        # app.root.players_list.items = ["one", "two", "three"]


class ManaGuiApp(App):
    use_kivy_settings = BooleanProperty(True)

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            sys.exit()
            return True
        return False

    def build(self):
        Window.bind(on_keyboard=self.hook_keyboard)
        return RootWidget()


if __name__ == "__main__":
    ManaGuiApp().run()
