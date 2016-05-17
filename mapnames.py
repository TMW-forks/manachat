
map_names = {}


def read_map_names(file='mapnames.txt'):
    with open(file) as f:
        for l in f.readlines():
            try:
                index = l.index(' ')
                map_id = l[:index]
                map_name = l[index + 1:-1]
                map_names[map_id] = map_name
            except ValueError:
                pass

    return map_names
