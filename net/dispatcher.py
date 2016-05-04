from construct import Struct, ULInt16, MetaField
from loggers import netlog
from packetlen import packet_lengths


def dispatch(stream, protodef):
    opcode = ULInt16("opcode").parse_stream(stream)

    if opcode in protodef:
        func, macro = protodef[opcode]
        data = macro.parse_stream(stream)
        func(data)
    else:
        data = ''
        pktlen = packet_lengths.get(opcode, -1)

        if pktlen > 0:
            data = stream.read(pktlen - 2)
        elif pktlen == -1:
            datadef = Struct("data",
                             ULInt16("length"),
                             MetaField("ignore",
                                       lambda ctx: ctx["length"] - 4))
            data = datadef.parse_stream(stream)

        netlog.warning('UNIMPLEMENTED opcode={:04x} data={}'.format(
            opcode, data))
