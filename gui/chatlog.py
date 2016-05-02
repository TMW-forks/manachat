from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty
from kivy.utils import escape_markup
from kivy.uix.listview import ListView  # , ListItemLabel
from kivy.uix.widget import Widget
from kivy.clock import Clock
# from kivy.uix.label import Label
from utils import log_method

from textutils import (links_to_markup, replace_emotes, preprocess,
                       remove_formatting)


class MyListView(ListView):

    # def __init__(self, *args, **kwargs):
    #     self._views = {}
    #     ListView.__init__(self, *args, **kwargs)

    @log_method
    def populate(self, istart=None, iend=None):
        container = self.container
        sizes = self._sizes
        rh = self.row_height

        # ensure we know what we want to show
        if istart is None:
            istart = self._wstart
            iend = self._wend

        # clear the view
        container.clear_widgets()

        def debugw(w):
            try:
                print w.children[0].texture_size, w.size, w.size_hint, \
                    w.children[0].text
            except Exception as err:
                print err.message

        # guess only ?
        if iend is not None and iend != -1:

            # fill with a "padding"
            fh = 0
            for x in range(istart):
                fh += sizes[x] if x in sizes else rh
            container.add_widget(Widget(size_hint_y=None, height=fh))

            # now fill with real item_view
            index = istart
            while index <= iend:
                # print index, len(self.adapter.data)
                # item_view = ChatLogItem(message=self.adapter.data[index])
                item_view = self.adapter.get_view(index)
                index += 1
                if item_view is None:
                    continue
                container.add_widget(item_view)
                item_view.children[0].texture_update()
                sizes[index] = item_view.height
                debugw(item_view)

        else:
            available_height = self.height
            real_height = 0
            index = self._index
            count = 0
            while available_height > 0:
                # print index, len(self.adapter.data)
                item_view = self.adapter.get_view(index)
                # item_view = ChatLogItem(message=self.adapter.data[index])
                if item_view is None:
                    break

                container.add_widget(item_view)
                item_view.children[0].texture_update()
                sizes[index] = item_view.height
                index += 1
                count += 1

                available_height -= item_view.height
                real_height += item_view.height
                debugw(item_view)

            self._count = count

            # extrapolate the full size of the container from the size
            # of view instances in the adapter
            if count:
                container.height = \
                    real_height / count * self.adapter.get_count()
                if self.row_height is None:
                    self.row_height = real_height / count


class ChatLogItem(GridLayout):
    message = StringProperty()
    background_color = ListProperty([0, 0, 0, 1])
    # text = StringProperty()
    # timestamp = StringProperty()
    # channel = StringProperty()


# def msg_converter(index, msg):
#     b = (index % 2) * 0.04
#     return {'message': msg,
#             'background_color': (0 + b, 0.17 + b, 0.21 + b, 1)}


class ChatLog(GridLayout):

    def append_message(self, msg):
        msg = preprocess(msg, (replace_emotes,
                               remove_formatting))
        msg = links_to_markup(escape_markup(msg))
        self.msg_list.adapter.data.append(msg)
        self.msg_list.children[0].scroll_y = 0

    def msg_converter(self, index, msg):
        b = (index % 2) * 0.04
        return {'message': msg,
                'width': self.width,
                'background_color': (0 + b, 0.17 + b, 0.21 + b, 1)}
