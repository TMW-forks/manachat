#!/usr/bin/python2

"""
Author: Joseph Botosh <rumly111@gmail.com>
Licence: GPLv2.
"""

import os
import sys
import pytmx


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} <maps-dir>'.format(sys.argv[0]))
        sys.exit(0)

    dirname = sys.argv[1]

    for tmx in (filter(lambda f: f.endswith('.tmx'),
                       os.listdir(dirname))):
        path = os.path.join(dirname, tmx)
        maptag = tmx[:-4]
        m = pytmx.TiledMap(filename=path)
        try:
            if 'name' in m.properties:
                mapname = m.properties['name']
            else:
                mapname = m.properties['Name']
            print maptag, mapname
        except KeyError:
            print '[error]', maptag
