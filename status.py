from collections import OrderedDict
import net.mapserv as mapserv
import net.stats as st


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
