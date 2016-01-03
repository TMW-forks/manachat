
monster_db = {}


def read_monster_db(file='monsterdb.txt'):
    with open(file) as f:
        for l in f.readlines():
            try:
                index = l.index(' ')
                monster_id = int(l[:index])
                monster_name = l[index + 1:-1]
                monster_db[monster_id] = monster_name
            except ValueError:
                pass

    return monster_db
