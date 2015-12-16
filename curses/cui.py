#-*- coding: utf-8 -*-
"""
Curses-based console user interface for TMW chat client.
"""

import curses
from curses.textpad import Textbox

stdscr = None
chatlog_win = None
input_win = None
players_win = None
input_textbox = None


def init():
    global stdscr, chatlog_win, input_win, players_win, input_textbox

    stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(1)
    
    h, w = stdscr.getmaxyx()
    PNW = 20  # player name width
    INH = 4   # input window height

    stdscr.vline(0, w - PNW - 1, curses.ACS_VLINE, h)
    stdscr.hline(h - INH - 1, 0, curses.ACS_HLINE, w - PNW - 1)

    chatlog_win = curses.newwin(h - INH - 1, w - PNW - 1, 0, 0)
    input_win = curses.newwin(INH, w - PNW - 1, h - INH, 0)
    players_win = curses.newwin(h, PNW, 0, w - PNW)

    chatlog_win.idlok(1)
    chatlog_win.scrollok(1)

    players_win.idlok(1)
    players_win.scrollok(1)


    input_textbox = Textbox(input_win)
    input_textbox.stripspaces = True

    stdscr.noutrefresh()
    input_win.noutrefresh()
    players_win.noutrefresh()
    chatlog_win.noutrefresh()

    curses.doupdate()


def chatlog_append(line):
    if line[-1] != "\n":
        line = line + "\n"
    chatlog_win.addstr(line)
    chatlog_win.refresh()


def input_loop(callback):
    def v(ch):
        # chatlog_append(curses.keyname(ch))
        if ch in (curses.KEY_ENTER, curses.ascii.NL):
            return curses.ascii.BEL
        return ch

    cmd = ''
    while cmd not in ('/exit', '/quit'):
        cmd = input_textbox.edit(v).strip()
        callback(cmd)
        input_win.clear()
        input_win.move(0, 0)


def finalize():
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
