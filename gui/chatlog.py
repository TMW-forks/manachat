from kivy.event import EventDispatcher
from kivy.uix.abstractview import AbstractView
from kivy.properties import ListProperty, NumericProperty
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.utils import escape_markup
from kivy.clock import Clock
from kivy.uix.label import Label
# from utils import log_method

from textutils import (links_to_markup, replace_emotes, preprocess,
                       remove_formatting)


class ChatLog(AbstractView, EventDispatcher):

    def __init__(self, **kwargs):
        # Check for adapter argument
        if 'adapter' not in kwargs:
            list_adapter = SimpleListAdapter(data=[], cls=Label)
            kwargs['adapter'] = list_adapter

        super(ChatLog, self).__init__(**kwargs)

        self._views = []

        populate = self._trigger_populate = Clock.create_trigger(
            self._populate, -1)

        fbind = self.fbind
        fbind('adapter', populate)

    max_lines = NumericProperty(100)
    cut_lines = NumericProperty(10)

    def _populate(self, *args):
        container = self.container
        adapter = self.adapter
        container.clear_widgets()

        for index in range(adapter.get_count()):
            item_view = adapter.get_view(index)
            self.container.add_widget(item_view)
            self._views.append(item_view)

        container.height = self._container_height()

    def _append(self, msg):
        container = self.container
        adapter = self.adapter
        views = self._views
        cl = self.cut_lines

        if len(views) >= self.max_lines:
            container.clear_widgets(views[:cl])
            self._views = views[cl:]
            adapter.data = adapter.data[cl:]

        adapter.data.append(msg)
        item_view = adapter.get_view(adapter.get_count() - 1)
        item_view.texture_update()

        self._views.append(item_view)
        container.add_widget(item_view)

    def _container_height(self, *args):
        h = 0
        for v in self._views:
            h += v.height
        return h

    def append_message(self, msg):
        msg = preprocess(msg, (replace_emotes,
                               remove_formatting))
        msg = links_to_markup(escape_markup(msg))
        self._append(msg)
        self.container.height = self._container_height()
        self.children[0].scroll_y = 0

    def msg_converter(self, index, msg):
        b = (index % 2) * 0.04
        return {'text': msg,
                'width': self.width,
                'background_color': (0 + b, 0.17 + b, 0.21 + b, 1)}
