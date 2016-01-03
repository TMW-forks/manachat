
import pytmx
from itertools import cycle, islice

from kivy.core.image import Image as CoreImage
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.animation import Animation
from kivy.properties import (StringProperty, ObjectProperty,
        NumericProperty)

from pathfind import breadth_first_search


def kivy_image_loader(filename, colorkey, **kwargs):
    texture = CoreImage(filename).texture

    def loader(rect, flags):
        x, y, w, h = rect
        t = texture.get_region(x,
                               texture.height - y - h,
                               w, h)

        if flags.flipped_diagonally:
            t.flip_horizontal()
            t.flip_vertical()
        elif flags.flipped_vertically:
            t.flip_vertical()
        elif flags.flipped_horizontally:
            t.flip_horizontal()

        return t

    return loader


def create_map_texture(map_data, tile_size=4):
    map_size = len(map_data[0]), len(map_data)
    texture = Texture.create(size=(map_size[0] * tile_size,
                                   map_size[1] * tile_size),
                             colorfmt='rgb')

    c = cycle('\x45\x46\x47')
    s = islice(c, 3 * 4000)
    buf = b''.join(s)

    for y, row in enumerate(map_data):
        for x, cell in enumerate(row):
            if cell > 0:
                continue

            texture.blit_buffer(buf, size=(tile_size, tile_size),
                                colorfmt='rgb',
                                pos=(x * tile_size, y * tile_size))

    texture.flip_vertical()

    return texture


class BeingWidget(Widget):
    anim = ObjectProperty(None)
    name = StringProperty()


class MapWidget(Image):
    tile_size = NumericProperty(16)
    player = ObjectProperty()
    collisions = ObjectProperty(None)
    beings = {}

    def load_map(self, filename, *args):
        m = pytmx.TiledMap(filename=filename)
        data = m.get_layer_by_name('Collision').data
        texture = create_map_texture(data, self.tile_size)
        self.texture = texture
        self.size = texture.size
        self.collisions = data

    def to_game_coords(self, pos):
        ts = self.tile_size
        height = len(self.collisions)
        x = int(pos[0] // ts)
        y = height - int(pos[1] // ts) - 1
        return x, y

    def from_game_coords(self, pos):
        ts = self.tile_size
        height = len(self.collisions)
        x = pos[0] * ts
        y = (height - pos[1] - 1) * ts
        return x, y

    def move_being(self, being, gx, gy):
        ts = self.tile_size
        ox = int(being.x // ts)
        oy = int(being.y // ts)
        gy = len(self.collisions) - gy - 1

        try:
            path = breadth_first_search(self.collisions,
                                        (ox, oy), (gx, gy))
        except KeyError:
            path = []

        if being.anim:
            being.anim.stop(being)

        being.anim = Animation(x=being.x, y=being.y, duration=0)

        for i in range(len(path) - 1):
            cx, cy = path[i + 1]
            px, py = path[i]
            distance = max(abs(cx - px), abs(cy - py))
            being.anim += Animation(x=cx * ts, y=cy * ts,
                                    duration=distance * 0.1)

        being.anim.start(being)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        if not self.collisions:
            return False

        ts = self.tile_size
        x = touch.x - touch.x % ts
        y = touch.y - touch.y % ts

        if touch.button == 'right':
            self.player.pos = x, y
            return True
        if touch.button == 'left':
            ox = int(self.player.x // ts)
            oy = int(self.player.y // ts)
            nx = int(touch.x // ts)
            ny = int(touch.y // ts)

            try:
                path = breadth_first_search(self.collisions,
                                            (ox, oy), (nx, ny))
            except KeyError:
                path = []

            if self.player.anim:
                self.player.anim.stop(self.player)

            self.player.anim = Animation(x=self.player.x,
                                         y=self.player.y,
                                         duration=0)

            for i in range(len(path) - 1):
                cx, cy = path[i + 1]
                px, py = path[i]
                distance = max(abs(cx - px), abs(cy - py))
                self.player.anim += Animation(x=cx * ts, y=cy * ts,
                                              duration=distance * 0.1)

            self.player.anim.start(self.player)
            return True

        return True
