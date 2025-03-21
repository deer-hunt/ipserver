import ipaddress
import threading
import time

from ipserver.configs import Constant
from ipserver.core.pipeline import Pipeline
from ipserver.server.socket_server import SocketCloseError
from ipserver.service.dumpfile import DumpFile
from ipserver.service.view_helper import ViewHelper


class ConnSockListener(threading.Thread):
    def __init__(self, socket_server, conn_bucket, args, factory, pipeline, view):
        super().__init__()

        self.daemon = True

        self.socket_server = socket_server
        self.conn_bucket = conn_bucket
        self.args = args
        self.factory = factory
        self.pipeline = pipeline  # type: Pipeline

        self.view = view  # type: ViewHelper
        self.dumpfile = None

    def _initialize(self):
        if self.args.dumpfile:
            self.dumpfile = self.factory.create_dumpfile(self.pipeline)
            self.dumpfile.initialize(Constant.DUMPFILE_DIR)

    def run(self):
        conn_sock = None

        try:
            self._initialize()

            self.pipeline.start_listen(self.socket_server, self.conn_bucket)

            while (True):
                if self.args.connection_max > 0:
                    self._wait_connectable()

                conn_sock = self.socket_server.accept()

                if not conn_sock:
                    continue

                if not self._verify_restriction(conn_sock):
                    self._deny_socket(conn_sock)

                    continue

                self.pipeline.post_accept(conn_sock, self.conn_bucket)
                self.view.accepted(conn_sock)

                forwarding_socket = None

                if self.args.forwarding:
                    forwarding_socket = self._initialize_forwarding(conn_sock)
                elif self.args.http_opt == Constant.HTTP_INTERACTIVE:
                    self.view.output_message('Running in interactive behavior. You must send server\'s response manually.\n', conn_sock, warn=False)

                conn_sock_receiver = self.factory.create_conn_sock_receiver(forwarding_socket, self.view)
                conn_sock_receiver.initialize(self.conn_bucket, conn_sock, self.pipeline, self.dumpfile)

                conn_sock_sender = self.factory.create_conn_sock_sender(forwarding_socket, self.view)
                conn_sock_sender.initialize(self.conn_bucket, conn_sock, self.pipeline, self.dumpfile)

                conn_sock_receiver.start()
                conn_sock_sender.start()

                conn_sock = None
        except Exception as e:
            self.socket_server.close()

            prefix = self.view.create_message('', conn_sock) if conn_sock else ''

            self.view.output_error(e, prefix=prefix)

    def _wait_connectable(self):
        while self.conn_bucket.get_conn_length() >= self.args.connection_max:
            self.conn_bucket.refresh_connections(False)
            time.sleep(0.2)

    def _initialize_forwarding(self, conn_sock):
        forwarding_socket = None

        if self.args.mode not in Constant.HTTP_MODES:
            forwarding_socket = self.factory.create_forwarding_socket(self.args)
            forwarding_socket.initialize()
            self.view.output_message('Running in forwarding behavior. Destination: {}:{}\n'.format(forwarding_socket.hostname, forwarding_socket.port), conn_sock, warn=False)
        else:
            forwarding_requester = self.factory.create_forwarding_requester()
            conn_sock.handler.set_forwarding_requester(forwarding_requester)

        return forwarding_socket

    def _verify_restriction(self, conn_sock):
        allow = True

        client_ip = conn_sock.addr[0]
        ip = ipaddress.ip_address(client_ip)

        restrict_allow = self.args.fixed_restrict_allow

        if len(restrict_allow) > 0 and not self._ip_in_range(ip, restrict_allow):
            allow = False

        restrict_deny = self.args.fixed_restrict_deny

        if len(restrict_deny) > 0 and self._ip_in_range(ip, restrict_deny):
            allow = False

        return allow

    def _ip_in_range(self, ip, ip_networks):
        for ip_network in ip_networks:
            if ip in ip_network:
                return True

        return False

    def _deny_socket(self, conn_sock):
        conn_sock.close()

        self.pipeline.deny_socket(conn_sock)

        self.view.output_logging('Deny {} by restriction.'.format(conn_sock.addr[0]))


class ConnSockReceiver(threading.Thread):
    def __init__(self, forwarding_socket, view):
        super().__init__()

        self.conn_bucket = None
        self.conn_sock = None
        self.forwarding_socket = forwarding_socket
        self.view = view
        self.dumpfile = None

    def initialize(self, conn_bucket, conn_sock, pipeline, dumpfile):
        self.conn_bucket = conn_bucket
        self.conn_sock = conn_sock
        self.pipeline = pipeline
        self.dumpfile = dumpfile  # type: DumpFile

    def run(self):
        try:
            while (True):
                binary = self.conn_sock.receive()

                if binary:
                    binary = self.pipeline.post_receive(self.conn_sock, binary)

                    if self.dumpfile:
                        self.dumpfile.write(self.conn_sock, 'recv', binary)

                    self.view.receive(binary, self.conn_sock)

                    send_binary = self.conn_sock.complete_receive(binary)

                    send_binary = self.pipeline.complete_receive(self.conn_sock, binary, send_binary)

                    if send_binary is not None:
                        self.conn_sock.queue.send(send_binary)

                if self.forwarding_socket:
                    binary = self.pipeline.pre_forwarding_send(self.conn_sock, binary)
                    self.forwarding_socket.send(binary)

                    self.view.forwarding_send(binary, self.forwarding_socket, self.conn_sock)

                self.conn_bucket.refresh()

                if not self.conn_sock.is_connected(True, binary):
                    raise SocketCloseError()
        except Exception as e:
            self._close(e)

    def _close(self, e):
        if self.conn_sock.sock:
            if self.forwarding_socket:
                self.forwarding_socket.close()

            self.conn_sock.close()
            self.pipeline.closed_socket(self.conn_sock)

            self.conn_bucket.refresh()

            self.view.closed_socket(self.conn_sock)

            if not isinstance(e, SocketCloseError):
                self.view.output_error(e, prefix='[{}] '.format(self.conn_sock.conn_id))


class ConnSockSender(threading.Thread):
    def __init__(self, forwarding_socket, view):
        super().__init__()

        self.conn_bucket = None
        self.conn_sock = None
        self.forwarding_socket = forwarding_socket
        self.view = view
        self.dumpfile = None

    def initialize(self, conn_bucket, conn_sock, pipeline, dumpfile):
        self.conn_bucket = conn_bucket
        self.conn_sock = conn_sock
        self.pipeline = pipeline
        self.dumpfile = dumpfile

    def run(self):
        try:
            while (True):
                queue = self.conn_sock.get_queue()

                if self.forwarding_socket:
                    binary = self.forwarding_socket.receive(Constant.RECV_BUF_SIZE)
                    binary = self.pipeline.post_forwarding_receive(self.conn_sock, binary)

                    self.view.forwarding_receive(binary, self.forwarding_socket, self.conn_sock)

                    queue.send(binary)

                binary = self._reduce_queues(queue)

                self.conn_bucket.refresh()

                if not self.conn_sock.is_connected(True, binary):
                    raise SocketCloseError()
        except Exception as e:
            self._close(e)

    def _reduce_queues(self, queue):
        binary = self._reduce_queue(queue, True)

        for i in range(queue.qsize()):
            binary = self._reduce_queue(queue, False)

        return binary

    def _reduce_queue(self, queue, blocking):
        binary = queue.get(blocking)

        if binary:
            binary = self.pipeline.pre_send(self.conn_sock, binary)

            self.conn_sock.send(binary)

            binary = self.pipeline.post_send(self.conn_sock, binary)

            if self.dumpfile:
                self.dumpfile.write(self.conn_sock, 'send', binary)

            self.view.send(binary, self.conn_sock)

            self.conn_sock.complete_send(binary)

            self.pipeline.complete_send(self.conn_sock, binary)

        return binary

    def _close(self, e):
        if self.conn_sock.sock:
            if self.forwarding_socket:
                self.forwarding_socket.close()

            self.conn_sock.close()
            self.pipeline.closed_socket(self.conn_sock)

            self.conn_bucket.refresh()

            self.view.closed_socket(self.conn_sock)

            if not isinstance(e, SocketCloseError):
                self.view.output_error(e, prefix='[{}] '.format(self.conn_sock.conn_id))
