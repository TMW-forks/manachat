#!/usr/bin/python2

import sys
import datetime


import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.logger import Logger
# from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, NumericProperty, \
    StringProperty, BooleanProperty, ListProperty, OptionProperty

from kivy.core.window import Window
from kivy.clock import Clock


class MessagesLog(BoxLayout):

    def append_message(self, msg):
        self.msg_log_label.text += '\n{} {}'.format(
            datetime.datetime.now().strftime('%H:%M:%S'), msg)
        self.msg_log_label.parent.scroll_y = 0.0


class PlayersList(FloatLayout):
    pass


class RootWidget(FloatLayout):

    def _focus_chat_input(self, dt):
        self.chat_input.focus = True

    def on_command_enter(self, *args):
        self.messages_log.append_message(self.chat_input.text)
        self.chat_input.text = ''
        Clock.schedule_once(self._focus_chat_input, 0.1)  # dirty hack :^)


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
