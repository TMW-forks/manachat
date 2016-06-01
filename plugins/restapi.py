import asyncore
import asynchat
import socket
import logging
import json
from collections import deque
from BaseHTTPServer import BaseHTTPRequestHandler

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import commands

__all__ = [ 'PLUGIN', 'init' ]

PLUGIN = {
    'name': 'restapi',
    'requires': (),
    'blocks': (),
    'default_config' : {
        'rest_ip': '127.0.0.1',
        'rest_port': '8971',
    }
}

last_id = 0
log_history = deque(maxlen=200)


def collect_messages(since_id):
    ss = []
    for m_id, m_text in log_history:
        if m_id >= since_id:
            ss.append({'id': m_id, 'message': m_text})

    return json.dumps(ss)


class RequestHandler(asynchat.async_chat, BaseHTTPRequestHandler):

    protocol_version = "HTTP/1.1"

    def __init__(self, conn, addr, server):
        asynchat.async_chat.__init__(self, conn)
        self.client_address = addr
        self.connection = conn
        self.server = server
        self.set_terminator('\r\n\r\n')
        self.rfile = StringIO()
        self.wfile = StringIO()
        self.found_terminator = self.handle_request_line

    def collect_incoming_data(self, data):
        """Collect the data arriving on the connexion"""
        self.rfile.write(data)

    def prepare_POST(self):
        """Prepare to read the request body"""
        bytesToRead = int(self.headers.getheader('Content-Length'))
        # set terminator to length (will read bytesToRead bytes)
        self.set_terminator(bytesToRead)
        self.rfile = StringIO()
        # control will be passed to a new found_terminator
        self.found_terminator = self.handle_post_data

    def handle_post_data(self):
        """Called when a POST request body has been read"""
        self.rfile.seek(0)
        self.do_POST()
        self.finish()

    def handle_request_line(self):
        """Called when the http request line and headers have been received"""
        self.rfile.seek(0)
        self.raw_requestline = self.rfile.readline()
        self.parse_request()

        if self.command == 'GET':
            self.do_GET()
            self.finish()
        elif self.command == 'POST':
            self.prepare_POST()
        else:
            self.send_error(501)

    def finish(self):
        data = self.wfile.getvalue()
        self.push(data)
        self.close_when_done()

    def do_GET(self):
        try:
            since_id = int(self.path[1:])
        except ValueError:
            self.send_error(400)
            return

        response = collect_messages(since_id)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        cmd = self.rfile.getvalue()
        commands.process_line(cmd)
        self.send_response(200)


class Server(asyncore.dispatcher):

    def __init__(self, ip, port, handler):
        asyncore.dispatcher.__init__(self)
        self.handler = handler
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((ip, port))
        self.listen(5)

    def handle_accept(self):
        try:
            conn, addr = self.accept()
        except:
            self.log_info('handle_accept() error', 'warning')
            return

        self.handler(conn, addr, self)


class RestDebugLogHandler(logging.Handler):
    def emit(self, record):
        global last_id
        msg = self.format(record)
        last_id += 1
        log_history.append((last_id, msg))


def init(config):
    debuglog = logging.getLogger("ManaChat.Debug")
    dbgh = RestDebugLogHandler()
    dbgh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s",
                                        datefmt="%H:%M:%S"))
    debuglog.addHandler(dbgh)

    ip = config.get(PLUGIN['name'], 'rest_ip')
    port = config.getint(PLUGIN['name'], 'rest_port')
    Server(ip, port, RequestHandler)
