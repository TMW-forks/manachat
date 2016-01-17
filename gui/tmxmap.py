
# import pytmx
import zipfile
from itertools import cycle, islice
try:
    import cPickle as pickle
except ImportError:
    import pickle

from kivy.core.image import Image as CoreImage
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.animation import Animation
from kivy.properties import (StringProperty, ObjectProperty,
        NumericProperty, DictProperty)
from kivy.logger import Logger

from pathfind import breadth_first_search
import net.mapserv as mapserv


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
    tile_size = NumericProperty(32)
    player = ObjectProperty()
    collisions = ObjectProperty(None)
    current_attacks = DictProperty()
    beings = DictProperty()
    maps = {}

    def load_map(self, name, *args):
        if name not in self.maps:
            Logger.info("Caching map %s", name)
            zf = zipfile.ZipFile('mapdb.zip', 'r')
            self.maps[name] = pickle.load(zf.open(name + '.pickle'))
            zf.close()
        # m = pytmx.TiledMap(filename=filename)
        # data = m.get_layer_by_name('Collision').data
        texture = create_map_texture(self.maps[name]['collisions'],
                                     self.tile_size)
        self.texture = texture
        self.size = texture.size
        self.collisions = self.maps[name]['collisions']

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

    def move_being(self, being, gx, gy, speed=150):
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
                                    duration=distance * speed / 1000.)

        being.anim.start(being)

    def get_attack_points(self, *bind_args):
        points = []
        try:
            player_id = mapserv.server.char_id
        except AttributeError:
            player_id = 0
        for (id1, id2) in self.current_attacks:
            try:
                # Temporary workaround
                if id1 == player_id:
                    x1, y1 = self.player.pos
                else:
                    x1, y1 = self.beings[id1].pos
                if id2 == player_id:
                    x2, y2 = self.player.pos
                else:
                    x2, y2 = self.beings[id2].pos
                points.extend([x1, y1, x2, y2])
            except:
                pass

        return points

    def get_attack_endpoints(self, *bind_args):
        points = []
        try:
            player_id = mapserv.server.char_id
        except AttributeError:
            player_id = 0
        for (_, target) in self.current_attacks:
            try:
                if target == player_id:
                    x, y = self.player.pos
                else:
                    x, y = self.beings[target].pos
                points.extend([x, y])
            except:
                pass

        return points
