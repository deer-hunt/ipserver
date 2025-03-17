import logging
import os
import queue
import socket
import ssl
from abc import ABC
from pathlib import Path

from logging import getLogger
from ipserver.configs import Constant
from ipserver.util.sys_util import AppException


class SocketServer(ABC):
    def __init__(self):
        self.conn_bucket = None
        self.hostname = None
        self.port = None
        self.bind_ip = None
        self.sock = None
        self.timeout = -1

    @staticmethod
    def get_error(e):
        error = None

        if isinstance(e, socket.timeout):
            error = 'Connection timeout.'
        elif isinstance(e, socket.gaierror):
            error = 'Connection error.'
        elif isinstance(e, PermissionError):
            error = 'Permission error. Please run as "root" user.'
        elif isinstance(e, socket.herror):
            error = 'Socket error.'
        elif isinstance(e, socket.error):
            if e.errno == 98:
                error = 'This port is already used.'

        return error

    def initialize(self, conn_bucket, timeout):
        self.conn_bucket = conn_bucket
        self.timeout = timeout

    def create(self, port, bind_ip=None):
        getLogger(__name__).info('Created socket.(port:{})'.format(port))

        self.port = port
        self.bind_ip = bind_ip

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((bind_ip, port))

    def listen(self, backlog=5):
        pass

    def accept(self, add_conn=True):
        pass

    def close(self):
        if self.sock:
            try:
                sock = self.sock
                self.sock = None
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except OSError as e:
                if e.errno != 107:  # Not Transport endpoint is not connected
                    raise e

    def __del__(self):
        self.close()


class ConnBucket:
    def __init__(self):
        self.conn_socks = []
        self.max_conn_id = 0

    def add_conn(self, conn_sock):
        conn_sock.set_conn_id(self.get_new_conn_id())

        self.conn_socks.append(conn_sock)

    def get_max_conn_sock(self):
        max_conn_sock = None

        for conn_sock in self.conn_socks:
            if max_conn_sock is None or conn_sock.conn_id > max_conn_sock.conn_id:
                max_conn_sock = conn_sock

        return max_conn_sock

    def get_new_conn_id(self):
        conn_id = self.max_conn_id + 1

        self.max_conn_id += 1

        return conn_id

    def get_conn(self, conn_id):
        return next((conn_sock for conn_sock in self.conn_socks if conn_sock.conn_id == conn_id), None)

    def get_conns(self):
        return self.conn_socks

    def refresh(self):
        self.conn_socks = [conn_sock for conn_sock in self.conn_socks if conn_sock.sock is not None]

    def verify_connections(self):
        conn_socks = []

        for conn_sock in self.conn_socks:
            if conn_sock.verify_connection():
                conn_socks.append(conn_sock)

        self.conn_socks = conn_socks

    def reset_id(self):
        max_conn_id = 0

        for conn_sock in self.conn_socks:
            if conn_sock.conn_id > max_conn_id:
                max_conn_id = conn_sock.conn_id

        self.max_conn_id = max_conn_id

    def refresh_connections(self):
        self.verify_connections()
        self.refresh()
        self.reset_id()


class SendQueue(queue.Queue):
    def send(self, binary):
        self.put(binary)

    def close(self):
        self.put(None)


class ConnSock(ABC):
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.conn_id = None
        self.queue = SendQueue()
        self.sequence = 0
        self.cur = 0

    def set_conn_id(self, conn_id):
        self.conn_id = conn_id

    def get_queue(self):
        return self.queue

    def send_queue(self, binary):
        self.queue.send(binary)

    def send(self, binary):
        self.add_sequence(Constant.DIRECTION_SEND)

    def complete_send(self, binary):
        pass

    def receive(self):
        self.add_sequence(Constant.DIRECTION_RECEIVE)

    def complete_receive(self, binary):
        pass

    def add_sequence(self, cur):
        if self.cur != cur:
            self.sequence += 1
            self.cur = cur

    def close(self):
        if self.sock:
            self.close_socket()

        if self.queue:
            self.queue.close()
            self.queue = None

    def close_socket(self):
        try:
            sock = self.sock
            self.sock = None
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except OSError as e:
            if e.errno != 9:  # Not Bad file descriptor
                raise e

    def is_connected(self, verify_data=False, binary=None):
        if verify_data and not binary:
            return False

        if self.sock:
            error = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

            if error == 0:
                return True

        return False

    def verify_connection(self, verify_data=False, binary=None):
        if not self.is_connected(verify_data, binary):
            self.close()
            return False

        return True

    def __del__(self):
        self.close()


class TCPSocketServer(SocketServer):
    def create(self, port, bind_ip=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        super().create(port, bind_ip)

    def listen(self, backlog=5):
        self.sock.listen(backlog)

    def accept(self, add_conn=True):
        sock, addr = self.sock.accept()
        sock.settimeout(self.timeout)

        conn_sock = TCPConnSock(sock, addr)

        if add_conn:
            self.conn_bucket.add_conn(conn_sock)

        return conn_sock


class TCPConnSock(ConnSock):
    def __init__(self, sock, addr):
        super().__init__(sock, addr)

    def send(self, binary):
        self.sock.sendall(binary)

        super().send(binary)

    def receive(self):
        binary = self.sock.recv(Constant.RECV_BUF_SIZE)

        super().receive()

        return binary


class UDPSocketServer(SocketServer):
    def create(self, port, bind_ip=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        super().create(port, bind_ip)

    def accept(self, add_conn=True):
        binary, addr = self.sock.recvfrom(0)

        conn_sock = UDPConnSock(None, addr)

        if add_conn:
            self.conn_bucket.add_conn(conn_sock)

        return conn_sock


class UDPConnSock(ConnSock):
    def listen(self, backlog=5):
        pass

    def send(self, binary):
        if self.addr:
            self.sock.sendto(binary, self.addr)
            super().send(binary)

    def receive(self):
        binary, addr = self.sock.recvfrom(Constant.RECV_BUF_SIZE)

        self.addr = addr
        super().receive()

        return binary


# https://docs.python.org/ja/3.13/library/ssl.html
class SSLSocketServer(SocketServer):
    def __init__(self, args):
        super().__init__()

        parent_path = Path(__file__).parent.parent.resolve()

        self.ssl_keypath = str(parent_path) + '/keys/' if not args.ssl_keypath else args.ssl_keypath
        self.ssl_certfile = 'certificate.pem' if not args.ssl_certfile else args.ssl_certfile
        self.ssl_keyfile = 'private.pem' if not args.ssl_keyfile else args.ssl_keyfile

        self.ssl_context = None

    def set_ssl_context(self, ssl_context):
        self.ssl_context = ssl_context

    def create(self, port, bind_ip=None):
        if not self.ssl_context:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        else:
            context = ssl.SSLContext(self.ssl_context)

        ssl_certfile = self.get_ssl_key_path(self.ssl_certfile)
        ssl_keyfile = self.get_ssl_key_path(self.ssl_keyfile)

        context.load_cert_chain(ssl_certfile, ssl_keyfile)

        context.set_alpn_protocols(['http/1.1'])

        self.sock = context.wrap_socket(socket.socket(socket.AF_INET), server_side=True)

        super().create(port, bind_ip)

    def get_ssl_key_path(self, filename):
        filepath = self.ssl_keypath + filename

        if not os.path.isfile(filepath):
            raise AppException('SSL key file does not exist.({})'.format(filepath))

        getLogger(__name__).info('SSL_KEY_FILE: ' + filepath)

        return filepath

    def listen(self, backlog=5):
        self.sock.listen(backlog)

    def accept(self, add_conn=True):
        conn_sock = None

        try:
            sock, addr = self.sock.accept()
            sock.settimeout(self.timeout)

            getLogger(__name__).info('SSL_VERSION: ' + sock.version())

            conn_sock = SSLConnSock(sock, addr)

            if add_conn:
                self.conn_bucket.add_conn(conn_sock)
        except ssl.SSLError:
            logger = getLogger(__name__)
            logger.info('SSL connection error.', exc_info=logger.isEnabledFor(logging.DEBUG))

        return conn_sock

    # https://gist.github.com/oborichkin/b935f2ccef7841459615e3a69e02db59
    def create_self_signed_cert(self):
        pass


class SSLConnSock(ConnSock):
    def send(self, binary):
        self.sock.sendall(binary)

        super().send(binary)

    def receive(self):
        binary = self.sock.recv(Constant.RECV_BUF_SIZE)

        super().receive()

        return binary


class SocketCloseError(socket.error):
    pass
