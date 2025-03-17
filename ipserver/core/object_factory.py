from abc import ABC

from ipserver.configs import Config
from ipserver.core.pipeline import Pipeline
from ipserver.service.args_builder import ArgsBuilder
from ipserver.service.dumpfile import DumpFile
from ipserver.service.forwarding_socket import ForwardingSocket
from ipserver.server.http_server import HTTPSocketServer, HTTPSSocketServer, HTTPHandler
from ipserver.server.socket_server import ConnBucket, TCPSocketServer, UDPSocketServer, SSLSocketServer
from ipserver.service.view_helper import ViewHelper
from ipserver.util.data_io import DataInput, DataOutput, InteractiveInput
from ipserver.util.requester import Requester
from ipserver.threads import ConnSockReceiver, ConnSockSender, ConnSockListener


class ObjectFactory(ABC):
    """

    """

    def get_config(self):
        """
        :rtype: Config
        """
        return Config

    def create_pipeline(self):
        """
        :rtype: Pipeline
        """
        return Pipeline()

    def create_args_builder(self, config, pipeline):
        """
        :param config:
        :type config: Config
        :param pipeline:
        :type pipeline: Pipeline
        :rtype: ArgsBuilder
        """

        return ArgsBuilder(config, pipeline)

    def create_data_input(self):
        return DataInput()

    def create_data_output(self):
        return DataOutput()

    def create_interactive_input(self):
        return InteractiveInput()

    def create_conn_bucket(self):
        return ConnBucket()

    def create_tcp_socket_server(self):
        return TCPSocketServer()

    def create_udp_socket_server(self):
        return UDPSocketServer()

    def create_ssl_socket_server(self, args):
        return SSLSocketServer(args)

    def create_http_socket_server(self, factory, pipeline, args):
        return HTTPSocketServer(factory, pipeline, args)

    def create_https_socket_server(self, factory, pipeline, args):
        return HTTPSSocketServer(factory, pipeline, args)

    def create_conn_sock_receiver(self, forwarding_socket, view):
        return ConnSockReceiver(forwarding_socket, view)

    def create_conn_sock_sender(self, forwarding_socket, view):
        return ConnSockSender(forwarding_socket, view)

    def create_conn_sock_listener(self, socket_server, conn_bucket, args, factory, pipeline, view):
        return ConnSockListener(socket_server, conn_bucket, args, factory, pipeline, view)

    def create_http_handler(self, conn_sock, port, pipeline, args, shared_object):
        return HTTPHandler(conn_sock, port, pipeline, args, shared_object)

    def create_forwarding_socket(self, args):
        return ForwardingSocket(args)

    def create_forwarding_requester(self):
        return Requester()

    def create_dumpfile(self, pipeline):
        return DumpFile(pipeline)

    def create_view_helper(self):
        return ViewHelper.get_instance()
