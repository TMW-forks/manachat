import time
import net.mapserv as mapserv
import net.charserv as charserv
import logicmanager
from net.common import distance
from utils import extends


__all__ = [ 'unreachable_ids', 'walkto_and_action', 'target', 'state' ]


_times = {
    'arrival_time': 0,
    'walk_request_time': 0,
}

unreachable_ids = set()
target = None
action = ''
state = ''


def reset_walkto():
    global state
    global target
    global action

    state = ''
    target = None
    action = ''


def walkto_and_action(obj, action_, min_distance=1):
    if obj.id in unreachable_ids:
        return

    global state
    global target
    global action

    if state == 'waiting_confirmation':
        return

    target = obj
    action = action_

    pp = mapserv.player_pos
    dist = distance(pp['x'], pp['y'], target.x, target.y)

    if dist <= min_distance:
        do_action(target, action)
    else:
        state = 'waiting_confirmation'
        _times['walk_request_time'] = time.time()
        mapserv.cmsg_player_change_dest(target.x, target.y)


def do_action(target, action):
    if action == 'attack':
        mapserv.cmsg_player_change_act(target.id, 7)
    elif action == 'pickup':
        mapserv.cmsg_item_pickup(target.id)


def walkto_logic(ts):
    global state

    if state == '':
        return
    elif state == 'waiting_confirmation':
        if ts > _times['walk_request_time'] + 0.5:
            unreachable_ids.add(target.id)
            reset_walkto()
    elif state == 'walking':
        if ts >= _times['arrival_time']:
            state = ''
            do_action(target, action)


@extends('smsg_being_remove')
@extends('smsg_item_remove')
def target_removed(data):
    unreachable_ids.discard(data.id)
    if target and target.id == data.id:
        reset_walkto()
    if data.id == charserv.server.account:
        reset_walkto()


@extends('smsg_player_warp')
def player_warp(data):
    reset_walkto()
    unreachable_ids.clear()


def calc_walk_time(distance, speed=0.15):
    return 0.5 + speed * distance


@extends('smsg_walk_response')
def walk_response(data):
    global state
    if state == 'waiting_confirmation':
        state = 'walking'
        cp = data.coor_pair
        dist = distance(cp.src_x, cp.src_y, cp.dst_x, cp.dst_y)
        _times['arrival_time'] = time.time() + calc_walk_time(dist)


logicmanager.logic_manager.add_logic(walkto_logic)
