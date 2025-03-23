from abc import ABC

from ipserver.configs import Config, Constant
from ipserver.server.socket_server import SocketServer, ConnBucket, ConnSock
from ipserver.server.http_server import HttpIo
from http.client import HTTPMessage


class Pipeline(ABC):
    """

    """

    def __init__(self):
        self.config = None  # type: Config

    def init_configure(self, arguments, conf_ags):
        """
        :param arguments:
        :type arguments: dict
        :param conf_ags:
        :type arguments: dict
        """
        pass

    def pre_configure(self, args):
        """
        :param args:
        :type args: argparse.Namespace
        """
        pass

    def post_configure(self, args):
        """
        :param args:
        :type args: argparse.Namespace
        """
        pass

    def initialize(self, config, socket_server):
        """
        :param config:
        :type config: Config
        :param socket_server:
        :type socket_server: SocketServer
        """

        self.config = config

    def create_socket(self, socket_server):
        """
        :param socket_server:
        :type socket_server: SocketServer
        """
        pass

    def connected(self, socket):
        """
        :param socket:
        :type socket: socket
        """
        pass

    def interactive_input(self, action, line, conn_sock, conn_bucket):
        """
        :param action:
        :type action: str
        :param line:
        :type line: str
        :param conn_sock:
        :type conn_sock: ConnSock
        :param conn_bucket:
        :type conn_bucket: ConnBucket
        """
        pass

    def kick_quiet_interval(self, conn_bucket):
        """
        :param conn_bucket:
        :type conn_bucket: ConnBucket
        """
        pass

    def start_listen(self, socket_server, conn_bucket):
        """
        :param socket_server:
        :type socket_server: SocketServer
        :param conn_bucket:
        :type conn_bucket: ConnBucket
        """
        pass

    def verify_restriction(self, conn_sock, allow):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param allow:
        :type allow: bool
        """
        return allow

    def deny_socket(self, conn_sock):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        """
        pass

    def post_accept(self, conn_sock, conn_bucket):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param conn_bucket:
        :type conn_bucket: ConnBucket
        """
        pass

    def post_receive(self, conn_sock, binary):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param binary:
        :type binary: bytes
        """
        return binary

    def complete_receive(self, conn_sock, receive_binary, send_binary=None):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param receive_binary:
        :type receive_binary: bytes
        :param send_binary:
        :type send_binary: bytes
        """
        return send_binary

    def pre_send(self, conn_sock, binary):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param binary:
        :type binary: bytes
        """
        return binary

    def post_send(self, conn_sock, binary):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param binary:
        :type binary: bytes
        """
        return binary

    def complete_send(self, conn_sock, binary):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param binary:
        :type binary: bytes
        """
        pass

    def pre_forwarding_send(self, conn_sock, binary):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param binary:
        :type binary: bytes
        """
        return binary

    def post_forwarding_receive(self, conn_sock, binary):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param binary:
        :type binary: bytes
        """
        return binary

    def closed_socket_server(self, socket_server):
        """
        :param socket_server:
        :type socket_server: SocketServer
        """
        pass

    def closed_socket(self, conn_sock):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        """
        pass

    def pre_http_process(self, http_opt, path, httpio):
        """
        :param http_opt:
        :type http_opt: str
        :param path:
        :type path: str
        :param httpio:
        :type httpio: HttpIo
        """
        return http_opt

    def digest_auth_load(self, users):
        """
        :param users:
        :type users: dict
        """
        pass

    def digest_auth_veirfy(self, httpio, username, auth_data, users):
        """
        :param httpio:
        :type httpio: HttpIo
        :param username:
        :type username: str
        :param auth_data:
        :type auth_data: dict
        :param users:
        :type users: dict
        """
        return False

    def get_http_app_path(self, httpio, root_path, request_path, translate_path):
        """
        :param httpio:
        :type httpio: HttpIo
        :param root_path:
        :type usernroot_pathame: str
        :param request_path:
        :type request_path: str
        :param translate_path:
        :type translate_path: str
        """
        return None

    def is_enable_file_upload(self, httpio, request_path):
        """
        :param httpio:
        :type httpio: HttpIo
        :param request_path:
        :type request_path: str
        """
        return True

    def pre_http_forwarding_request(self, httpio, forwarding_url, req_headers):
        """
        :param httpio:
        :type httpio: HttpIo
        :param forwarding_url:
        :type forwarding_url: str
        :param req_headers:
        :type req_headers: HTTPMessage
        """
        return forwarding_url

    def post_http_forwarding_request(self, httpio, forwarding_url, req_headers, res_headers, response, binary):
        """
        :param httpio:
        :type httpio: HttpIo
        :param forwarding_url:
        :type forwarding_url: str
        :param req_headers:
        :type req_headers: HTTPMessage
        :param res_headers:
        :type res_headers: HTTPMessage
        :param binary:
        :type binary: bytes
        """
        return binary

    def pre_http_file_upload(self, httpio, mpart):
        """
        :param httpio:
        :type httpio: HttpIo
        """
        return True

    def post_http_file_upload(self, httpio, mpart):
        """
        :param httpio:
        :type httpio: HttpIo
        """
        pass

    def pre_http_respond(self, httpio):
        """
        :param httpio:
        :type httpio: HttpIo
        """
        pass

    def get_filename(self, conn_sock, direction, filename):
        """
        :param conn_sock:
        :type conn_sock: ConnSock
        :param direction:
        :type direction: int
        :param filename:
        :type filename: str
        """
        return filename

    def pre_dump_write(self, file, binary, filename, conn_sock, direction):
        """
        :param file:
        :type file: File
        :param binary:
        :type binary: bytes
        :param filename:
        :type filename: str
        :param conn_sock:
        :type conn_sock: ConnSock
        :param direction:
        :type direction: int
        """
        pass

    def complete(self):
        pass
