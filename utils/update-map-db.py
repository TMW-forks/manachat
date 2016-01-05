#!/usr/bin/python2

"""
Update pickle file containing maps information.
It is needed, because for some reason pytmx doesn't work
properly on android.

Author: Joseph Botosh <rumly111@gmail.com>
Licence: GPLv2.
"""

import os
import sys
import pytmx
import pickle


def LoadTmxMap(filename, mapname):
    m = pytmx.TiledMap(filename=filename)

    tmx = {
        'tag': mapname,
        'name': m.properties['name'],
        'width': m.width,
        'height': m.height,
        'collisions': m.get_layer_by_name('Collision').data
    }

    return tmx


def PrintHelp():
    print('Usage: {} <maps-dir> <outfile.pickle>'.format(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        PrintHelp()
        sys.exit(0)
    dirname = sys.argv[1]
    outfile = sys.argv[2]

    with open(outfile, "wb") as out:
        for tmx in (filter(lambda f: f.endswith('.tmx'),
                           os.listdir(dirname))):
            path = os.path.join(dirname, tmx)
            mapname = tmx[:-4]
            print("Loading map {} ...".format(mapname))
            try:
                c = LoadTmxMap(path, mapname)
                print("\tname={} tag={} size=({},{})".format(
                    c['name'], c['tag'], c['width'], c['height']))
                pickle.dump(c, out)
            except KeyError as e:
                print("Error loading {}: {}".format(tmx, e))

    print("Done processing maps")
