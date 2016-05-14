import net.mapserv as mapserv
from net.common import distance


def find_nearest_being(name='', type='', ignored_ids=[], allowed_jobs=[]):

    if mapserv.beings_cache is None:
        return None

    min_disance = 1000000
    px = mapserv.player_pos['x']
    py = mapserv.player_pos['y']
    nearest = None

    for b in mapserv.beings_cache.values():
        if b.id in ignored_ids:
            continue
        if name and b.name != name:
            continue
        if type and b.type != type:
            continue
        if allowed_jobs and b.job not in allowed_jobs:
            continue
        dist = distance(px, py, b.x, b.y)
        if dist < min_disance:
            min_disance = dist
            nearest = b

    return nearest
