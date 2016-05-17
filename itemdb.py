
from loggers import debuglog

item_names = {0: 'GP'}


def load_itemdb(dbfile='itemdb.txt'):
    with open(dbfile, 'rt') as f:
        for l in f.readlines():
            try:
                sn, sr = l.split(' ', 1)
                item_id = int(sn)
                item_name = sr[:-1] if sr.endswith('\n') else sr
                item_names[item_id] = item_name
            except ValueError:
                pass

    debuglog.info("Loaded itemdb from %s", dbfile)
    return item_names


def item_name(item_id, mplus=False):
    name = item_names.get(item_id, 'Item' + str(item_id))
    if mplus:
        return '[@@{}|{}@@]'.format(item_id, name)
    else:
        return name
