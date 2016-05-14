from collections import OrderedDict
import net.mapserv as mapserv
import net.stats as st
from utils import encode_str


def stats_repr(*stat_types):
    ps = mapserv.player_stats
    sd = OrderedDict()

    if 'stats' in stat_types:
        sd['stats'] = 'STR:{} AGI:{} VIT:{} INT:{} DEX:{} LUK:{}'.format(
            ps[st.STR], ps[st.AGI], ps[st.VIT], ps[st.VIT],
            ps[st.DEX], ps[st.LUK])

    if 'hpmp' in stat_types:
        sd['hpmp'] = 'HP:{}/{} MP:{}/{}'.format(ps[st.HP], ps[st.MAX_HP],
                                                ps[st.MP], ps[st.MAX_MP])

    if 'weight' in stat_types:
        sd['weight'] = 'WG: {}/{}'.format(ps[st.TOTAL_WEIGHT],
                                          ps[st.MAX_WEIGHT])

    if 'points' in stat_types:
        sd['points'] = 'LVL: {} CP:{} SP:{}'.format(ps[st.LEVEL],
                                                    ps[st.CHAR_POINTS],
                                                    ps[st.SKILL_POINTS])

    if 'zeny' in stat_types:
        sd['zeny'] = 'GP:{}'.format(ps[st.MONEY])

    if 'attack' in stat_types:
        sd['attack'] = 'ATK:{} DEF:{} MATK:{} MDEF:{}'.format(
            ps[st.ATK], ps[st.DEF], ps[st.MATK], ps[st.MDEF])

    return sd


def invlists(max_items=1000):
    inventory = OrderedDict()

    for id_, amount in mapserv.player_inventory.values():
        inventory[id_] = inventory.setdefault(id_, 0) + amount

    lists = []
    data = '\302\202B1'
    i = 0
    for id_, amount in inventory.items():
        i += 1
        if i > max_items:
            i = 0
            lists.append(data)
            data = '\302\202B1'
        data += encode_str(id_, 2)
        data += encode_str(1, 4)
        data += encode_str(amount, 3)

    lists.append(data)
    return lists
