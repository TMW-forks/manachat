
from construct import *
from construct.protocols.layer3.ipv4 import IpAddress
from protocol import *
from dispatcher import dispatch
from utils import *
from charserv import cmsg_char_server_connect

loginsrv = None
username = 'john_doe'
password = '123456'
server_addr = 'server.themanaworld.org'
server_port = 6902


def smsg_server_version(data):
    print "SMSG_SERVER_VERSION {}.{}".format(data.hi, data.lo)

    packet_def = Struct("packet",
                        ULInt16("opcode"),
                        ULInt32("clientversion"),
                        StringZ("username", 24),
                        StringZ("password", 24),
                        Byte("flags"))

    class packet:
        opcode = CMSG_LOGIN_REGISTER
        clientversion = 3
        username = username
        password = password
        flags = 3

    packet_def.build_stream(packet, loginsrv)
    dispatch(loginsrv, login_packets)

def smsg_update_host(data):
    print "SMSG_UPDATE_HOST {}".format(data.host)
    dispatch(loginsrv, login_packets)

def smsg_login_data(data):
    print "SMSG_LOGIN_DATA", data
    loginsrv.close()
    cmsg_char_server_connect(data)

def smsg_login_error(data):

    error_codes = {
        0: "Unregistered ID",
        1: "Wrong password",
        2: "Account expired",
        3: "Rejected from server",
        4: "Permban",
        5: "Client too old",
        6: "Temporary ban until {}".format(data.date),
        7: "Server overpopulated",
        9: "Username already taken",
        10: "Wrong name",
        11: "Incurrect email",
        99: "Username permanently erased" }

    print "SMSG_LOGIN_ERROR {}".format(error_codes.get(data.code, "Unknown error"))
    loginsrv.close()

login_packets = {
    0x7531 : (smsg_server_version,
              Struct("data",
                     ULInt32("hi"),
                     ULInt32("lo"))),
    0x0063 : (smsg_update_host,
              Struct("data",
                     ULInt16("length"),
                     StringZ("host",
                            lambda ctx: ctx.length - 4))),
    0x0069 : (smsg_login_data,
              Struct("data",
                     ULInt16("length"),
                     ULInt32("session1"),
                     ULInt32("account"),
                     ULInt32("session2"),
                     IpAddress("oldip"),
                     StringZ("lastlogin", 24),
                     Padding(2),
                     Enum(Byte("gender"),
                          BOY = 1,
                          GIRL = 0),
                     Array(lambda ctx: (ctx.length - 47) / 32,
                           Struct("worlds",
                                  IpAddress("address"),
                                  ULInt16("port"),
                                  StringZ("name", 20),
                                  ULInt16("onlineusers"),
                                  Padding(4))))),

    0x006a : (smsg_login_error,
              Struct("data",
                     Byte("code"),
                     StringZ("date", 20)))
}

def cmsg_server_version_request(host, port):
    global loginsrv
    loginsrv = SocketWrapper()
    loginsrv.connect((host, port))
    ULInt16("opcode").build_stream(0x7530, loginsrv)
    dispatch(loginsrv, login_packets)

if __name__ == "__main__":
    host, port = 'server.themanaworld.org', 6902
    cmsg_server_version_request(host, port)
