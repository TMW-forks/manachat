import loginsrv


def login(host, port, username, password, charname):
    loginsrv.connect(host, port)

    loginsrv.server.username = username
    loginsrv.server.password = password
    loginsrv.server.char_name = charname

    loginsrv.cmsg_server_version_request()
