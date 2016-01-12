import mapserv


def get_item_index(item_id):
    for index, (id_, _) in mapserv.player_inventory.iteritems():
        if id_ == item_id:
            return index

    return -10


def remove_from_inventory(index, amount):
    item_id, curr_amount = mapserv.player_inventory[index]
    curr_amount -= amount
    if curr_amount <= 0:
        del mapserv.player_inventory[index]
    else:
        mapserv.player_inventory[index] = item_id, curr_amount


def add_to_inventory(index, item_id, amount):
    if index not in mapserv.player_inventory:
        mapserv.player_inventory[index] = item_id, amount
    else:
        _, curr_amount = mapserv.player_inventory[index]
        mapserv.player_inventory[index] = item_id, curr_amount + amount
