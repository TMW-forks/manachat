#!/usr/bin/python

"""
Generate a dict of packet lenghts, based on packetsin.inc from ManaPlus.
Author: Joseph Botosh <rumly111@gmail.com>
Licence: GPLv2.
"""

import os
import sys


def GeneratePacketLengths(infile):
    plength = {}
    with open(infile) as f:
        for l in f:
            if l.startswith('packet('):
                w = l[7:-2].split(',')
                opcode = int(w[1].strip(), 16)
                length = int(w[2].strip())
                plength[opcode] = length
    return plength


def PrettyPrint(plengths, width=80):
    s = 'packet_lengths = {\n    '
    curr_line_len = 4
    for opcode in sorted(plengths.keys()):
        r = '0x{:04x}: {:d},'.format(opcode, plengths[opcode]).ljust(12)
        if curr_line_len + len(r) > width:
            curr_line_len = 4
            s += '\n    '
        s += r
        curr_line_len += len(r)
    s += '}\n'
    return s


def PrintHelp():
    print('Usage: {} /path/to/packetsin.inc'.format(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        PrintHelp()
        sys.exit(0)
    filename = sys.argv[1]
    if os.path.isfile(filename):
        pl = GeneratePacketLengths(filename)
        print(PrettyPrint(pl))
        # print('packet_lengths = ',
        #       GeneratePacketLengths(filename))
    else:
        print('File not found:', filename, file=sys.stderr)
        sys.exit(1)
