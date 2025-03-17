from abc import ABC

from ipserver.configs import Config, Constant


class Pipeline(ABC):
    """

    """

    def __init__(self):
        self.config = None  # type: Config

    def init_configure(self, arguments, conf_ags):
        """
        :param arguments:
        :type arguments: dict
        """
        pass

    def pre_configure(self, args, conf_args):
        """
        :param args:
        :type args: argparse.Namespace
        :param conf_args:
        :type conf_args: dict
        """
        pass

    def post_configure(self, args, conf_args):
        """
        :param args:
        :type args: argparse.Namespace
        :param conf_args:
        :type conf_args: dict
        """
        pass

    def initialize(self, config, socket_server):
        """
        :param config:
        :type config: Config
        """

        self.config = config

    def create_socket(self, socket_server):
        pass

    def connected(self, socket):
        pass

    def interactive_input(self, action, line, conn_sock, conn_bucket):
        pass

    def kick_quiet(self):
        pass

    def start_listen(self, socket_server, conn_bucket):
        pass

    def post_accept(self, conn_sock, conn_bucket):
        pass

    def post_receive(self, conn_sock, binary):
        return binary

    def complete_receive(self, conn_sock, binary):
        return binary

    def pre_send(self, conn_sock, binary):
        return binary

    def post_send(self, conn_sock, binary):
        return binary

    def complete_send(self, conn_sock, binary):
        return binary

    def pre_forwarding_send(self, conn_sock, binary):
        return binary

    def post_forwarding_receive(self, conn_sock, binary):
        return binary

    def deny_socket(self, conn_sock):
        pass

    def closed_socket(self, conn_sock):
        pass

    def digest_auth_load(self, users):
        pass

    def digest_auth_veirfy(self, httpio, username, auth_data, users):
        return False

    def pre_http_process(self, http_opt, path, httpio):
        return http_opt

    def get_http_app_path(self, httpio, root_path, request_path, translate_path):
        return None

    def is_enable_file_upload(self, httpio, request_path):
        return True

    def pre_http_forwarding_request(self, httpio, forwarding_url, req_headers):
        return forwarding_url

    def post_http_forwarding_request(self, httpio, forwarding_url, req_headers, res_headers, response, binary):
        return binary

    def pre_http_file_upload(self, httpio, mpart):
        return True

    def post_http_file_upload(self, httpio, mpart):
        pass

    def pre_http_respond(self, httpio):
        pass

    def complete(self):
        pass

    def get_filename(self, conn_sock, direction, filename):
        return filename

    def pre_writefile(self, dest, port, binary, file):
        pass

    def post_writefile(self, dest, port, binary, file):
        pass
