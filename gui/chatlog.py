from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from kivy.utils import escape_markup

from textutils import (links_to_markup, replace_emotes, preprocess,
                       remove_formatting)


class ChatLogItem(BoxLayout):
    message = StringProperty()
    timestamp = StringProperty()
    channel = StringProperty()
    background_color = ListProperty([0, 0, 0, 1])


class ChatLog(BoxLayout):

    def append_message(self, msg):
        msg = preprocess(msg, (replace_emotes,
                               remove_formatting))
        msg = links_to_markup(escape_markup(msg))
        self.msg_list.adapter.data.append(msg)
        self.msg_list.children[0].scroll_y = 0

    def msg_converter(self, index, msg):
        b = (index % 2) * 0.04
        return {'message': msg,
                'background_color': (0 + b, 0.17 + b, 0.21 + b, 1)}
