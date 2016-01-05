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
import zipfile
import pytmx

try:
    import cPickle as pickle
except:
    import pickle

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
    del zlib
except:
    compression = zipfile.ZIP_STORED


modes = { zipfile.ZIP_DEFLATED: 'deflated',
          zipfile.ZIP_STORED:   'stored' }


def LoadTmxMap(filename, maptag):
    m = pytmx.TiledMap(filename=filename)

    tmx = {
        'tag': maptag,
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

    n = 0
    zf = zipfile.ZipFile(outfile, 'w')

    for tmx in (filter(lambda f: f.endswith('.tmx'),
                       os.listdir(dirname))):
        path = os.path.join(dirname, tmx)
        maptag = tmx[:-4]
        print("Loading map {} ...".format(path))
        try:
            c = LoadTmxMap(path, maptag)
            print("\tname={} tag={} size=({},{})".format(
                c['name'], c['tag'], c['width'], c['height']))
            zf.writestr(maptag + '.pickle', pickle.dumps(c), compression)
            n += 1
        except KeyError as e:
            print("Error loading {}: {}".format(tmx, e))

    zf.close()
    print("Done processing {} maps".format(n))
