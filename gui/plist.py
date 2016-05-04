from kivy.app import App
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ListProperty
from kivy.uix.listview import ListView, ListItemLabel


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
